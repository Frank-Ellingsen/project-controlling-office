"""
Unit Tests for SkatteFUNN & Grant Calculation Engine
====================================================
Tests statutory ceilings (530 kr/h, 1850 h, 25M NOK cap),
19% tax deduction computation, and audit warnings.
"""

import unittest
from src.engine_compute.grant_calculator import (
    SkatteFUNNCalculator,
    SkatteFUNNInput,
    SkatteFUNNResult
)


class TestSkatteFUNNCalculator(unittest.TestCase):

    def test_standard_compliant_claim(self):
        # 1000 hours at 500 NOK/hour (below 530 limit)
        inp = SkatteFUNNInput(
            project_id="SK-001",
            fiscal_year=2025,
            hourly_rate_claimed=500.0,
            hours_logged=1000.0,
            procured_rd_services=200000.0,
            other_direct_costs=50000.0
        )
        res = SkatteFUNNCalculator.calculate(inp)
        
        self.assertEqual(res.approved_hourly_rate, 500.0)
        self.assertEqual(res.approved_hours, 1000.0)
        self.assertEqual(res.approved_internal_labor_cost, 500000.0)
        self.assertEqual(res.total_eligible_cost_basis, 750000.0)
        self.assertEqual(res.tax_deduction_amount, 750000.0 * 0.19)
        self.assertFalse(res.hourly_rate_exceeded)
        self.assertFalse(res.hours_exceeded)
        self.assertFalse(res.capped_by_max_limit)
        self.assertEqual(len(res.audit_notes), 0)

    def test_hourly_rate_capping(self):
        # Claimed 750 NOK/hr -> should be capped at 530 NOK/hr
        inp = SkatteFUNNInput(
            project_id="SK-002",
            fiscal_year=2025,
            hourly_rate_claimed=750.0,
            hours_logged=1000.0
        )
        res = SkatteFUNNCalculator.calculate(inp)
        self.assertEqual(res.approved_hourly_rate, 530.0)
        self.assertTrue(res.hourly_rate_exceeded)
        self.assertEqual(res.approved_internal_labor_cost, 530000.0)

    def test_annual_hours_capping(self):
        # Claimed 2100 hours -> should be capped at 1850 hours
        inp = SkatteFUNNInput(
            project_id="SK-003",
            fiscal_year=2025,
            hourly_rate_claimed=500.0,
            hours_logged=2100.0
        )
        res = SkatteFUNNCalculator.calculate(inp)
        self.assertEqual(res.approved_hours, 1850.0)
        self.assertTrue(res.hours_exceeded)
        self.assertEqual(res.approved_internal_labor_cost, 1850.0 * 500.0)

    def test_total_cost_basis_cap(self):
        # Subtotal exceeds 25M NOK cap
        inp = SkatteFUNNInput(
            project_id="SK-004",
            fiscal_year=2025,
            hourly_rate_claimed=530.0,
            hours_logged=1850.0,
            procured_rd_services=28000000.0  # 28M NOK external services
        )
        res = SkatteFUNNCalculator.calculate(inp)
        self.assertTrue(res.capped_by_max_limit)
        self.assertEqual(res.total_eligible_cost_basis, 25000000.0)
        self.assertEqual(res.tax_deduction_amount, 25000000.0 * 0.19)


if __name__ == "__main__":
    unittest.main()

