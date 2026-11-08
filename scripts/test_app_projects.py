"""
Test script verifying all 3 projects in the Streamlit Executive Workstation UI
==============================================================================
Tests EVM calculations, DuckDB OLAP queries, Power BI S-Curves,
and Orchestrator routing across CA-1042, CA-2088, and CA-3015.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.engine_compute.evm_calculator import EVMCalculator, EVMInput, EACType
from src.engine_compute.duckdb_store import DuckDBStore, DuckDBStoreManager
from src.integrations.powerbi_push import PowerBIPushPipeline
from src.engine_agents.orchestrator import OrchestratorRouter
from src.engine_compute.grant_calculator import SkatteFUNNCalculator, SkatteFUNNInput
from src.engine_agents.audit_logger import AuditLogger


def run_project_test_suite():
    print("=======================================================================")
    print("   ELKEM TECHNOLOGY CONTROLLER HUB — 3 PROJECTS COMPREHENSIVE TEST     ")
    print("=======================================================================")

    store = DuckDBStore()
    pbi = PowerBIPushPipeline()
    router = OrchestratorRouter()
    audit_logger = AuditLogger()

    project_data = {
        "CA-1042": EVMInput(
            control_account_id="CA-1042",
            control_account_name="Furnace Automation & Digital Twin System",
            project_domain="Furnace Technology & Automation",
            cam_name="Ingeniør Marianne Lie (Senior Controller)",
            bac=10000000.0,
            bcws=4000000.0,
            bcwp=3500000.0,
            acwp=3800000.0,
            grant_funding_body="Norges Forskningsråd (NFR)",
            contract_value=12500000.0,
            invoiced_to_date=3000000.0
        ),
        "CA-2088": EVMInput(
            control_account_id="CA-2088",
            control_account_name="Silicon Battery Anode R&D",
            project_domain="Silicon & Carbon Solutions",
            cam_name="Kjell Arne Bakke (R&D Director)",
            bac=25000000.0,
            bcws=12000000.0,
            bcwp=12500000.0,
            acwp=11800000.0,
            grant_funding_body="SkatteFUNN (RF-1053B)",
            contract_value=30000000.0,
            invoiced_to_date=10000000.0
        ),
        "CA-3015": EVMInput(
            control_account_id="CA-3015",
            control_account_name="Fiskaa Furnace Digital Twin & Carbon Pilot",
            project_domain="Process Development & Pilot Plant",
            cam_name="Dr. Håkon Olsen (Lead Scientist)",
            bac=8000000.0,
            bcws=5000000.0,
            bcwp=4200000.0,
            acwp=4600000.0,
            grant_funding_body="Enova (Klima- og energifondet)",
            contract_value=9500000.0,
            invoiced_to_date=4000000.0
        )
    }

    results = {}

    for pid, inp in project_data.items():
        print(f"\n[{pid}] PROSJEKT: {inp.control_account_name}")
        print(f"      Ansvarlig CAM : {inp.cam_name} | Domene: {inp.project_domain}")
        print(f"      Tilskuddsorgan: {inp.grant_funding_body}")
        print("-" * 71)

        # 1. Test EVM Calculations across 3 EAC forecasting methods
        for eac_method in [EACType.CPI_BASED, EACType.COMPOSITE, EACType.BUDGETED_RATE]:
            res = EVMCalculator.calculate(inp, default_eac_method=eac_method)
            print(f"  [EVM {eac_method.value.upper():10s}] CPI: {res.cpi:.4f} ({res.cost_status:12s}) | "
                  f"SPI: {res.spi:.4f} ({res.schedule_status:15s}) | "
                  f"EAC: {res.eac_cpi:>12,.0f} NOK | PoC: {res.poc_percentage:>5.1f}% | "
                  f"Contract Asset: {res.contract_asset:>11,.0f} NOK")
            results[f"{pid}_{eac_method.value}"] = res

        # 2. Test DuckDB OLAP Actuals Query
        actuals = store.query_evm_actuals(pid)
        print(f"  [DuckDB Store  ] Labor: {actuals['labor_cost_nok']:>10,.0f} NOK | "
              f"Procurement: {actuals['procurement_cost_nok']:>10,.0f} NOK | "
              f"Bokført ACWP: {actuals['total_acwp_nok']:>10,.0f} NOK")

        # 3. Test Power BI S-Curve Streaming Generation
        scurve = pbi.generate_scurve_rows(pid, periods=8)
        print(f"  [Power BI Push ] Generert S-kurve: {len(scurve)} månedspunkter. "
              f"Sluttpunkt: PV={scurve[-1]['bcws_pv_nok']:,.0f}, "
              f"EV={scurve[-1]['bcwp_ev_nok']:,.0f}, AC={scurve[-1]['acwp_ac_nok']:,.0f} NOK")

        # 4. Test Orchestrator Router Intent Classification
        route = router.process_query(f"Hva er årsaken til CPI-avviket på prosjekt {pid}?")
        print(f"  [AI Orchestrator] Spørring: 'Hva er årsaken til CPI-avviket på prosjekt {pid}?'\n"
              f"                   -> Intent: {route['intent']} | Ruting: {route['routing_target']}")

        # 5. Test SkatteFUNN & Grants calculation
        sk_res = SkatteFUNNCalculator.calculate(SkatteFUNNInput(
            project_id=pid,
            fiscal_year=2025,
            hourly_rate_claimed=580.0 if pid == "CA-1042" else 500.0,
            hours_logged=1900.0 if pid == "CA-1042" else 1500.0,
            procured_rd_services=1500000.0,
            other_direct_costs=300000.0
        ))
        print(f"  [SkatteFUNN RF ] Godkjent timesats: {sk_res.approved_hourly_rate:.0f} NOK/t | "
              f"Godkjente timer: {sk_res.approved_hours:.0f} t | "
              f"Beregnet skattefradrag (19%): {sk_res.tax_deduction_amount:,.0f} NOK")

    # 6. Verify COSO / EU AI Act Audit Integrity
    chain_valid = audit_logger.verify_chain_integrity()
    print("\n" + "=" * 71)
    print(f" [UFORANDERLIG REVISJONSLOGG] COSO 2013 / EU AI Act Art. 12 SHA-256 Kjederesultat: {'🟢 GYLDIG' if chain_valid else '🔴 KOMPROMITTERT'}")
    print("=" * 71)

    return results


if __name__ == "__main__":
    run_project_test_suite()

