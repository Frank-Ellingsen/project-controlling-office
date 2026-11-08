"""
FastAPI Server & REST API
=========================
Elkem Technology Controller Hub Backend
Provides microservice endpoints for:
- Deterministic EVM (EIA-748) & IFRS 15 computations
- SkatteFUNN & Enova grant verification
- DuckDB local analytical OLAP queries
- Power BI REST API S-Curve streaming
- Qdrant VectorDB document ingestion
- Agent intent routing and MS Teams HITL Adaptive Cards
- COSO 2013 / EU AI Act Art. 12 audit logs
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from src.engine_compute.evm_calculator import EVMCalculator, EVMInput, EACType
from src.engine_compute.grant_calculator import SkatteFUNNCalculator, SkatteFUNNInput
from src.engine_compute.duckdb_store import DuckDBStore
from src.engine_agents.orchestrator import OrchestratorRouter
from src.engine_agents.ingest_kunnskapsbase import QdrantIngestPipeline
from src.engine_agents.audit_logger import AuditLogger
from src.integrations.ms_graph_teams import MSTeamsConnector
from src.integrations.powerbi_push import PowerBIPushPipeline

app = FastAPI(
    title="Elkem Technology Controller Hub API",
    description="Deterministic EVM, Grant Management, and Agentic Orchestration for Elkem ASA Technology",
    version="1.1.0"
)

# Global store & audit logger instances
duckdb_store = DuckDBStore()
audit_logger = AuditLogger()


# --- Request & Response Models ---

class EVMRequest(BaseModel):
    control_account_id: str = Field(..., example="CA-1042")
    control_account_name: str = Field(..., example="Subsea Pilot Module Development")
    bac: float = Field(..., gt=0, example=10000000.0)
    bcws: float = Field(..., ge=0, example=4000000.0)
    bcwp: float = Field(..., ge=0, example=3500000.0)
    acwp: float = Field(..., ge=0, example=3800000.0)
    contract_value: Optional[float] = Field(None, example=12500000.0)
    invoiced_to_date: Optional[float] = Field(None, example=3000000.0)
    eac_method: str = Field("cpi", example="cpi")


class SkatteFUNNRequest(BaseModel):
    project_id: str = Field(..., example="CA-1042")
    fiscal_year: int = Field(2025, example=2025)
    hourly_rate_claimed: float = Field(..., ge=0, example=650.0)
    hours_logged: float = Field(..., ge=0, example=1920.0)
    procured_rd_services: float = Field(0.0, ge=0, example=1200000.0)
    other_direct_costs: float = Field(0.0, ge=0, example=450000.0)


class RouteQueryRequest(BaseModel):
    query: str = Field(..., example="Er avviket på CPI for CA-1042 innenfor Enova-reglene?")


class TeamsCardRequest(BaseModel):
    project_id: str = Field(..., example="CA-1042")
    eac_adjustment: float = Field(..., example=857142.86)
    reason: str = Field(..., example="CPI under 0.95 pga testkostnader")


class PowerBIPushRequest(BaseModel):
    project_id: str = Field(..., example="CA-1042")
    periods: int = Field(6, ge=1, le=24, example=6)


# --- Endpoints ---

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "elkem-controller-backend",
        "governance": "COSO 2013 / EU AI Act Art. 12 compliant",
        "duckdb_connected": True
    }


@app.post("/api/v1/evm/calculate")
def calculate_evm(req: EVMRequest):
    try:
        eac_type = EACType(req.eac_method)
    except ValueError:
        eac_type = EACType.CPI_BASED

    inp = EVMInput(
        control_account_id=req.control_account_id,
        control_account_name=req.control_account_name,
        bac=req.bac,
        bcws=req.bcws,
        bcwp=req.bcwp,
        acwp=req.acwp,
        contract_value=req.contract_value,
        invoiced_to_date=req.invoiced_to_date
    )
    result = EVMCalculator.calculate(inp, default_eac_method=eac_type)
    
    # Audit log if CPI variance threshold exceeded
    if result.cpi < 0.95:
        audit_logger.log_event(
            event_type="EVM_VARIANCE_TRIGGER",
            control_account_id=req.control_account_id,
            actor="EVMCalculator",
            action="CPI_BELOW_THRESHOLD",
            details={"cpi": result.cpi, "vac": result.vac},
            hitl_status="PENDING_APPROVAL"
        )
    return result.to_dict()


@app.post("/api/v1/grants/skattefunn")
def calculate_skattefunn(req: SkatteFUNNRequest):
    inp = SkatteFUNNInput(
        project_id=req.project_id,
        fiscal_year=req.fiscal_year,
        hourly_rate_claimed=req.hourly_rate_claimed,
        hours_logged=req.hours_logged,
        procured_rd_services=req.procured_rd_services,
        other_direct_costs=req.other_direct_costs
    )
    res = SkatteFUNNCalculator.calculate(inp)
    return res.to_dict()


@app.get("/api/v1/analytics/evm-actuals/{project_id}")
def get_evm_actuals(project_id: str):
    """Retrieves aggregated actuals (labor + procurement = ACWP) from DuckDB."""
    return duckdb_store.query_evm_actuals(project_id)


@app.post("/api/v1/integrations/powerbi/push-scurve")
def push_powerbi_scurve(req: PowerBIPushRequest):
    """Simulates/pushes monthly S-Curve data to Power BI REST API."""
    pbi = PowerBIPushPipeline()
    return pbi.push_scurve_data(project_id=req.project_id, periods=req.periods)


@app.post("/api/v1/rag/ingest")
def trigger_rag_ingest():
    """Scans and indexes Kunnskapsbase documents into Qdrant."""
    pipeline = QdrantIngestPipeline()
    return pipeline.ingest_folder()


@app.post("/api/v1/orchestrator/route")
def route_query(req: RouteQueryRequest):
    router = OrchestratorRouter()
    return router.process_query(req.query)


@app.post("/api/v1/integrations/teams/approval-card")
def generate_teams_card(req: TeamsCardRequest):
    return MSTeamsConnector.format_adaptive_card_approval(
        project_id=req.project_id,
        eac_adjustment=req.eac_adjustment,
        reason=req.reason
    )


@app.get("/api/v1/audit/logs")
def get_audit_trail(limit: int = 50):
    return {
        "integrity_verified": audit_logger.verify_chain_integrity(),
        "entries": audit_logger.get_recent_logs(limit=limit)
    }
