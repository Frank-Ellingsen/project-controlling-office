"""
EVM & Financial Control Calculation Engine (Root Compatibility Wrapper)
=======================================================================
Re-exports from src.engine_compute.evm_calculator
"""

from src.engine_compute.evm_calculator import (
    EVMCalculator,
    EVMInput,
    EVMResult,
    EACType
)

if __name__ == "__main__":
    sample_input = EVMInput(
        control_account_id="CA-1042",
        control_account_name="Subsea Pilot Module Development",
        bac=10000000.0,
        bcws=4000000.0,
        bcwp=3500000.0,
        acwp=3800000.0,
        contract_value=12500000.0,
        invoiced_to_date=3000000.0
    )
    res = EVMCalculator.calculate(sample_input)
    print("--- EVM & IFRS 15 CALCULATION RESULT ---")
    print(f"Control Account : {res.control_account_name} ({res.control_account_id})")
    print(f"Cost Variance   : {res.cv:,.2f} NOK (CPI: {res.cpi}) -> {res.cost_status}")
    print(f"Sched Variance  : {res.sv:,.2f} NOK (SPI: {res.spi}) -> {res.schedule_status}")
    print(f"Forecast EAC    : {res.eac_cpi:,.2f} NOK (VAC: {res.vac:,.2f} NOK)")
    print(f"IFRS 15 Progress: {res.poc_percentage}%")
    print(f"Recognized Rev  : {res.recognized_revenue:,.2f} NOK")
    print(f"Contract Asset  : {res.contract_asset:,.2f} NOK (Unbilled Revenue)")
