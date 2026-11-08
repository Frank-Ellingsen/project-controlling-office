"""
EVM & Financial Control Calculation Engine (Root Compatibility Wrapper)
=======================================================================
Re-exports from src.engine_compute.evm_calculator
"""

from src.engine_compute.evm_calculator import (
    EVMCalculator,
    EVMInput,
    EVMResult,
    EACType,
    ElkemEVMComplianceEngine
)

__all__ = [
    "EVMCalculator",
    "EVMInput",
    "EVMResult",
    "EACType",
    "ElkemEVMComplianceEngine"
]

if __name__ == "__main__":
    calc = EVMCalculator()
    portfolio = calc.get_elkem_portfolio_sample_data()
    print("--- ELKEM ASA TECHNOLOGY PORTFOLIO EVM CALCULATION ---")
    for item in portfolio:
        res = calc.calculate(item)
        print(f"[{res.control_account_id}] {res.control_account_name} ({res.grant_funding_body})")
        print(f"  CPI: {res.cpi} ({res.cost_status}) | SPI: {res.spi} ({res.schedule_status})")
        print(f"  BAC: {res.bac:,.2f} NOK | EAC: {res.eac_cpi:,.2f} NOK | PoC: {res.poc_percentage}%")
        print(f"  Contract Asset: {res.contract_asset:,.2f} NOK\n")
