"""
Unit Tests for External Integrations & Connectors
=================================================
Tests MS Teams Adaptive Cards, Power BI push datasets,
and Norwegian Public API connectors (Brreg, Enova).
"""

import unittest
from src.integrations.ms_graph_teams import (
    MSTeamsConnector,
    PowerBIStreamConnector,
    PowerPointDeckGenerator
)
from src.integrations.norwegian_public_apis import (
    PublicRegistryConnector,
    GrantRegistryConnector
)


class TestIntegrations(unittest.TestCase):

    def test_ms_teams_adaptive_card_structure(self):
        card = MSTeamsConnector.format_adaptive_card_approval(
            project_id="CA-1042",
            eac_adjustment=857142.86,
            reason="CPI below threshold 0.95"
        )
        self.assertEqual(card["type"], "AdaptiveCard")
        self.assertEqual(card["version"], "1.4")
        self.assertEqual(len(card["actions"]), 2)
        
        approve_action = card["actions"][0]
        self.assertEqual(approve_action["data"]["action"], "approve")
        self.assertEqual(approve_action["data"]["project_id"], "CA-1042")

    def test_power_bi_payload_formatting(self):
        metrics = [{"cpi": 0.92, "spi": 0.88, "control_account_id": "CA-1042"}]
        payload = PowerBIStreamConnector.prepare_push_payload(metrics)
        self.assertIn("rows", payload)
        self.assertEqual(payload["rows"][0]["cpi"], 0.92)

    def test_powerpoint_deck_summary(self):
        summary = PowerPointDeckGenerator.generate_monthly_deck_summary(
            project_name="Subsea Pilot",
            metrics={"cpi": 0.92, "spi": 0.88}
        )
        self.assertIn("Subsea Pilot", summary)
        self.assertIn("CPI=0.92", summary)

    def test_public_registry_vendor_verification(self):
        vendor = PublicRegistryConnector.verify_vendor("922995481")
        self.assertEqual(vendor["org_number"], "922995481")
        self.assertEqual(vendor["name"], "ELKEM ASA")
        self.assertTrue(vendor["is_active"])

    def test_grant_registry_status(self):
        grant = GrantRegistryConnector.get_grant_status("GRANT-2024-1042")
        self.assertEqual(grant["grant_id"], "GRANT-2024-1042")
        self.assertEqual(grant["status"], "APPROVED")
        self.assertEqual(grant["approved_amount"], 15000000.0)


if __name__ == "__main__":
    unittest.main()

