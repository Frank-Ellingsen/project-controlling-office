"""
Bounded document ingestion into the local Qdrant collection.

Supported inputs are PDF, DOCX, Markdown, and plain-text files. Text is
embedded by the configured Ollama model and only successfully embedded points
are reported as indexed.
"""

import io
import json
import math
import os
import uuid
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from docx import Document
from pypdf import PdfReader


class QdrantIngestPipeline:
    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".md", ".txt"}
    COLLECTION_NAME = "elkem_kunnskapsbase"

    def __init__(
        self,
        kunnskapsbase_path: Optional[str] = None,
        qdrant_host: Optional[str] = None,
        ollama_host: Optional[str] = None,
        embedding_model: str = "nomic-embed-text",
        *,
        request_timeout: float = 20.0,
        max_file_bytes: int = 10 * 1024 * 1024,
        max_uncompressed_docx_bytes: int = 50 * 1024 * 1024,
        max_documents: int = 100,
        max_scanned_files: int = 5000,
        max_pages_per_pdf: int = 200,
        max_text_chars_per_document: int = 1_000_000,
        chunk_size: int = 1200,
        chunk_overlap: int = 150,
        max_total_chunks: int = 1000,
    ):
        if kunnskapsbase_path is None:
            local_path = Path(__file__).resolve().parents[2] / "Kunnskapsbase"
            self.kunnskapsbase_path = str(
                local_path if local_path.exists() else os.getenv(
                    "KUNNSKAPSBASERE_PATH", "/app/data/kunnskapsbase"
                )
            )
        else:
            self.kunnskapsbase_path = str(kunnskapsbase_path)

        self.qdrant_host = qdrant_host or os.getenv("QDRANT_HOST", "http://localhost:6333")
        if not self.qdrant_host.startswith(("http://", "https://")):
            self.qdrant_host = f"http://{self.qdrant_host}:6333"
        self.ollama_host = ollama_host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.embedding_model = embedding_model
        self.collection_name = self.COLLECTION_NAME
        self.request_timeout = request_timeout
        self.max_file_bytes = max_file_bytes
        self.max_uncompressed_docx_bytes = max_uncompressed_docx_bytes
        self.max_documents = max_documents
        self.max_scanned_files = max_scanned_files
        self.max_pages_per_pdf = max_pages_per_pdf
        self.max_text_chars_per_document = max_text_chars_per_document
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_total_chunks = max_total_chunks
        if chunk_size <= 0 or chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("chunk_size must be positive and chunk_overlap smaller than chunk_size")

    def get_embedding(self, text: str) -> List[float]:
        """Return a real Ollama embedding, failing explicitly if it is unavailable."""
        try:
            response = requests.post(
                f"{self.ollama_host}/api/embeddings",
                json={"model": self.embedding_model, "prompt": text},
                timeout=self.request_timeout,
            )
            response.raise_for_status()
            payload = response.json()
            embedding = payload.get("embedding") if isinstance(payload, dict) else None
            if not isinstance(embedding, list) or not embedding:
                raise ValueError("Ollama returned no embedding")
            vector = [float(value) for value in embedding]
            if any(not math.isfinite(value) for value in vector):
                raise ValueError("Ollama returned a non-finite embedding value")
            return vector
        except (requests.RequestException, ValueError, TypeError, KeyError) as exc:
            raise RuntimeError(f"Embedding request failed: {exc}") from exc

    def ensure_collection(self, vector_size: int) -> None:
        """Create the collection when absent and reject incompatible collections."""
        url = f"{self.qdrant_host}/collections/{self.collection_name}"
        try:
            response = requests.get(url, timeout=self.request_timeout)
            if response.status_code == 200:
                result = response.json().get("result", {})
                vectors = result.get("config", {}).get("params", {}).get("vectors", {})
                existing_size = vectors.get("size") if isinstance(vectors, dict) else None
                if existing_size is not None and existing_size != vector_size:
                    raise RuntimeError(
                        f"Qdrant collection vector size is {existing_size}; "
                        f"received embeddings of size {vector_size}"
                    )
                return
            if response.status_code != 404:
                response.raise_for_status()
                raise RuntimeError(f"Unexpected Qdrant response: {response.status_code}")

            response = requests.put(
                url,
                json={"vectors": {"size": vector_size, "distance": "Cosine"}},
                timeout=self.request_timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"Qdrant collection setup failed: {exc}") from exc

    def _extract_text(self, path: Path, data: bytes) -> str:
        suffix = path.suffix.lower()
        if suffix in {".txt", ".md"}:
            text = data.decode("utf-8-sig")
        elif suffix == ".docx":
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                expanded_size = sum(member.file_size for member in archive.infolist())
            if expanded_size > self.max_uncompressed_docx_bytes:
                raise ValueError(
                    "DOCX expanded size "
                    f"{expanded_size} exceeds {self.max_uncompressed_docx_bytes} byte limit"
                )
            document = Document(io.BytesIO(data))
            sections = [paragraph.text for paragraph in document.paragraphs]
            sections.extend(
                " ".join(cell.text for cell in row.cells)
                for table in document.tables
                for row in table.rows
            )
            text = "\n".join(sections)
        elif suffix == ".pdf":
            reader = PdfReader(io.BytesIO(data), strict=False)
            if len(reader.pages) > self.max_pages_per_pdf:
                raise ValueError(
                    f"PDF has {len(reader.pages)} pages; limit is {self.max_pages_per_pdf}"
                )
            page_texts = []
            total_chars = 0
            for page in reader.pages:
                page_text = page.extract_text() or ""
                total_chars += len(page_text)
                if total_chars > self.max_text_chars_per_document:
                    raise ValueError(
                        "Extracted text exceeds "
                        f"{self.max_text_chars_per_document} character limit"
                    )
                page_texts.append(page_text)
            text = "\n".join(page_texts)
        else:
            raise ValueError(f"Unsupported document type: {suffix}")

        text = text.strip()
        if not text:
            raise ValueError("No extractable text found")
        if len(text) > self.max_text_chars_per_document:
            raise ValueError(
                f"Extracted text exceeds {self.max_text_chars_per_document} character limit"
            )
        return text

    def _chunks(self, text: str) -> List[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end == len(text):
                break
            start = end - self.chunk_overlap
        return chunks

    def _discover_documents(self) -> tuple[List[Path], int, List[Dict[str, str]]]:
        root = Path(self.kunnskapsbase_path)
        if not root.is_dir():
            return [], 0, [{"file": str(root), "error": "Document directory does not exist"}]

        documents: List[Path] = []
        scanned_files = 0
        failures: List[Dict[str, str]] = []
        limit_reached = False
        for directory, dirs, filenames in os.walk(root, followlinks=False):
            dirs[:] = sorted(
                name for name in dirs
                if not (Path(directory) / name).is_symlink()
            )
            for filename in sorted(filenames):
                scanned_files += 1
                path = Path(directory) / filename
                if path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                    if len(documents) == self.max_documents:
                        failures.append({
                            "file": path.relative_to(root).as_posix(),
                            "error": f"Document limit ({self.max_documents}) reached",
                        })
                        limit_reached = True
                        break
                    documents.append(path)
                if scanned_files >= self.max_scanned_files:
                    failures.append({
                        "file": "",
                        "error": f"File scan limit ({self.max_scanned_files}) reached",
                    })
                    limit_reached = True
                    break
            if limit_reached:
                break
        return documents, scanned_files, failures

    def _upsert(self, points: List[Dict[str, Any]]) -> None:
        try:
            response = requests.put(
                f"{self.qdrant_host}/collections/{self.collection_name}/points?wait=true",
                json={"points": points},
                timeout=self.request_timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"Qdrant point upsert failed: {exc}") from exc

    def ingest_folder(self) -> Dict[str, Any]:
        """Extract, embed, and upsert bounded local documents into Qdrant."""
        documents, total_files, failures = self._discover_documents()
        discovered_documents = len(documents) + sum(
            failure.get("error", "").startswith("Document limit")
            for failure in failures
        )
        indexed_documents = 0
        indexed_chunks = 0
        vector_size: Optional[int] = None

        if not documents:
            if not failures:
                failures.append({"file": "", "error": "No supported documents found"})
            return self._result(total_files, 0, 0, discovered_documents, failures)

        for document_index, path in enumerate(documents):
            relative_path = path.relative_to(Path(self.kunnskapsbase_path)).as_posix()
            try:
                size = path.stat().st_size
                if size > self.max_file_bytes:
                    raise ValueError(f"File size {size} exceeds {self.max_file_bytes} byte limit")
                text = self._extract_text(path, path.read_bytes())
                chunks = self._chunks(text)
                if indexed_chunks + len(chunks) > self.max_total_chunks:
                    raise ValueError(f"Total chunk limit ({self.max_total_chunks}) reached")

                points = []
                for index, chunk in enumerate(chunks):
                    vector = self.get_embedding(chunk)
                    if vector_size is None:
                        vector_size = len(vector)
                        self.ensure_collection(vector_size)
                    elif len(vector) != vector_size:
                        raise RuntimeError("Embedding model returned inconsistent vector dimensions")
                    point_id = str(uuid.uuid5(
                        uuid.NAMESPACE_URL, f"{relative_path}:{index}"
                    ))
                    points.append({
                        "id": point_id,
                        "vector": vector,
                        "payload": {
                            "source": relative_path,
                            "chunk_index": index,
                            "text": chunk,
                        },
                    })

                for offset in range(0, len(points), 64):
                    self._upsert(points[offset:offset + 64])
                    indexed_chunks += len(points[offset:offset + 64])
                indexed_documents += 1
            except Exception as exc:
                failures.append({"file": relative_path, "error": str(exc)})
                # A collection or service error is unlikely to be fixed by retrying
                # every remaining document during the same bounded request.
                if isinstance(exc, RuntimeError):
                    for pending_path in documents[document_index + 1:]:
                        failures.append({
                            "file": pending_path.relative_to(
                                Path(self.kunnskapsbase_path)
                            ).as_posix(),
                            "error": "Not processed after an earlier service failure",
                        })
                    break

        return self._result(
            total_files, discovered_documents, indexed_documents, indexed_chunks, failures
        )

    def _result(
        self,
        total_files: int,
        discovered_documents: int,
        indexed_documents: int,
        indexed_chunks: int,
        failures: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        status = "SUCCESS" if indexed_documents > 0 and not failures else (
            "PARTIAL_FAILURE"
            if indexed_documents > 0 or indexed_chunks > 0
            else "FAILED"
        )
        return {
            "status": status,
            "kunnskapsbase_path": self.kunnskapsbase_path,
            "total_files": total_files,
            "discovered_documents": discovered_documents,
            "indexed_documents": indexed_documents,
            "indexed_chunks": indexed_chunks,
            "collection_name": self.collection_name,
            "embedding_model": self.embedding_model,
            "failures": failures,
        }


if __name__ == "__main__":
    print(json.dumps(QdrantIngestPipeline().ingest_folder(), indent=2))
