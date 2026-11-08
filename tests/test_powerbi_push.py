"""
Unit Tests for Power BI Push Pipeline
=====================================
Tests S-Curve dataset row generation, CPI/SPI math,
and simulated push payload.
"""

import unittest
from src.integrations.powerbi_push import PowerBIPushPipeline


class TestPowerBIPushPipeline(unittest.TestCase):

    def setUp(self):
        self.pipeline = PowerBIPushPipeline(dataset_id="test-ds", group_id="test-grp")

    def test_generate_scurve_rows(self):
        rows = self.pipeline.generate_scurve_rows("CA-1042", periods=6)
        self.assertEqual(len(rows), 6)
        
        # Test Month 1
        m1 = rows[0]
        self.assertEqual(m1["month_num"], 1)
        self.assertEqual(m1["bcws_pv_nok"], 1000000.0)
        self.assertEqual(m1["bcwp_ev_nok"], 950000.0)
        self.assertEqual(m1["acwp_ac_nok"], 1030000.0)
        self.assertAlmostEqual(m1["cpi"], 950000.0 / 1030000.0, places=4)
        self.assertAlmostEqual(m1["spi"], 950000.0 / 1000000.0, places=4)

        # Test Month 6 cumulative
        m6 = rows[5]
        self.assertEqual(m6["month_num"], 6)
        self.assertEqual(m6["bcws_pv_nok"], 6000000.0)

    def test_push_scurve_data_structure(self):
        res = self.pipeline.push_scurve_data("CA-1042", periods=4)
        self.assertEqual(res["status"], "SIMULATED_PUSH_SUCCESS")
        self.assertEqual(res["rows_pushed"], 4)
        self.assertIn("tables/SCurveData/rows", res["endpoint"])
        self.assertIn("cpi", res["sample_row"])


if __name__ == "__main__":
    unittest.main()

