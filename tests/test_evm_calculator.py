"""
Unit Tests for EIA-748 EVM & IFRS 15 Calculation Engine
======================================================
Tests deterministic mathematics, FAST standard compliance,
and boundary conditions (zero-division, negative values).
"""

import unittest
from src.engine_compute.evm_calculator import EVMCalculator, EVMInput, EVMResult, EACType


class TestEVMCalculator(unittest.TestCase):

    def setUp(self):
        self.standard_input = EVMInput(
            control_account_id="CA-1042",
            control_account_name="Subsea Pilot Module Development",
            bac=10000000.0,
            bcws=4000000.0,
            bcwp=3500000.0,
            acwp=3800000.0,
            contract_value=12500000.0,
            invoiced_to_date=3000000.0
        )

    def test_standard_evm_metrics(self):
        res = EVMCalculator.calculate(self.standard_input)
        
        # Variances
        self.assertEqual(res.cv, -300000.0)   # 3.5M - 3.8M = -300k
        self.assertEqual(res.sv, -500000.0)   # 3.5M - 4.0M = -500k
        
        # Indices
        self.assertAlmostEqual(res.cpi, 3500000.0 / 3800000.0, places=4)
        self.assertAlmostEqual(res.spi, 3500000.0 / 4000000.0, places=4)
        self.assertEqual(res.cost_status, "OVER_BUDGET")
        self.assertEqual(res.schedule_status, "BEHIND_SCHEDULE")

    def test_eac_methods(self):
        # 1. CPI Method
        res_cpi = EVMCalculator.calculate(self.standard_input, default_eac_method=EACType.CPI_BASED)
        expected_eac_cpi = round(10000000.0 / (3500000.0 / 3800000.0), 2)
        self.assertEqual(res_cpi.eac_cpi, expected_eac_cpi)
        self.assertEqual(res_cpi.vac, round(10000000.0 - expected_eac_cpi, 2))

        # 2. Budgeted Rate Method: ACWP + (BAC - BCWP) = 3.8M + (10M - 3.5M) = 10.3M
        res_budgeted = EVMCalculator.calculate(self.standard_input, default_eac_method=EACType.BUDGETED_RATE)
        self.assertEqual(res_budgeted.eac_budgeted, 10300000.0)

        # 3. Composite Method: ACWP + (BAC - BCWP) / (CPI * SPI)
        cpi = 3500000.0 / 3800000.0
        spi = 3500000.0 / 4000000.0
        expected_composite = round(3800000.0 + (6500000.0 / (cpi * spi)), 2)
        self.assertEqual(res_cpi.eac_composite, expected_composite)

    def test_ifrs_15_revenue_recognition(self):
        res = EVMCalculator.calculate(self.standard_input)
        
        # PoC % = ACWP / EAC
        expected_poc = round((3800000.0 / res.eac_cpi) * 100, 2)
        self.assertEqual(res.poc_percentage, expected_poc)
        
        # Recognized Revenue = PoC * Contract Value (12.5M)
        expected_rev = round(12500000.0 * (res.poc_percentage / 100.0), 2)
        self.assertAlmostEqual(res.recognized_revenue, expected_rev, delta=100.0)
        
        # Contract Asset = Recognized (approx 4.37M) - Invoiced (3.0M) > 0
        self.assertGreater(res.contract_asset, 0)
        self.assertEqual(res.contract_liability, 0.0)

    def test_contract_liability_advance_payment(self):
        advance_input = EVMInput(
            control_account_id="CA-9999",
            control_account_name="Advance Payment Test",
            bac=1000000.0,
            bcws=200000.0,
            bcwp=200000.0,
            acwp=200000.0,
            contract_value=1000000.0,
            invoiced_to_date=500000.0  # 500k invoiced vs 200k earned
        )
        res = EVMCalculator.calculate(advance_input)
        self.assertEqual(res.contract_asset, 0.0)
        self.assertAlmostEqual(res.contract_liability, 300000.0, delta=1.0)

    def test_zero_actual_cost_edge_case(self):
        # Work scheduled but no costs incurred yet
        zero_cost_input = EVMInput(
            control_account_id="CA-0001",
            control_account_name="Unstarted Project",
            bac=5000000.0,
            bcws=100000.0,
            bcwp=0.0,
            acwp=0.0
        )
        res = EVMCalculator.calculate(zero_cost_input)
        self.assertEqual(res.cpi, 1.0)
        self.assertEqual(res.cv, 0.0)
        self.assertEqual(res.poc_percentage, 0.0)

    def test_input_validation_errors(self):
        with self.assertRaises(ValueError):
            EVMCalculator.calculate(EVMInput("CA-ERR", "Test", bac=0.0, bcws=0, bcwp=0, acwp=0))

        with self.assertRaises(ValueError):
            EVMCalculator.calculate(EVMInput("CA-ERR", "Test", bac=100.0, bcws=-10.0, bcwp=0, acwp=0))

    def test_to_dict_conversion(self):
        res = EVMCalculator.calculate(self.standard_input)
        d = res.to_dict()
        self.assertIsInstance(d, dict)
        self.assertIn("cpi", d)
        self.assertIn("poc_percentage", d)
        self.assertEqual(d["control_account_id"], "CA-1042")


if __name__ == "__main__":
    unittest.main()

