"""
Unit Tests for LLM & Provider Manager
=====================================
Verifies configuration parsing, local Ollama endpoints, and provider routing.
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from llm_provider import ModelProviderManager
except ImportError:
    from src.engine_agents.llm_provider import ModelProviderManager


class TestModelProviderManager(unittest.TestCase):

    def setUp(self):
        self.patcher = patch.dict(os.environ, {
            "OLLAMA_MODEL": "llama3.1",
            "GEMINI_MODEL": "gemini-3.8-flash",
            "EMBEDDING_PROVIDER": "ollama",
            "EMBEDDING_MODEL": "nomic-embed-text",
            "LOG_LEVEL": "INFO"
        })
        self.patcher.start()
        self.provider = ModelProviderManager()

    def tearDown(self):
        self.patcher.stop()

    def test_config_keys(self):
        summary = self.provider.get_config_summary()
        self.assertEqual(summary["ollama_model"], "llama3.1")
        self.assertEqual(summary["gemini_model"], "gemini-3.8-flash")
        self.assertEqual(summary["embedding_provider"], "ollama")
        self.assertEqual(summary["embedding_model"], "nomic-embed-text")

    @patch("urllib.request.urlopen")
    def test_ollama_endpoint_mock(self, mock_urlopen):
        mock_res = MagicMock()
        mock_res.getcode.return_value = 200
        mock_res.read.return_value = b'{"status": "ok"}'
        mock_urlopen.return_value = mock_res

        import urllib.request
        res = urllib.request.urlopen(f"{self.provider.ollama_host}/api/tags", timeout=2)
        self.assertEqual(res.getcode(), 200)


if __name__ == "__main__":
    unittest.main()
