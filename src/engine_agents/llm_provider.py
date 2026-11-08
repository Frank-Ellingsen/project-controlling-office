"""
LLM & Embedding Provider Manager
================================
Handles hybrid model routing between:
1. Local Ollama (llama3.1 for private reasoning + nomic-embed-text for local RAG)
2. Gemini (gemini-3.8-flash for fast multimodal/OCR & heavy summarization)
3. Serper API (for web research & live market data)
"""

import os
import json
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load local environment variables from .env
load_dotenv()


class ModelProviderManager:
    """
    Styrer koblingen mot lokalt installert Ollama, Gemini API og Serper Web Search.
    """
    def __init__(self):
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", self.ollama_host)
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")
        self.embedding_provider = os.getenv("EMBEDDING_PROVIDER", "ollama")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
        self.serper_key = os.getenv("SERPER_API_KEY", "")
        self.mini_key = os.getenv("MINI_API_KEY", "")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

    def get_config_summary(self) -> Dict[str, Any]:
        """Returnerer aktiv systemkonfigurasjon for diagnostikk."""
        return {
            "ollama_host": self.ollama_host,
            "ollama_base_url": self.ollama_base_url,
            "ollama_model": self.ollama_model,
            "gemini_model": self.gemini_model,
            "gemini_configured": bool(self.gemini_key),
            "embedding_provider": self.embedding_provider,
            "embedding_model": self.embedding_model,
            "serper_configured": bool(self.serper_key),
            "mini_api_configured": bool(self.mini_key),
            "log_level": self.log_level
        }


if __name__ == "__main__":
    mgr = ModelProviderManager()
    print("=== MODEL PROVIDER CONFIGURATION ===")
    print(json.dumps(mgr.get_config_summary(), indent=2))

