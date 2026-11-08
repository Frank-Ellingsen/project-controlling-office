"""
Multi-Agent Orchestrator & Dual-Mode Chat Router (Root Compatibility Wrapper)
=============================================================================
Re-exports from src.engine_agents.orchestrator
"""

import json
from src.engine_agents.orchestrator import OrchestratorRouter, IntentType

if __name__ == "__main__":
    router = OrchestratorRouter()
    sample_query = "Er avviket på CPI for prosjekt CA-1042 innenfor Enova sine retningslinjer for godkjente FoU-kostnader?"
    print(json.dumps(router.process_query(sample_query), indent=2, ensure_ascii=False))
