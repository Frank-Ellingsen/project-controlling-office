"""
Microsoft 365 Ecosystem Integration Module
===========================================
Connects Elkem Project Controller App to:
- MS Teams (Notifications & HITL Approvals)
- Power BI (Push Datasets & S-Curves)
- MS Graph / OneDrive (Document Auto-Sync to VectorDB)
- PowerPoint (Automated Executive Presentations)
"""

from typing import Dict, Any, List
import json


class MSTeamsConnector:
    """
    Kopler agenten til Microsoft Teams via Webhooks / Bot Framework
    for avviksvarsling og godkjenningskort (Adaptive Cards).
    """
    
    @staticmethod
    def format_adaptive_card_approval(project_id: str, eac_adjustment: float, reason: str) -> Dict[str, Any]:
        """
        Bygger et Microsoft Teams Adaptive Card for Human-in-the-Loop (HITL) godkjenning.
        """
        return {
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": f"⚠️ Endring i EAC-prognose krever godkjenning: {project_id}",
                    "weight": "Bolder",
                    "size": "Medium",
                    "color": "Warning"
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {"title": "Prosjekt ID:", "value": project_id},
                        {"title": "Beregnet EAC-justering:", "value": f"{eac_adjustment:,.2f} NOK"},
                        {"title": "Årsak / Avvik:", "value": reason}
                    ]
                }
            ],
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "✅ Godkjenn og oppdater ERP",
                    "data": {"action": "approve", "project_id": project_id, "amount": eac_adjustment}
                },
                {
                    "type": "Action.Submit",
                    "title": "❌ Avvis og behold opprinnelig EAC",
                    "data": {"action": "reject", "project_id": project_id}
                }
            ]
        }


class PowerBIStreamConnector:
    """
    Streamer EVM-beregninger og IFRS 15-tall direkte inn i Power BI Push Datasets.
    """
    
    @staticmethod
    def prepare_push_payload(evm_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "rows": evm_metrics
        }


class PowerPointDeckGenerator:
    """
    Genererer månedlige statusoversikter for prosjektmøter.
    """
    
    @staticmethod
    def generate_monthly_deck_summary(project_name: str, metrics: Dict[str, Any]) -> str:
        return f"PowerPoint slaidsett for {project_name} generert med CPI={metrics.get('cpi')}, SPI={metrics.get('spi')}."


if __name__ == "__main__":
    teams_card = MSTeamsConnector.format_adaptive_card_approval(
        project_id="CA-1042",
        eac_adjustment=857142.86,
        reason="CPI under 0.95 pga uforutsette offshore testkostnader."
    )
    print("--- TEAMS ADAPTIVE CARD PAYLOAD ---")
    print(json.dumps(teams_card, indent=2, ensure_ascii=False))

