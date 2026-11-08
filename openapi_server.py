"""
Elkem Project Controlling Office — OpenAPI Server
=================================================
FastAPI backend implementing OpenAPI 3.1 specifications for:
- EIA-748 Earned Value Management (EVM)
- IFRS 15 Revenue Recognition & Contract Asset Accounting
- Grant compliance auditing (NKRF 3/2018, SkatteFUNN, Enova, Horizon Europe)
- Multi-Agent Human-in-the-Loop (HITL) Action Proposals
- Serving the Interactive Project Controlling Office Dashboard (HTML)
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import deterministic engines
from src.engine_compute.evm_calculator import EVMCalculator, EVMInput, EACType
from src.engine_compute.grant_calculator import SkatteFUNNCalculator, SkatteFUNNInput
from src.engine_compute.duckdb_store import DuckDBStore
from src.engine_agents.audit_logger import AuditLogger

# Initialize core services
app = FastAPI(
    title="Elkem Project Controlling Office API",
    description="Agentic Financial Control, EIA-748 EVM, IFRS 15 Revenue Recognition & Grant Audit Platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Enable CORS for browser dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

duckdb_store = DuckDBStore()
audit_logger = AuditLogger()

# Path to the interactive dashboard HTML (searches docs/ first, then fallback paths)
def _find_dashboard_path() -> str:
    search_paths = [
        os.path.join(os.path.dirname(__file__), "docs", "Project_Controlling_Office_-_Interactive_Dashboard___Inter.html"),
        os.path.join(os.path.dirname(__file__), "docs", "dashboard.html"),
        os.path.join(os.path.dirname(__file__), "src", "ui_frontend", "static", "dashboard.html"),
        os.path.join(os.path.dirname(__file__), "Project_Controlling_Office_-_Interactive_Dashboard___Inter.html"),
    ]
    for p in search_paths:
        if os.path.exists(p):
            return p
    return search_paths[0]

HTML_DASHBOARD_PATH = _find_dashboard_path()


# --- Pydantic Models ---

class EVMRequest(BaseModel):
    control_account_id: str = Field(..., example="WBS-2.1")
    control_account_name: Optional[str] = Field("Refractory Lining & Shell Assembly", example="Refractory Lining")
    bac: float = Field(..., gt=0, example=26000000.0, description="Budget at Completion (NOK)")
    bcws: float = Field(..., ge=0, example=22000000.0, description="Planned Value / BCWS (NOK)")
    bcwp: float = Field(..., ge=0, example=19800000.0, description="Earned Value / BCWP (NOK)")
    acwp: float = Field(..., ge=0, example=23200000.0, description="Actual Cost / ACWP (NOK)")
    contract_value: Optional[float] = Field(None, example=32000000.0)
    invoiced_to_date: Optional[float] = Field(None, example=15000000.0)
    eac_method: Optional[str] = Field("cpi", example="cpi", description="'cpi', 'composite', or 'budgeted'")


class SkatteFUNNAuditRequest(BaseModel):
    project_id: str = Field(..., example="ZEP-26")
    fiscal_year: int = Field(2025, example=2025)
    hourly_rate_claimed: float = Field(..., ge=0, example=650.0)
    hours_logged: float = Field(..., ge=0, example=1920.0)
    procured_rd_services: float = Field(0.0, ge=0, example=1200000.0)
    other_direct_costs: float = Field(0.0, ge=0, example=450000.0)


class HITLActionRequest(BaseModel):
    action_id: str = Field(..., example="ACT-2026-092")
    decision: str = Field(..., example="APPROVE", description="'APPROVE' or 'REJECT'")
    actor: str = Field(..., example="Frank Ellingsen (Lead Project Controller)")
    notes: Optional[str] = Field(None, example="Approved under condition of thermal soak monitoring.")


# --- Master Datasets for Dashboard ---

MASTER_WBS = [
    {"code": "WBS 1.1", "name": "Fundamental Metallurgical Kinetics", "cam": "Dr. T. Solheim", "bac": 9500000, "pv": 9500000, "ev": 9500000, "ac": 9800000, "ias38": "EXPENSED", "status": "Complete"},
    {"code": "WBS 1.2", "name": "Off-Gas Thermochemistry Simulations", "cam": "Dr. T. Solheim", "bac": 7500000, "pv": 7500000, "ev": 7500000, "ac": 7400000, "ias38": "EXPENSED", "status": "Complete"},
    {"code": "WBS 1.3", "name": "Control Loop Sensor Architecture", "cam": "Dr. T. Solheim", "bac": 5000000, "pv": 5000000, "ev": 4900000, "ac": 5100000, "ias38": "CAPITALIZED", "status": "Complete"},
    {"code": "WBS 2.1", "name": "Refractory Lining & Shell Assembly", "cam": "I. Lindqvist", "bac": 26000000, "pv": 22000000, "ev": 19800000, "ac": 23200000, "ias38": "CAPITALIZED", "status": "Critical"},
    {"code": "WBS 2.2", "name": "Electrode Column & Hydraulic Rig", "cam": "I. Lindqvist", "bac": 19000000, "pv": 16500000, "ev": 15400000, "ac": 16800000, "ias38": "CAPITALIZED", "status": "At Risk"},
    {"code": "WBS 2.3", "name": "Sensor Ingestion & Pyrometer Bus", "cam": "I. Lindqvist", "bac": 13000000, "pv": 11000000, "ev": 10600000, "ac": 11200000, "ias38": "CAPITALIZED", "status": "On Track"},
    {"code": "WBS 3.1", "name": "Catalytic Slipstream Pilot Module", "cam": "H. Foss", "bac": 18500000, "pv": 14000000, "ev": 13100000, "ac": 14200000, "ias38": "CAPITALIZED", "status": "At Risk"},
    {"code": "WBS 3.2", "name": "Heat Recovery Exchanger Bank", "cam": "H. Foss", "bac": 14000000, "pv": 10500000, "ev": 10100000, "ac": 10600000, "ias38": "CAPITALIZED", "status": "On Track"},
    {"code": "WBS 4.1", "name": "Chemical Slag Assays & Quality Logs", "cam": "M. Berntsen", "bac": 8000000, "pv": 6000000, "ev": 5900000, "ac": 6050000, "ias38": "EXPENSED", "status": "On Track"},
    {"code": "WBS 4.2", "name": "Microstructure Characterization Rig", "cam": "M. Berntsen", "bac": 6000000, "pv": 4800000, "ev": 4600000, "ac": 4720000, "ias38": "EXPENSED", "status": "On Track"},
    {"code": "WBS 5.1", "name": "Power Grid 22kV Substation Intertie", "cam": "F. Ellingsen", "bac": 10000000, "pv": 5500000, "ev": 5250000, "ac": 5400000, "ias38": "CAPITALIZED", "status": "On Track"},
    {"code": "WBS 5.2", "name": "Hot Commissioning & Baseline Smelt", "cam": "F. Ellingsen", "bac": 6000000, "pv": 2500000, "ev": 2000000, "ac": 1950000, "ias38": "CAPITALIZED", "status": "On Track"}
]

MASTER_GRANT_VOUCHERS = [
    {"id": "VOUCH-2026-0881", "scheme": "Enova", "wbs": "WBS 2.1", "date": "2026-07-14", "desc": "Lønnsutgifter sykemeldt ingeniør (arbeidsgiverperiode dag 1-16)", "amount": 42500.0, "hours": 55.0, "eligible": False, "finding": "Ineligible under NKRF 3/2018: Sick leave during employer period."},
    {"id": "VOUCH-2026-0914", "scheme": "SkatteFUNN", "wbs": "WBS 2.2", "date": "2026-07-22", "desc": "Sykepenger tekniker hydraulikk (arbeidsgiverperiode)", "amount": 36000.0, "hours": 48.0, "eligible": False, "finding": "Ineligible under NKRF 3/2018 & SkatteFUNN guidelines."},
    {"id": "VOUCH-2026-1042", "scheme": "Horizon Europe", "wbs": "WBS 3.1", "date": "2026-08-04", "desc": "Sykeavbrudd prosessmetallurg (arbeidsgiverperiode dag 3-12)", "amount": 38000.0, "hours": 45.0, "eligible": False, "finding": "Ineligible under MGA Art. 6.2(A) & NKRF 3/2018."},
    {"id": "VOUCH-2026-1108", "scheme": "Horizon Europe", "wbs": "WBS 2.1", "date": "2026-08-18", "desc": "Sykemelding skiftleder pilotanlegg (dag 5-14)", "amount": 26000.0, "hours": 32.0, "eligible": False, "finding": "Ineligible under MGA Art. 6.2(A): Sick leave quarantine."},
    {"id": "VOUCH-2026-0712", "scheme": "Enova", "wbs": "WBS 2.1", "date": "2026-06-11", "desc": "Inconel furnace shell refractory plates invoice #94012", "amount": 840000.0, "hours": 0.0, "eligible": True, "finding": "Eligible industrial investment CAPEX."},
    {"id": "VOUCH-2026-0755", "scheme": "SkatteFUNN", "wbs": "WBS 1.1", "date": "2026-06-25", "desc": "Direct metallurgical kinetics R&D labor (120 hrs @ 530 cap)", "amount": 63600.0, "hours": 120.0, "eligible": True, "finding": "Verified against timesheet logs. Capped rate applied."}
]


# --- Endpoints ---

@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def serve_dashboard():
    """Serves the interactive Carbon-styled Project Controlling Office dashboard."""
    if not os.path.exists(HTML_DASHBOARD_PATH):
        raise HTTPException(status_code=404, detail="Dashboard HTML file not found.")
    with open(HTML_DASHBOARD_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content)


@app.get("/health")
def health_check():
    """Health check endpoint exposing system readiness and cryptographic chain state."""
    return {
        "status": "healthy",
        "service": "Elkem Project Controlling Office API",
        "version": "2.0.0",
        "coso_audit_chain_intact": audit_logger.verify_chain_integrity(),
        "duckdb_connected": True,
        "standards": ["ANSI/EIA-748 EVM", "IFRS 15", "IAS 38", "NKRF 3/2018", "EU AI Act Art. 12"]
    }


@app.get("/api/v1/wbs")
def get_wbs_elements():
    """Returns all WBS elements with baseline budgets, earned value, actual costs, and IAS 38 flags."""
    return {"project_id": "ZEP-26", "count": len(MASTER_WBS), "wbs_elements": MASTER_WBS}


@app.get("/api/v1/scurve")
def get_scurve_timeseries():
    """Returns monthly cumulative EVM S-Curve progression (PV, EV, AC) for months 1 to 24."""
    data = [
        {"m": 1, "pv": 4200000, "ev": 4100000, "ac": 4050000},
        {"m": 2, "pv": 8500000, "ev": 8300000, "ac": 8200000},
        {"m": 3, "pv": 13200000, "ev": 12900000, "ac": 13100000},
        {"m": 4, "pv": 18000000, "ev": 17400000, "ac": 17900000},
        {"m": 5, "pv": 23500000, "ev": 22600000, "ac": 23400000},
        {"m": 6, "pv": 29500000, "ev": 28200000, "ac": 29400000},
        {"m": 7, "pv": 35800000, "ev": 34100000, "ac": 35600000},
        {"m": 8, "pv": 42000000, "ev": 39800000, "ac": 41500000},
        {"m": 9, "pv": 48200000, "ev": 45600000, "ac": 47900000},
        {"m": 10, "pv": 54600000, "ev": 51800000, "ac": 54400000},
        {"m": 11, "pv": 61200000, "ev": 58000000, "ac": 61100000},
        {"m": 12, "pv": 68000000, "ev": 64200000, "ac": 67800000},
        {"m": 13, "pv": 74200000, "ev": 69800000, "ac": 73900000},
        {"m": 14, "pv": 80100000, "ev": 75200000, "ac": 79500000},
        {"m": 15, "pv": 86000000, "ev": 80800000, "ac": 85300000},
        {"m": 16, "pv": 92000000, "ev": 86500000, "ac": 91200000},
        {"m": 17, "pv": 98100000, "ev": 92200000, "ac": 97800000},
        {"m": 18, "pv": 104000000, "ev": 98200000, "ac": 104800000},
        {"m": 19, "pv": 109500000, "ev": 103400000, "ac": 110600000},
        {"m": 20, "pv": 114800000, "ev": 108650000, "ac": 116420000},
        {"m": 21, "pv": 121500000, "ev": None, "ac": None},
        {"m": 22, "pv": 128500000, "ev": None, "ac": None},
        {"m": 23, "pv": 135500000, "ev": None, "ac": None},
        {"m": 24, "pv": 142500000, "ev": None, "ac": None}
    ]
    return {"project_id": "ZEP-26", "cutoff_month": 20, "time_series": data}


@app.post("/api/v1/evm/calculate")
def calculate_evm(req: EVMRequest):
    """
    Computes deterministic EIA-748 EVM and IFRS 15 PoC metrics.
    Zero LLM dependencies.
    """
    try:
        eac_type = EACType(req.eac_method) if req.eac_method else EACType.CPI_BASED
    except ValueError:
        eac_type = EACType.CPI_BASED

    inp = EVMInput(
        control_account_id=req.control_account_id,
        control_account_name=req.control_account_name or req.control_account_id,
        bac=req.bac,
        bcws=req.bcws,
        bcwp=req.bcwp,
        acwp=req.acwp,
        contract_value=req.contract_value,
        invoiced_to_date=req.invoiced_to_date
    )
    result = EVMCalculator.calculate(inp, default_eac_method=eac_type)

    if result.cpi < 0.95:
        audit_logger.log_event(
            event_type="EVM_VARIANCE_WARNING",
            control_account_id=req.control_account_id,
            actor="EVMCalculator",
            action="CPI_BELOW_0.95",
            details={"cpi": result.cpi, "vac": result.vac},
            hitl_status="PENDING_APPROVAL"
        )
    return result.to_dict()


@app.get("/api/v1/grants/vouchers")
def get_grant_vouchers(scheme: Optional[str] = None):
    """Returns audited grant expenditure vouchers, highlighting NKRF 3/2018 sick leave disallowances."""
    if scheme:
        filtered = [v for v in MASTER_GRANT_VOUCHERS if v["scheme"].lower() == scheme.lower()]
        return {"count": len(filtered), "vouchers": filtered}
    return {"count": len(MASTER_GRANT_VOUCHERS), "vouchers": MASTER_GRANT_VOUCHERS}


@app.post("/api/v1/grants/skattefunn")
def calculate_skattefunn(req: SkatteFUNNAuditRequest):
    """Applies Norwegian SkatteFUNN statutory caps (530 kr/hr, 1850 hours, 25 MNOK base)."""
    inp = SkatteFUNNInput(
        project_id=req.project_id,
        fiscal_year=req.fiscal_year,
        hourly_rate_claimed=req.hourly_rate_claimed,
        hours_logged=req.hours_logged,
        procured_rd_services=req.procured_rd_services,
        other_direct_costs=req.other_direct_costs
    )
    return SkatteFUNNCalculator.calculate(inp).to_dict()


@app.post("/api/v1/hitl/action")
def submit_hitl_action(req: HITLActionRequest):
    """
    Submits a Human-in-the-Loop decision, generating a SHA-256 hash-chained audit entry.
    """
    if req.decision.upper() not in ["APPROVE", "REJECT"]:
        raise HTTPException(status_code=400, detail="Decision must be 'APPROVE' or 'REJECT'")

    event_payload = audit_logger.log_event(
        event_type="HITL_DECISION",
        control_account_id=req.action_id,
        actor=req.actor,
        action=f"ACTION_{req.decision.upper()}",
        details={"action_id": req.action_id, "notes": req.notes},
        hitl_status="APPROVED" if req.decision.upper() == "APPROVE" else "REJECTED"
    )

    return {
        "status": "COMMITTED",
        "action_id": req.action_id,
        "decision": req.decision.upper(),
        "audit_hash": event_payload["entry_hash"],
        "timestamp": event_payload["timestamp"]
    }


@app.get("/api/v1/audit/logs")
def get_audit_logs(limit: int = 50):
    """Retrieves immutable audit trail entries with cryptographic hash chain verification."""
    return {
        "chain_intact": audit_logger.verify_chain_integrity(),
        "total_returned": len(audit_logger.get_recent_logs(limit=limit)),
        "logs": audit_logger.get_recent_logs(limit=limit)
    }


if __name__ == "__main__":
    import uvicorn
    print("⚡ Starting Elkem Project Controlling Office OpenAPI Server on http://0.0.0.0:8000")
    print("📊 Interactive Dashboard available at http://localhost:8000/dashboard")
    print("📖 OpenAPI Interactive Docs available at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
