"""
Unit Tests for DuckDB Local Analytics Store
===========================================
Tests OLAP tables, actuals aggregation (labor + procurement),
and S-curve extraction.
"""

import unittest
import os
import tempfile
from src.engine_compute.duckdb_store import DuckDBStore


class TestDuckDBStore(unittest.TestCase):

    def setUp(self):
        # Create a temporary database for test isolation
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_analytics.duckdb")
        self.store = DuckDBStore(db_path=self.db_path)
        self.store.seed_sample_data()

    def tearDown(self):
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass

    def test_schema_initialization(self):
        with self.store.get_connection() as conn:
            tables = [r[0] for r in conn.execute("SHOW TABLES;").fetchall()]
            self.assertIn("wbs_nodes", tables)
            self.assertIn("time_entries", tables)
            self.assertIn("procurement_actuals", tables)
            self.assertIn("fact_monthly_actuals", tables)

    def test_query_evm_actuals(self):
        actuals = self.store.query_evm_actuals("CA-1042")
        self.assertEqual(actuals["project_id"], "CA-1042")
        
        # Expected labor:
        # T-001: 160h * 650 = 104,000
        # T-002: 150h * 520 = 78,000
        # T-003: 170h * 480 = 81,600
        # Total Labor = 263,600 NOK
        self.assertEqual(actuals["labor_cost_nok"], 263600.0)
        
        # Expected procurement:
        # PO-901: 1,500,000
        # PO-902: 2,000,000
        # Total Procurement = 3,500,000 NOK
        self.assertEqual(actuals["procurement_cost_nok"], 3500000.0)
        
        # Total ACWP = 263,600 + 3,500,000 = 3,763,600 NOK
        self.assertEqual(actuals["total_acwp_nok"], 3763600.0)

    def test_query_evm_actuals_nonexistent_project(self):
        actuals = self.store.query_evm_actuals("CA-NONEXISTENT")
        self.assertEqual(actuals["total_acwp_nok"], 0.0)
        self.assertEqual(actuals["labor_cost_nok"], 0.0)

    def test_get_s_curve_data(self):
        df = self.store.get_s_curve_data("CA-1042")
        self.assertFalse(df.empty)
        self.assertEqual(len(df), 3)
        self.assertIn("Planned Value (PV)", df.columns)
        self.assertIn("Earned Value (EV)", df.columns)
        self.assertIn("Actual Cost (AC)", df.columns)


if __name__ == "__main__":
    unittest.main()

