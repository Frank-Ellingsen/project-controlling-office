"""
Integration Tests for FastAPI Backend Endpoints
===============================================
Tests:
- /health
- /api/v1/evm/calculate
- /api/v1/grants/skattefunn
- /api/v1/orchestrator/route
- /api/v1/integrations/teams/approval-card
- /api/v1/analytics/evm-actuals/{project_id}
- /api/v1/integrations/powerbi/push-scurve
- /api/v1/rag/ingest
- /api/v1/audit/logs
"""

import unittest
from fastapi.testclient import TestClient
from src.api.main import app, duckdb_store


class TestFastAPIBackend(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        duckdb_store.seed_sample_data()

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("COSO 2013", data["governance"])
        self.assertTrue(data["duckdb_connected"])

    def test_evm_calculate_endpoint(self):
        payload = {
            "control_account_id": "CA-1042",
            "control_account_name": "Subsea Pilot Module Development",
            "bac": 10000000.0,
            "bcws": 4000000.0,
            "bcwp": 3500000.0,
            "acwp": 3800000.0,
            "contract_value": 12500000.0,
            "invoiced_to_date": 3000000.0,
            "eac_method": "cpi"
        }
        response = self.client.post("/api/v1/evm/calculate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["cv"], -300000.0)
        self.assertEqual(data["sv"], -500000.0)
        self.assertAlmostEqual(data["cpi"], 3500000.0 / 3800000.0, places=4)
        self.assertEqual(data["cost_status"], "OVER_BUDGET")

    def test_skattefunn_endpoint(self):
        payload = {
            "project_id": "CA-1042",
            "fiscal_year": 2025,
            "hourly_rate_claimed": 650.0,
            "hours_logged": 1920.0,
            "procured_rd_services": 1200000.0,
            "other_direct_costs": 450000.0
        }
        response = self.client.post("/api/v1/grants/skattefunn", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["approved_hourly_rate"], 530.0)
        self.assertEqual(data["approved_hours"], 1850.0)
        self.assertTrue(data["hourly_rate_exceeded"])
        self.assertTrue(data["hours_exceeded"])

    def test_orchestrator_route_endpoint(self):
        payload = {"query": "Hva er reglene for SkatteFUNN i 2025?"}
        response = self.client.post("/api/v1/orchestrator/route", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["intent"], "VECTOR_RAG")
        self.assertEqual(data["routing_target"], "rag_kunnskapsbase_agent")

    def test_teams_card_endpoint(self):
        payload = {
            "project_id": "CA-1042",
            "eac_adjustment": 857142.86,
            "reason": "Cost overrun test"
        }
        response = self.client.post("/api/v1/integrations/teams/approval-card", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["type"], "AdaptiveCard")

    def test_duckdb_evm_actuals_endpoint(self):
        response = self.client.get("/api/v1/analytics/evm-actuals/CA-1042")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["project_id"], "CA-1042")
        self.assertGreater(data["total_acwp_nok"], 0)

    def test_powerbi_push_endpoint(self):
        payload = {"project_id": "CA-1042", "periods": 6}
        response = self.client.post("/api/v1/integrations/powerbi/push-scurve", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "SIMULATED_PUSH_SUCCESS")
        self.assertEqual(data["rows_pushed"], 6)

    def test_rag_ingest_endpoint(self):
        response = self.client.post("/api/v1/rag/ingest")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertGreater(data["indexed_documents"], 0)

    def test_audit_logs_endpoint(self):
        response = self.client.get("/api/v1/audit/logs")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["integrity_verified"])
        self.assertIsInstance(data["entries"], list)


if __name__ == "__main__":
    unittest.main()
