"""Tests for bounded document extraction, Ollama embeddings, and Qdrant upserts."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import requests
from docx import Document

from src.engine_agents.ingest_kunnskapsbase import QdrantIngestPipeline


def response(status_code=200, payload=None):
    result = MagicMock()
    result.status_code = status_code
    result.json.return_value = payload or {}
    result.raise_for_status.side_effect = (
        requests.HTTPError(f"HTTP {status_code}") if status_code >= 400 else None
    )
    return result


class TestQdrantIngestPipeline(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.pipeline = QdrantIngestPipeline(
            kunnskapsbase_path=str(self.root),
            qdrant_host="http://qdrant:6333",
            ollama_host="http://ollama:11434",
            chunk_size=20,
            chunk_overlap=2,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_default_configuration(self):
        pipeline = QdrantIngestPipeline(kunnskapsbase_path=str(self.root))
        self.assertEqual(pipeline.collection_name, "elkem_kunnskapsbase")
        self.assertEqual(pipeline.embedding_model, "nomic-embed-text")

    @patch("src.engine_agents.ingest_kunnskapsbase.requests.post")
    def test_get_embedding_returns_real_response(self, mock_post):
        mock_post.return_value = response(payload={"embedding": [0.1, 0.2, 0.3]})
        self.assertEqual(self.pipeline.get_embedding("Test prompt"), [0.1, 0.2, 0.3])
        mock_post.assert_called_once()

    @patch("src.engine_agents.ingest_kunnskapsbase.requests.post")
    def test_embedding_failure_is_explicit(self, mock_post):
        mock_post.side_effect = requests.ConnectionError("Ollama is unavailable")
        with self.assertRaisesRegex(RuntimeError, "Embedding request failed"):
            self.pipeline.get_embedding("Test prompt")

    @patch("src.engine_agents.ingest_kunnskapsbase.requests.post")
    def test_ingestion_does_not_claim_success_when_embedding_fails(self, mock_post):
        (self.root / "policy.txt").write_text("A policy document.", encoding="utf-8")
        mock_post.side_effect = requests.ConnectionError("Ollama is unavailable")

        result = self.pipeline.ingest_folder()

        self.assertEqual(result["status"], "FAILED")
        self.assertEqual(result["indexed_documents"], 0)
        self.assertEqual(result["indexed_chunks"], 0)
        self.assertIn("Embedding request failed", result["failures"][0]["error"])

    @patch("src.engine_agents.ingest_kunnskapsbase.requests.put")
    @patch("src.engine_agents.ingest_kunnskapsbase.requests.get")
    @patch("src.engine_agents.ingest_kunnskapsbase.requests.post")
    def test_ingest_extracts_embeds_and_upserts_document(
        self, mock_post, mock_get, mock_put
    ):
        (self.root / "policy.txt").write_text("A supported policy document.", encoding="utf-8")
        mock_post.return_value = response(payload={"embedding": [0.1, 0.2, 0.3]})
        mock_get.return_value = response(status_code=404)
        mock_put.return_value = response()

        result = self.pipeline.ingest_folder()

        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["discovered_documents"], 1)
        self.assertEqual(result["indexed_documents"], 1)
        self.assertGreater(result["indexed_chunks"], 1)
        self.assertEqual(result["failures"], [])
        self.assertEqual(mock_get.call_count, 1)
        self.assertEqual(mock_put.call_count, 2)  # collection creation and point upsert
        point_call = mock_put.call_args_list[1]
        point = point_call.kwargs["json"]["points"][0]
        self.assertEqual(point["vector"], [0.1, 0.2, 0.3])
        self.assertEqual(point["payload"]["source"], "policy.txt")
        self.assertIn("policy", point["payload"]["text"])

    @patch("src.engine_agents.ingest_kunnskapsbase.requests.put")
    @patch("src.engine_agents.ingest_kunnskapsbase.requests.get")
    @patch("src.engine_agents.ingest_kunnskapsbase.requests.post")
    def test_ingest_docx_and_reports_file_failure(
        self, mock_post, mock_get, mock_put
    ):
        document = Document()
        document.add_paragraph("DOCX policy text")
        document_path = self.root / "policy.docx"
        document.save(document_path)
        (self.root / "empty.md").write_text("   ", encoding="utf-8")

        mock_post.return_value = response(payload={"embedding": [0.2, 0.3]})
        mock_get.return_value = response(status_code=404)
        mock_put.return_value = response()

        result = self.pipeline.ingest_folder()

        self.assertEqual(result["status"], "PARTIAL_FAILURE")
        self.assertEqual(result["indexed_documents"], 1)
        self.assertEqual(result["discovered_documents"], 2)
        self.assertEqual(result["failures"][0]["file"], "empty.md")
        self.assertIn("No extractable text", result["failures"][0]["error"])
        self.assertEqual(mock_get.call_args.kwargs["timeout"], self.pipeline.request_timeout)

    def test_oversized_and_unsupported_documents_do_not_report_success(self):
        (self.root / "large.txt").write_text("some text", encoding="utf-8")
        (self.root / "ignored.csv").write_text("not supported", encoding="utf-8")
        pipeline = QdrantIngestPipeline(
            kunnskapsbase_path=str(self.root), max_file_bytes=2
        )

        result = pipeline.ingest_folder()

        self.assertEqual(result["status"], "FAILED")
        self.assertEqual(result["indexed_documents"], 0)
        self.assertIn("exceeds", result["failures"][0]["error"])

    def test_missing_directory_and_empty_directory_fail_explicitly(self):
        missing = QdrantIngestPipeline(kunnskapsbase_path=str(self.root / "missing"))
        empty_result = self.pipeline.ingest_folder()
        missing_result = missing.ingest_folder()
        self.assertEqual(empty_result["status"], "FAILED")
        self.assertIn("No supported documents", empty_result["failures"][0]["error"])
        self.assertEqual(missing_result["status"], "FAILED")
        self.assertIn("does not exist", missing_result["failures"][0]["error"])

    def test_collection_size_mismatch_is_rejected(self):
        with patch(
            "src.engine_agents.ingest_kunnskapsbase.requests.get",
            return_value=response(
                payload={"result": {"config": {"params": {"vectors": {"size": 768}}}}}
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "vector size is 768"):
                self.pipeline.ensure_collection(3)


if __name__ == "__main__":
    unittest.main()
