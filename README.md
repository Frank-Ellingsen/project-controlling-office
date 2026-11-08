# ⚡ Elkem Technology Controller Hub (`project-controlling-office`)

> **Agentic Governance, Earned Value Management (EIA-748), IFRS 15 Revenue Control & Grant Management Workstation for Elkem ASA Technology (Fiskaa).**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B.svg)](https://streamlit.io)
[![DuckDB](https://img.shields.io/badge/DuckDB-OLAP-FFF000.svg)](https://duckdb.org)
[![Governance](https://img.shields.io/badge/COSO%202013-EU%20AI%20Act%20Art.%2012-emerald.svg)]()
[![Tests](https://img.shields.io/badge/tests-43%20passed-brightgreen.svg)]()

---

## 🏛️ Core Architectural Axiom

```
   Models Reason. Software Computes. Agents Orchestrate. Systems Verify.
```

Financial calculations must **never** be subject to LLM math hallucinations. In this hub:
* **Deterministic Compute Engine (Python / SQL)** handles 100% of the mathematical, financial, and tax credit formulas.
* **LLM / Multi-Agent Layer (Ollama / Gemini)** is strictly restricted to semantic classification, unstructured regulatory lookup (RAG), and prescriptive commentary.
* **Local-First Analytical Storage (DuckDB)** provides sub-second OLAP rollups over WBS nodes, timecards, and procurement actuals without cloud egress costs.
* **Cryptographic Audit Trail (COSO 2013 & EU AI Act Art. 12)** enforces SHA-256 hash chaining on all model outputs and Human-in-the-Loop (HITL) approvals.

---

## 🌟 Key Capabilities

### 1. Earned Value Management (EIA-748) & FAST Standard
* Calculates Planned Value ($BCWS$), Earned Value ($BCWP$), Actual Cost ($ACWP$), Cost Variance ($CV$), Schedule Variance ($SV$), $CPI$, and $SPI$.
* Forecasts Estimate at Completion ($EAC$) across multiple methods (CPI-based, Composite $CPI \times SPI$, Budgeted Rate).
* Evaluates Variance at Completion ($VAC$) and To-Complete Performance Index ($TCPI$).

### 2. IFRS 15 (Revenue from Contracts with Customers)
* Implements the **Cost-to-Cost Percentage of Completion (PoC %)** input method: $\text{PoC} = \frac{ACWP}{EAC}$.
* Calculates cumulative recognized revenue against milestone billing.
* Automatically balances **Contract Assets** (unbilled revenue) vs **Contract Liabilities** (advance payments).

### 3. Grant Compliance (SkatteFUNN RF-1053B & Enova)
* Statutory capping of internal R&D hourly rates to **530 NOK/hour** (2025 standard).
* Maximum cap of **1,850 hours/year** per employee.
* Annual cost ceiling of **25,000,000 NOK** per company with 19% tax credit computation.
* Pre-submission audit check flagging non-compliant time registrations for ISA 805 / ISAE 3000 audit readiness.

### 4. Local-First DuckDB OLAP Engine
* High-performance SQL engine joining WBS nodes, employee timecards, and purchase orders.
* Eliminates Cartesian fan-out using CTE-based multi-fact aggregation to compute mathematically exact actuals ($ACWP$).

### 5. Power BI REST API Push Pipeline
* Real-time streaming of cumulative S-Curve time series ($PV$, $EV$, $AC$) directly into Power BI Push Datasets for corporate dashboards.

### 6. Edward Tufte Data-Ink Executive UI
* Minimalist Streamlit workstation UI.
* Zero vertical gridlines, muted base colors, direct S-Curve line labeling (no separate legends), and alert highlights only when $CPI < 0.95$.
* Interactive Human-in-the-Loop (HITL) tollbooth gate requiring controller sign-off before committing EAC changes to ERP (SAP / Agresso).

---

## 📂 Repository Structure

```
project-controlling-office/
├── src/
│   ├── engine_compute/             # Deterministic financial math (FAST standard, 0 LLM)
│   │   ├── evm_calculator.py       # EIA-748 EVM & IFRS 15 PoC formulas
│   │   ├── grant_calculator.py     # SkatteFUNN RF-1053B & Enova statutory rules
│   │   └── duckdb_store.py         # Local DuckDB OLAP schema & CTE aggregations
│   ├── engine_agents/              # Agentic orchestration & governance
│   │   ├── orchestrator.py         # Dual-mode intent router (Structured vs RAG vs Hybrid)
│   │   ├── llm_provider.py         # Model manager (Ollama llama3.1, Gemini 3.8 Flash)
│   │   ├── ingest_kunnskapsbase.py # Qdrant vector ingestion for regulatory PDFs
│   │   └── audit_logger.py         # COSO 2013 / EU AI Act Art. 12 SHA-256 audit logger
│   ├── integrations/               # Ecosystem connectors
│   │   ├── ms_graph_teams.py       # Teams Adaptive Cards & PowerPoint decks
│   │   ├── powerbi_push.py         # Power BI REST API S-Curve streaming
│   │   └── norwegian_public_apis.py# Brønnøysundregistrene (Brreg) & Grant APIs
│   ├── ui_frontend/                # Streamlit Executive Workstation
│   │   └── app.py                  # Tufte-style Split-View UI & HITL Tollbooth
│   ├── api/                        # FastAPI microservice
│   │   └── main.py                 # REST endpoints for EVM, grants, actuals & logs
│   └── main.py                     # Uvicorn entrypoint for Docker
├── tests/                          # 43 unit and integration tests (100% pass rate)
├── data/
│   ├── sample_data/                # Control accounts sample datasets (JSON)
│   └── audit_logs/                 # Cryptographically chained audit trail (JSONL)
├── scripts/
│   └── bootstrap_dev.py            # Development environment initialization script
├── .streamlit/
│   └── config.toml                 # Elkem corporate theme configuration
├── Dockerfile.backend              # FastAPI Docker container
├── Dockerfile.frontend             # Streamlit Docker container
├── docker-compose.yml              # Container orchestration (Backend + Frontend + Qdrant)
└── requirements.txt                # Python dependencies
```

---

## 🚀 Quickstart

### 1. Prerequisites
* Python 3.12+ (or 3.14)
* (Optional) Docker Desktop
* (Optional) Local [Ollama](https://ollama.com) running `llama3.1` and `nomic-embed-text`

### 2. Bootstrap Environment
```powershell
# Clone the repository
git clone https://github.com/Frank-Ellingsen/project-controlling-office.git
cd project-controlling-office

# Install dependencies
pip install -r requirements.txt

# Run bootstrap initializer (creates .env and seeds DuckDB)
python scripts/bootstrap_dev.py
```

### 3. Run Automated Test Suite
```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```
*43 tests covering EVM math, IFRS 15, statutory grants, DuckDB CTE joins, and API endpoints.*

### 4. Launch Executive Workstation
```powershell
streamlit run app.py
```
*Open [http://localhost:8501](http://localhost:8501) in your browser.*

### 5. Launch via Docker Compose
```powershell
docker compose up --build
```
* Access Workstation UI: [http://localhost:8501](http://localhost:8501)
* Access FastAPI Interactive Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔒 Governance & Regulatory Compliance

* **COSO 2013 Internal Controls**: Segregation of duties enforced through mandatory Human-in-the-Loop (HITL) approval cards before committing adjustments.
* **EU AI Act (Article 12 - High-Risk AI)**: Every prompt route, heuristic rule, and financial metric modification is logged with timestamp, user, previous value, proposed value, and a cryptographic SHA-256 hash pointer linking to the preceding entry.
* **Audit Verification**: Run `audit_logger.verify_chain_integrity()` or call `GET /api/v1/audit/logs` to cryptographically prove that no historical records have been altered.

---

## 👤 Author
**Frank Ellingsen**  
*Financial Controller / BI Specialist & Project Controller*  
*Specializing in Project Controlling, EIA-748 EVM, and Agentic AI Architecture for Engineering and Maritime Sectors.*

