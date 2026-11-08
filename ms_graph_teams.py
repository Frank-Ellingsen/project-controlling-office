"""
Microsoft 365 Ecosystem Integration Module (Root Compatibility Wrapper)
========================================================================
Re-exports from src.integrations.ms_graph_teams
"""

import json
from src.integrations.ms_graph_teams import (
    MSTeamsConnector,
    PowerBIStreamConnector,
    PowerPointDeckGenerator
)

if __name__ == "__main__":
    teams_card = MSTeamsConnector.format_adaptive_card_approval(
        project_id="CA-1042",
        eac_adjustment=857142.86,
        reason="CPI under 0.95 pga uforutsette offshore testkostnader."
    )
    print("--- TEAMS ADAPTIVE CARD PAYLOAD ---")
    print(json.dumps(teams_card, indent=2, ensure_ascii=False))
