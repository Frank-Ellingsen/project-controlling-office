"""
EVM & Financial Control Calculation Engine
==========================================
Deterministic Python engine for Earned Value Management (EIA-748) 
and IFRS 15 Revenue Recognition calculations.

Rules:
- NO LLM calls or probabilistic models inside this module.
- FAST Standard compliant (Clear, Structured, Transparent).
- Strict zero-division protection and type safety.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum
import math


class EACType(Enum):
    CPI_BASED = "cpi"               # EAC = BAC / CPI (Typical future performance equals past)
    COMPOSITE = "composite"         # EAC = ACWP + (BAC - BCWP) / (CPI * SPI) (Critical path / cost+schedule impact)
    BUDGETED_RATE = "budgeted"     # EAC = ACWP + (BAC - BCWP) (Future work performed at planned budget)


@dataclass
class EVMInput:
    control_account_id: str
    control_account_name: str
    bac: float      # Budget at Completion (Planned total budget)
    bcws: float     # Budgeted Cost of Work Scheduled (Planned Value / PV)
    bcwp: float     # Budgeted Cost of Work Performed (Earned Value / EV)
    acwp: float     # Actual Cost of Work Performed (Actual Cost / AC)
    contract_value: Optional[float] = None  # Total contract price for IFRS 15
    invoiced_to_date: Optional[float] = None # Milestone invoices sent to customer


@dataclass
class EVMResult:
    control_account_id: str
    control_account_name: str
    
    # Core Metrics
    bac: float
    bcws: float
    bcwp: float
    acwp: float
    
    # Variances
    cv: float       # Cost Variance (BCWP - ACWP)
    sv: float       # Schedule Variance (BCWP - BCWS)
    
    # Performance Indices
    cpi: float      # Cost Performance Index (BCWP / ACWP)
    spi: float      # Schedule Performance Index (BCWP / BCWS)
    
    # Forecasts
    eac_cpi: float            # EAC based on CPI
    eac_composite: float      # EAC based on CPI * SPI
    eac_budgeted: float       # EAC based on original plan rate
    etc: float                # Estimate to Complete (EAC - ACWP)
    vac: float                # Variance at Completion (BAC - EAC)
    tcpi_bac: float           # To-Complete Performance Index vs BAC
    
    # Status Flags
    cost_status: str          # "UNDER_BUDGET", "ON_BUDGET", "OVER_BUDGET"
    schedule_status: str      # "AHEAD_OF_SCHEDULE", "ON_SCHEDULE", "BEHIND_SCHEDULE"
    
    # IFRS 15 Financial Accounting Integration
    poc_percentage: float                   # Percentage of Completion (ACWP / EAC)
    recognized_revenue: Optional[float]     # Poc % * Contract Value
    contract_asset: Optional[float]         # Unbilled revenue (Recognized > Invoiced)
    contract_liability: Optional[float]     # Advance payment (Invoiced > Recognized)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result dataclass to dictionary."""
        return {
            "control_account_id": self.control_account_id,
            "control_account_name": self.control_account_name,
            "bac": self.bac,
            "bcws": self.bcws,
            "bcwp": self.bcwp,
            "acwp": self.acwp,
            "cv": self.cv,
            "sv": self.sv,
            "cpi": self.cpi,
            "spi": self.spi,
            "eac_cpi": self.eac_cpi,
            "eac_composite": self.eac_composite,
            "eac_budgeted": self.eac_budgeted,
            "etc": self.etc,
            "vac": self.vac,
            "tcpi_bac": self.tcpi_bac,
            "cost_status": self.cost_status,
            "schedule_status": self.schedule_status,
            "poc_percentage": self.poc_percentage,
            "recognized_revenue": self.recognized_revenue,
            "contract_asset": self.contract_asset,
            "contract_liability": self.contract_liability
        }


