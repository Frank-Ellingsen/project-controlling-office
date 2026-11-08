"""
Grant Compliance & Calculation Engine
=====================================
Deterministic calculation engine for Norwegian R&D tax incentives
and state aid programs (SkatteFUNN RF-1053B and Enova).

Standards & Statutory Limits:
- Skatteetaten / Forskningsrådet SkatteFUNN regulations
- Maximum recognized hourly rate: 530 NOK/hour (2025 standard)
- Maximum annual R&D hours per person: 1,850 hours
- Maximum annual eligible project costs: 25,000,000 NOK
- Tax deduction benefit rate: 19%
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class SkatteFUNNInput:
    project_id: str
    fiscal_year: int
    hourly_rate_claimed: float
    hours_logged: float
    procured_rd_services: float = 0.0  # Kjøp av FoU-tjenester fra eksterne
    other_direct_costs: float = 0.0     # Andre direkte prosjektkostnader


@dataclass
class SkatteFUNNResult:
    project_id: str
    fiscal_year: int
    
    # Input Echo
    claimed_hourly_rate: float
    claimed_hours: float
    
    # Adjusted / Approved Metrics
    approved_hourly_rate: float
    approved_hours: float
    approved_internal_labor_cost: float
    approved_procured_services: float
    approved_other_direct_costs: float
    
    # Total Basis & Benefit
    total_eligible_cost_basis: float
    tax_deduction_amount: float        # 19% of total eligible cost basis
    capped_by_max_limit: bool          # True if total > 25M NOK
    
    # Audit Flags
    hourly_rate_exceeded: bool
    hours_exceeded: bool
    audit_notes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "fiscal_year": self.fiscal_year,
            "claimed_hourly_rate": self.claimed_hourly_rate,
            "claimed_hours": self.claimed_hours,
            "approved_hourly_rate": self.approved_hourly_rate,
            "approved_hours": self.approved_hours,
            "approved_internal_labor_cost": self.approved_internal_labor_cost,
            "approved_procured_services": self.approved_procured_services,
            "approved_other_direct_costs": self.approved_other_direct_costs,
            "total_eligible_cost_basis": self.total_eligible_cost_basis,
            "tax_deduction_amount": self.tax_deduction_amount,
            "capped_by_max_limit": self.capped_by_max_limit,
            "hourly_rate_exceeded": self.hourly_rate_exceeded,
            "hours_exceeded": self.hours_exceeded,
            "audit_notes": self.audit_notes,
        }


class SkatteFUNNCalculator:
    """
    Computes eligible costs and tax credit according to Norwegian SkatteFUNN regulations.
    """
    MAX_HOURLY_RATE = 530.0    # NOK / hour
    MAX_HOURS_PER_PERSON = 1850.0  # Hours / year
    MAX_ANNUAL_CAP = 25000000.0   # 25M NOK total cost ceiling
    TAX_CREDIT_RATE = 0.19     # 19% tax credit

    @classmethod
    def calculate(cls, inp: SkatteFUNNInput) -> SkatteFUNNResult:
        if inp.hours_logged < 0 or inp.hourly_rate_claimed < 0:
            raise ValueError("Hours and hourly rates must be non-negative.")

        audit_notes: List[str] = []
        
        # 1. Check & Cap Hourly Rate
        if inp.hourly_rate_claimed > cls.MAX_HOURLY_RATE:
            approved_rate = cls.MAX_HOURLY_RATE
            rate_exceeded = True
            audit_notes.append(
                f"Avkortet timesats fra {inp.hourly_rate_claimed:.2f} kr til maks lovlig {cls.MAX_HOURLY_RATE:.2f} kr/t."
            )
        else:
            approved_rate = inp.hourly_rate_claimed
            rate_exceeded = False

        # 2. Check & Cap Hours
        if inp.hours_logged > cls.MAX_HOURS_PER_PERSON:
            approved_hours = cls.MAX_HOURS_PER_PERSON
            hours_exceeded = True
            audit_notes.append(
                f"Avkortet timer fra {inp.hours_logged:.1f} timer til maksimalt {cls.MAX_HOURS_PER_PERSON:.1f} timer pr år."
            )
        else:
            approved_hours = inp.hours_logged
            hours_exceeded = False

        # 3. Calculate Cost Basis
        approved_internal_labor = approved_rate * approved_hours
        subtotal = approved_internal_labor + inp.procured_rd_services + inp.other_direct_costs

        # 4. Check Annual Cost Cap (25M NOK)
        if subtotal > cls.MAX_ANNUAL_CAP:
            total_eligible_basis = cls.MAX_ANNUAL_CAP
            capped_max = True
            audit_notes.append(
                f"Total kostnadsbase overskrider taket på {cls.MAX_ANNUAL_CAP:,.0f} NOK; avkortet."
            )
        else:
            total_eligible_basis = subtotal
            capped_max = False

        # 5. Calculate 19% Tax Credit
        tax_deduction = round(total_eligible_basis * cls.TAX_CREDIT_RATE, 2)

        return SkatteFUNNResult(
            project_id=inp.project_id,
            fiscal_year=inp.fiscal_year,
            claimed_hourly_rate=inp.hourly_rate_claimed,
            claimed_hours=inp.hours_logged,
            approved_hourly_rate=approved_rate,
            approved_hours=approved_hours,
            approved_internal_labor_cost=round(approved_internal_labor, 2),
            approved_procured_services=round(inp.procured_rd_services, 2),
            approved_other_direct_costs=round(inp.other_direct_costs, 2),
            total_eligible_cost_basis=round(total_eligible_basis, 2),
            tax_deduction_amount=tax_deduction,
            capped_by_max_limit=capped_max,
            hourly_rate_exceeded=rate_exceeded,
            hours_exceeded=hours_exceeded,
            audit_notes=audit_notes,
        )
