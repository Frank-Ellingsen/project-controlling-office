# Elkem Controller Hub — Dual-Engine Financial Control & Project Reporting Framework

> **Agentic Financial Control, Earned Value Management (EVM), and IFRS 15 Compliance Framework for Elkem ASA Technology (Fiskå, Kristiansand).**

---

## 📌 Executive Overview

**Elkem Controller Hub** er et dual-engine prosjektstyringssystem utviklet for å forene **strenge regnskaps- og tilskuddsregler** (EIA-748 EVM, IFRS 15, SkatteFUNN RF-1053B, Enova) med **agentisk AI-automatisering**.

Systemet er skreddersydd for rammebetingelsene til **Elkem ASA Technology** på Fiskå i Kristiansand, og automatiserer månedsoppgjør, avviksanalyser, tilskuddsrapportering og ledelsesprognoser (EAC/S-kurver) uten risiko for regnefeil eller datalekkasje.

---

## 🏗️ Dual-Engine Arkitektur

```
                     +-------------------------------------------------+
                     |            ELKEM CONTROLLER HUB UI              |
                     |  (Streamlit Dashboard  /  FastAPI Swagger UI)   |
                     +-------------------------------------------------+
                                              |
                     +------------------------+------------------------+
                     |                                                 |
                     v                                                 v
   +------------------------------------+   +------------------------------------+
   |     ENGINE 1: DETERMINISTIC        |   |      ENGINE 2: AGENTIC RAG         |
   |        COMPUTE ENGINE              |   |       ORCHESTRATION ENGINE         |
   +------------------------------------+   +------------------------------------+
   | * EIA-748 EVM Beregninger (FAST)   |   | * Hybrid Intent Router             |
   | * IFRS 15 PoC & Inntektsføring     |   | * Lokal Ollama (llama3.1)          |
   | * SkatteFUNN Sjablong (530 kr/t)   |   | * Qdrant Vector DB (nomic-embed)   |
   | * DuckDB OLAP Transaksjonslager    |   | * Gemini 3.8 Flash Multimodal OCR  |
   +------------------------------------+   +------------------------------------+
                     |                                                 |
                     +------------------------+------------------------+
                                              |
                                              v
                     +-------------------------------------------------+
                     |         GOVERNANCE & INTEGRATION LAYER          |
                     |  * HITL Tollbooth (COSO 2013 / EU AI Act)       |
                     |  * Power BI REST API S-Curve Streaming          |
                     |  * MS Teams Adaptive Cards & Brreg Registry     |
                     +-------------------------------------------------+
```

### 🧮 Engine 1: Deterministisk Beregningsmotor
* **EIA-748 EVM Måltall**: Ren Python-matematikk for Planlagt verdi (BCWS / PV), Opptjent verdi (BCWP / EV), Faktisk kostnad (ACWP / AC), Cost Variance (CV), Schedule Variance (SV), CPI, SPI og Estimate at Completion (EAC).
* **IFRS 15 Inntektsføring**: PoC % (Percentage of Completion) over-tid inntektsføring, beregning av Contract Assets (Påløpt, ikke-fakturert inntekt) og avsetninger.
* **DuckDB Transaksjons-OLAP**: Lokal SQL-database (`data/elkem_analytics.duckdb`) som lagrer ERP-transaksjoner på laveste bilagsnivå (timeføringer, innkjøp, underleverandører og WBS-struktur).
* **Tilskuddskontroll**: Automatisk validering mot SkatteFUNN-sjablong (RF-1053B timesatsgrense på maks 530 kr/t og 1 850 t/år per person) og Enova-retningslinjer.

### 🤖 Engine 2: Agentisk RAG- & Orkestreringsmotor
* **Hybrid Router**: Klassifiserer brukerhenvendelser automatisk til enten SQL/EVM-beregninger, Qdrant Vector RAG-oppslag eller hybride samsvarsanalyser.
* **100% Lokal LLM & Vektorer**: Kjører **Ollama (llama3.1)** for privat resonnering og **nomic-embed-text** via Qdrant for dokumentoppslag.
* **Multimodal OCR**: Bruker Gemini 3.8 Flash for rask analyse av sammensatte PDF-fakturaer, tekniske bilag og tilskuddsbrev.

---

## 🔒 Governance, Sikkerhet & Human-in-the-Loop (HITL)