class EVMCalculator:
    """
    Deterministic EVM & IFRS 15 Engine.
    Fully unit-testable and ISO/EIA-748 compliant.
    """
    
    @staticmethod
    def calculate(inp: EVMInput, default_eac_method: EACType = EACType.CPI_BASED) -> EVMResult:
        # 1. Input Validation
        if inp.bac <= 0:
            raise ValueError(f"BAC must be greater than 0. Got {inp.bac} for CA {inp.control_account_id}")
        if inp.acwp < 0 or inp.bcwp < 0 or inp.bcws < 0:
            raise ValueError("BCWS, BCWP, and ACWP must be non-negative.")

        # 2. Variances
        cv = inp.bcwp - inp.acwp
        sv = inp.bcwp - inp.bcws

        # 3. Performance Indices (Zero-Division Safe)
        cpi = inp.bcwp / inp.acwp if inp.acwp > 0 else (1.0 if inp.bcwp == 0 else 999.0)
        spi = inp.bcwp / inp.bcws if inp.bcws > 0 else (1.0 if inp.bcwp == 0 else 999.0)

        # 4. EAC Calculations
        # A. CPI Method: BAC / CPI
        eac_cpi = inp.bac / cpi if cpi > 0 else inp.bac * 2.0
        
        # B. Composite (CPI * SPI)
        cpi_spi_product = cpi * spi
        remaining_work = max(0.0, inp.bac - inp.bcwp)
        if cpi_spi_product > 0:
            eac_composite = inp.acwp + (remaining_work / cpi_spi_product)
        else:
            eac_composite = inp.acwp + remaining_work
            
        # C. Budgeted Rate
        eac_budgeted = inp.acwp + remaining_work

        # Select primary EAC for downstream calculations
        if default_eac_method == EACType.CPI_BASED:
            primary_eac = eac_cpi
        elif default_eac_method == EACType.COMPOSITE:
            primary_eac = eac_composite
        else:
            primary_eac = eac_budgeted

        # 5. ETC & VAC
        etc = max(0.0, primary_eac - inp.acwp)
        vac = inp.bac - primary_eac

        # 6. TCPI (To-Complete Performance Index vs BAC)
        remaining_budget = inp.bac - inp.acwp
        if remaining_budget > 0:
            tcpi_bac = remaining_work / remaining_budget
        else:
            tcpi_bac = 999.0  # Target impossible if ACWP >= BAC before work completion

        # 7. Status Evaluation (2% threshold default)
        if cpi >= 1.02:
            cost_status = "UNDER_BUDGET"
        elif cpi >= 0.98:
            cost_status = "ON_BUDGET"
        else:
            cost_status = "OVER_BUDGET"

        if spi >= 1.02:
            schedule_status = "AHEAD_OF_SCHEDULE"
        elif spi >= 0.98:
            schedule_status = "ON_SCHEDULE"
        else:
            schedule_status = "BEHIND_SCHEDULE"

        # 8. IFRS 15 Cost-to-Cost Revenue Recognition
        poc_percentage = min(1.0, inp.acwp / primary_eac) if primary_eac > 0 else 0.0
        
        recognized_revenue = None
        contract_asset = None
        contract_liability = None

        if inp.contract_value is not None:
            recognized_revenue = round(inp.contract_value * poc_percentage, 2)
            if inp.invoiced_to_date is not None:
                diff = recognized_revenue - inp.invoiced_to_date
                if diff > 0:
                    contract_asset = round(diff, 2)
                    contract_liability = 0.0
                else:
                    contract_asset = 0.0
                    contract_liability = round(abs(diff), 2)

        return EVMResult(
            control_account_id=inp.control_account_id,
            control_account_name=inp.control_account_name,
            bac=round(inp.bac, 2),
            bcws=round(inp.bcws, 2),
            bcwp=round(inp.bcwp, 2),
            acwp=round(inp.acwp, 2),
            cv=round(cv, 2),
            sv=round(sv, 2),
            cpi=round(cpi, 4),
            spi=round(spi, 4),
            eac_cpi=round(eac_cpi, 2),
            eac_composite=round(eac_composite, 2),
            eac_budgeted=round(eac_budgeted, 2),
            etc=round(etc, 2),
            vac=round(vac, 2),
            tcpi_bac=round(tcpi_bac, 4),
            cost_status=cost_status,
            schedule_status=schedule_status,
            poc_percentage=round(poc_percentage * 100, 2),
            recognized_revenue=recognized_revenue,
            contract_asset=contract_asset,
            contract_liability=contract_liability
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
    print(res.to_dict())

