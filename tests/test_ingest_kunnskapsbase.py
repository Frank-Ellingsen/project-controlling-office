"""
Unit Tests for Qdrant Ingestion Pipeline
========================================
Tests folder scanning, document filtering, embedding fallback,
and collection definition.
"""

import unittest
import os
from unittest.mock import patch, MagicMock
from src.engine_agents.ingest_kunnskapsbase import QdrantIngestPipeline


class TestQdrantIngestPipeline(unittest.TestCase):

    def setUp(self):
        self.pipeline = QdrantIngestPipeline()

    def test_default_paths(self):
        self.assertTrue(os.path.exists(self.pipeline.kunnskapsbase_path))
        self.assertEqual(self.pipeline.collection_name, "elkem_kunnskapsbase")
        self.assertEqual(self.pipeline.embedding_model, "nomic-embed-text")

    def test_get_embedding_fallback(self):
        # When Ollama is offline / unreachable, fallback vector must have 768 dimensions
        vec = self.pipeline.get_embedding("Test prompt")
        self.assertEqual(len(vec), 768)
        self.assertEqual(vec[0], 0.0)

    @patch("requests.post")
    def test_get_embedding_mock(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"embedding": [0.1] * 768}
        mock_post.return_value = mock_resp

        vec = self.pipeline.get_embedding("Test with live mock")
        self.assertEqual(len(vec), 768)
        self.assertEqual(vec[0], 0.1)

    def test_ingest_folder_scan(self):
        res = self.pipeline.ingest_folder()
        self.assertEqual(res["status"], "SUCCESS")
        self.assertGreater(res["total_files"], 0)
        self.assertGreater(res["indexed_documents"], 0)
        self.assertIn("sample_files", res)


if __name__ == "__main__":
    unittest.main()

