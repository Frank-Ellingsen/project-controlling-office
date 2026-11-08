"""
Unit & Integration Tests for OpenAPI Server & Interactive Dashboard
===================================================================
Tests OpenAPI 3.1 endpoints, HTML dashboard delivery,
EIA-748 calculations, and HITL cryptographic audit logging.
"""

import unittest
from fastapi.testclient import TestClient
from openapi_server import app


class TestOpenAPIServer(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_dashboard_delivery(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.headers["content-type"])
        self.assertIn("Project Controlling", res.text)

    def test_dashboard_alias(self):
        res = self.client.get("/dashboard")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.headers["content-type"])

    def test_health_endpoint(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["coso_audit_chain_intact"])
        self.assertIn("ANSI/EIA-748 EVM", data["standards"])

    def test_wbs_elements_endpoint(self):
        res = self.client.get("/api/v1/wbs")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreater(data["count"], 0)
        self.assertEqual(data["project_id"], "ZEP-26")

    def test_scurve_timeseries_endpoint(self):
        res = self.client.get("/api/v1/scurve")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["time_series"]), 24)
        self.assertEqual(data["cutoff_month"], 20)

    def test_evm_calculate_endpoint(self):
        payload = {
            "control_account_id": "WBS-2.1",
            "control_account_name": "Refractory Lining",
            "bac": 26000000.0,
            "bcws": 22000000.0,
            "bcwp": 19800000.0,
            "acwp": 23200000.0,
            "contract_value": 32000000.0,
            "invoiced_to_date": 15000000.0,
            "eac_method": "cpi"
        }
        res = self.client.post("/api/v1/evm/calculate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["cv"], -3400000.0)
        self.assertEqual(data["sv"], -2200000.0)
        self.assertAlmostEqual(data["cpi"], 19800000.0 / 23200000.0, places=4)
        self.assertEqual(data["cost_status"], "OVER_BUDGET")

    def test_grant_vouchers_endpoint(self):
        res = self.client.get("/api/v1/grants/vouchers")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreater(data["count"], 0)

        # Filter by Enova
        res_enova = self.client.get("/api/v1/grants/vouchers?scheme=Enova")
        self.assertEqual(res_enova.status_code, 200)
        data_enova = res_enova.json()
        for v in data_enova["vouchers"]:
            self.assertEqual(v["scheme"], "Enova")

    def test_skattefunn_endpoint(self):
        payload = {
            "project_id": "ZEP-26",
            "fiscal_year": 2025,
            "hourly_rate_claimed": 650.0,
            "hours_logged": 1920.0,
            "procured_rd_services": 1200000.0,
            "other_direct_costs": 450000.0
        }
        res = self.client.post("/api/v1/grants/skattefunn", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["approved_hourly_rate"], 530.0)
        self.assertEqual(data["approved_hours"], 1850.0)

    def test_hitl_action_submission(self):
        payload = {
            "action_id": "ACT-2026-092",
            "decision": "APPROVE",
            "actor": "Frank Ellingsen (Lead Project Controller)",
            "notes": "Thermal soak verified"
        }
        res = self.client.post("/api/v1/hitl/action", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "COMMITTED")
        self.assertEqual(data["decision"], "APPROVE")
        self.assertIn("audit_hash", data)

    def test_audit_logs_retrieval(self):
        res = self.client.get("/api/v1/audit/logs")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["chain_intact"])
        self.assertIsInstance(data["logs"], list)


if __name__ == "__main__":
    unittest.main()

