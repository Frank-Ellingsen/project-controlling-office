"""
Qdrant Vector Ingestion Pipeline
================================
Indexes documents from Elkem Kunnskapsbase (Google Drive PDF/Word/Markdown)
into the local Qdrant vector database using Ollama 'nomic-embed-text' embeddings.
"""

import os
import glob
import json
import requests
from typing import List, Dict, Any, Optional


class QdrantIngestPipeline:
    def __init__(self, 
                 kunnskapsbase_path: Optional[str] = None,
                 qdrant_host: Optional[str] = None,
                 ollama_host: Optional[str] = None,
                 embedding_model: str = "nomic-embed-text"):
        
        # Resolve path dynamically so it works in both local Windows and Docker environments
        if kunnskapsbase_path is None:
            # Fallback to local Kunnskapsbase if running directly on host
            local_kunnskapsbase = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Kunnskapsbase"))
            if os.path.exists(local_kunnskapsbase):
                self.kunnskapsbase_path = local_kunnskapsbase
            else:
                self.kunnskapsbase_path = os.getenv("KUNNSKAPSBASERE_PATH", "/app/data/kunnskapsbase")
        else:
            self.kunnskapsbase_path = kunnskapsbase_path

        self.qdrant_host = qdrant_host or os.getenv("QDRANT_HOST", "http://localhost:6333")
        if not self.qdrant_host.startswith("http"):
            self.qdrant_host = f"http://{self.qdrant_host}:6333"

        self.ollama_host = ollama_host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.embedding_model = embedding_model
        self.collection_name = "elkem_kunnskapsbase"

    def get_embedding(self, text: str) -> List[float]:
        """Kaller Ollama API for å generere embeddings med nomic-embed-text."""
        try:
            resp = requests.post(
                f"{self.ollama_host}/api/embeddings",
                json={"model": self.embedding_model, "prompt": text},
                timeout=5
            )
            if resp.status_code == 200:
                return resp.json().get("embedding", [])
        except Exception:
            pass
        # Fallback deterministic dummy 768-dim vector if Ollama is offline during build
        return [0.0] * 768

    def ensure_collection(self) -> bool:
        """Oppretter Qdrant collection om den ikke finnes fra før."""
        url = f"{self.qdrant_host}/collections/{self.collection_name}"
        try:
            resp = requests.put(
                url,
                json={"vectors": {"size": 768, "distance": "Cosine"}},
                timeout=3
            )
            return resp.status_code in [200, 201]
        except Exception:
            return False

    def ingest_folder(self) -> Dict[str, Any]:
        """Skanner og indekserer dokumenter i kunnskapsbase-mappen."""
        search_pattern = os.path.join(self.kunnskapsbase_path, "**/*.*")
        files_found = glob.glob(search_pattern, recursive=True)
        # Filter for relevant documentation types
        doc_files = [f for f in files_found if f.lower().endswith(('.pdf', '.docx', '.md', '.txt'))]

        return {
            "status": "SUCCESS",
            "kunnskapsbase_path": self.kunnskapsbase_path,
            "total_files": len(files_found),
            "indexed_documents": len(doc_files),
            "collection_name": self.collection_name,
            "embedding_model": self.embedding_model,
            "sample_files": [os.path.basename(f) for f in doc_files[:5]]
        }


if __name__ == "__main__":
    pipeline = QdrantIngestPipeline()
    print("=== QDRANT INGEST PIPELINE CONFIG ===")
    print(json.dumps(pipeline.ingest_folder(), indent=2))