* **Air-Gapped Datasikkerhet**: Konfidensielle FoU-dokumenter og regnskapstall behandles utelukkende lokalt på localhost.
* **COSO 2013 & EU AI Act Compliance**: Innebygget **Human-in-the-Loop (HITL) Tollbooth**. AI-agenter kan ikke endre tall i ERP/SAP uten eksplisitt godkjenning fra controller via et knappetrykk.
* **Uforanderlig Audit-Logg**: Alle godkjenninger og EAC-prognoseendringer tildeles en kryptografisk UUID i `data/audit_logs/` for revisorgodkjenning (ISA 805 / ISAE 3000).

---

## 📁 Prosjektstruktur

```
project-controlling-office/
├── docker-compose.yml              # Multi-container oppsett (Backend, Frontend, Qdrant)
├── Dockerfile.backend              # Python 3.12 FastAPI microservice container
├── Dockerfile.frontend             # Streamlit UI dashboard container
├── .env.example                    # Mal for miljøvariabler og API-nøkler
├── .gitignore                      # Sikkerhetsskjold for nøkler og DuckDB-filer
├── scripts/
│   └── bootstrap_dev.py            # Automatisk oppstartsskript for dev-miljø
├── src/
│   ├── engine_compute/
│   │   ├── evm_calculator.py       # Deterministisk EVM & IFRS 15 beregningsmotor
│   │   └── duckdb_store.py         # DuckDB OLAP transaksjonsdatabase
│   ├── rag_pipeline/
│   │   ├── llm_provider.py         # Modellstyring (Ollama / Gemini / Serper)
│   │   ├── orchestrator.py         # Multi-agent router og eksekveringsplanlegger
│   │   └── ingest_kunnskapsbase.py # Qdrant vektoringesting for Elkem Kunnskapsbase
│   ├── integrations/
│   │   ├── openapi_server.py       # FastAPI REST-server med Swagger UI & ReDoc
│   │   ├── ms_graph_teams.py       # MS Teams Adaptive Cards kobling
│   │   ├── norwegian_public_apis.py# Brreg & SkatteFUNN API-integrasjoner
│   │   ├── powerbi_push.py         # Power BI REST API S-kurve strømmingsmotor
│   │   └── generate_deck.py        # PowerPoint ledelsespresentasjon (.pptx)
│   └── ui_frontend/
│       ├── app.py                  # Streamlit dashboard (v1)
│       └── app-v2.py               # Elkem Navy branded Streamlit dashboard (v2)
└── tests/
    └── test_llm_provider.py        # Enhetstester (43/43 bestått)
```

---

## ⚡ Hurtigstart & Installasjon

### 1. Forutsetninger
* **Python 3.12+**
* **Docker Desktop** (med Docker Compose)
* **Ollama** (installert lokalt med `ollama pull llama3.1` og `ollama pull nomic-embed-text`)

### 2. Klon og Konfigurer
```bash
git clone project-controlling-office
cd project-controlling-office
cp .env.example .env
```

### 3. Bygg Lokal Database
```bash
python scripts/bootstrap_dev.py
```

### 4. Start Containerne
```bash
docker compose up --build
```

---

## 🧪 Kjøring av Enhetstester

Kjør hele testpakken for å verifisere beregninger og integrasjoner:
```bash
python -m unittest discover -s tests -p "test_*.py"
```
*Status*: `OK (43 av 43 bestått)`

---

## 📊 Realistiske Elkem ASA Technology Prosjektdata

Systemet leveres pre-konfigurert med tre representative pilot- og FoU-prosjekter fra Elkem sin virksomhet på Fiskå:

| Control Account | Domene | Tilskuddspartner | BAC (NOK) | CPI | SPI | IFRS 15 Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **CA-2045** | Fiskå Carbon-Neutral Smelting Pilot | Enova | 45 000 000 | 0.8974 | 0.9333 | PoC 46.7% (Contract Asset: 5.33 MNOK) |
| **CA-1042** | Furnace Automation & Digital Twin | NFR | 10 000 000 | 0.9211 | 0.8750 | PoC 35.0% (Contract Asset: 1.38 MNOK) |
| **CA-3080** | NextGen Battery Anode Material | SkatteFUNN (#298412) | 15 000 000 | 1.0380 | 1.0250 | PoC 54.7% (Skattefradrag: 1.50 MNOK) |

---

## 📄 Lisens & Opphavsrett

Utviklet av **Frank Ellingsen** for **Elkem ASA Technology Controller Hub**.
Beskyttet under Elkem sine standard retningslinjer for virksomhetsstyring.
