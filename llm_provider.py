"""
LLM & Embedding Provider Manager (Root Compatibility Wrapper)
=============================================================
Re-exports from src.engine_agents.llm_provider
"""

import json
from src.engine_agents.llm_provider import ModelProviderManager

if __name__ == "__main__":
    mgr = ModelProviderManager()
    print("=== MODEL PROVIDER CONFIGURATION ===")
    print(json.dumps(mgr.get_config_summary(), indent=2))
