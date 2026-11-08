# Executive Briefing: Elkem Technology Controller Hub

**Til:** Financial Manager & Ledelsen i Elkem ASA Technology  
**Fra:** Frank Ellingsen, Lead Project Controller / Prosjektøkonom  
**Dato:** November 2026  
**Emne:** Strategisk Rammeverk for Digitalisering, Prosjektstyring og Agentisk AI i Elkem Technology Controller Hub  

---

## 1. Strategisk Visjon og Verdivurdering

Elkem ASA Technology på Fiskaa forvalter konsernets mest kritiske FoU-prosjekter, pilotanlegg og industrielle teknologi-initiativer. Tradisjonell prosjektoppfølging preges ofte av manuelle prosesser, reaktiv avvikshåndtering ved månedsoppgjør og tunge Excel-modeller.

Dette initiativet transformerer økonomicontrolleren fra reaktiv bilagsførering til et strategisk **Agentisk Controller Hub**. Ved å arkitekturere en løsning der "Models Reason, Software Computes, Agents Orchestrate, Systems Verify", oppnår Elkem Technology tre vesentlige gevinstområder:

*   **70 % reduksjon i manuelle rutineoppgaver**: Automatiserte dataløp fra ERP til FAST-strukturerte Excel-modeller og månedlige statusdekker.
*   **100 % beregningssikkerhet (Zero Math Hallucination)**: Skille mellom deterministisk Python/SQL-kode for finansiell matematikk (Earned Value Management, IFRS 15, timelister) og generativ AI for regelverksoppslag og prosjektanalyse.
*   **Full revisjonsklarhet (Audit-Readiness)**: Løpende kontroll av offentlige tilskuddsrammer (SkatteFUNN, Enova, Horizon Europe) kombinert med uforanderlige loggkjeder som tilfredsstiller COSO 2013-rammeverket og kravene i EU AI Act Art. 12.

---

## 2. Fem Strategiske Pilarer for Controller Hub

Gjennomføringen struktureres rundt fem operasjonelle pilarer som direkte adresserers ansvarsområdene i Elkem ASA Technology sin prosjektportefølje:

| Pilar | Operasjonelt Fokus | Primære Leveranser & Standarder |
| :--- | :--- | :--- |
| **1. Standardisering & Governance** | Enhetlig prosjektstruktur og kontoplan | Harmonisert WBS/OBS, FAST-standard for finansmodeller, IFRS 15 over-tid inntektsføring og IAS 38/NRS 8 FoU-aktivering. |
| **2. Prosess- & Rapporteringsautomatisering** | Hurtigere måneds- og årsoppgjør | Automatiserte dataløp fra ERP, standardiserte sjekklistekontroller (månedsoppgjør/årsoppgjør) og Power BI live-strømming. |
| **3. Deterministisk EVM & ML-Prognoser** | Måling av fremdrift og kostnadseffektivitet | EIA-748 Earned Value Management (BCWS, BCWP, ACWP, CPI, SPI, EAC) kombinert med ML-risikomodeller for kostnadsavvik. |
| **4. Grant Management & Tilskuddskontroll** | Maksimering og sikring av offentlig støtte | Automatisk revisjonssjekk for SkatteFUNN (RF-1053B), Enova og Horizon Europe (AGA/MGA) mot ISA 805 / ISAE 3000. |
| **5. Agentisk AI & M365-Integrasjon** | Beslutningsstøtte og orkestrering | Dual-Mode AI Chatbot, Teams Adaptive Cards for Human-in-the-Loop (HITL) godkjenninger, og EU AI Act Art. 12 audit logs. |

---

## 3. Arkitektur: "Models Reason, Software Computes"

Plattformen er bygget som en **Dual-Engine containerisert mikrotjeneste-arkitektur** som kjøres lokalt i Elkems IT-miljø via Docker Compose:

1.  **Engine 1 — Deterministisk Beregningsmotor (Python / SQL)**:
    *   Kjører alle matematiske formler for EIA-748 EVM, IFRS 15 (cost-to-cost over-tid inntektsføring), timeprisberegninger for 2025 og SkatteFUNN-begrensninger (maks 1850 timer, 530 kr/t).
    *   Helt fri for AI-hallusinasjoner og enhetstestet med 100 % dekning via `pytest`.
2.  **Engine 2 — Multi-Agent Orkestrering (Dual-Mode Chat & RAG)**:
    *   **Lead Router Agent**: Identifiserer brukerens intuisjon og ruter enten til strukturerte datatabeller (SQL/EVM) eller ustrukturerte regelverk.
    *   **RAG & Compliance Agent**: Søker i vektordatabasen Qdrant over Elkem Kunnskapsbase (`G:\My Drive\Elkem`) for umiddelbare svar på tilskuddsregler og IFRS-standarder.
    *   **Audit & Governance Agent**: Fanger opp alle beslutningstredyp, krever **Human-in-the-Loop (HITL)** godkjenning før skriving til ERP, og fører logg over alle promptruter.
3.  **M365 & Ekstern Integrasjonslag**:
    *   Toveis MS Excel/Office-kobling, Power BI Push Datasets, MS Teams interaktive godkjenningskort, samt API-koblinger mot Brønnøysundregistrene (Brreg) og Skatteetaten.

---

## 4. Faset Gjennomføringsplan (12 Måneder)

*   **Fase 1 (Måned 1–3) — Fundament & Standardisering**: Harmonisk WBS-oppsett for FoU-porteføljen, etablering av FAST-modellregler og montering av lokal Google Drive Kunnskapsbase.
*   **Fase 2 (Måned 4–6) — Automasjon & EVM-Kjerne**: Idriftsettelse av containerisert beregningsmotor for EVM og IFRS 15, samt kobling mot månedsrapportering.
*   **Fase 3 (Måned 7–9) — ML-Prognoser & Tilskuddskontroll**: Utrulling av automatiske avviksanalyser og revisjonsklare pakker for SkatteFUNN og Enova.
*   **Fase 4 (Måned 10–12) — Full Agentisk Integrasjon**: Utrulling av MS Teams HITL Tollbooth, Dual-Mode Chatbot for prosjektledere og Power BI Command Dashboards.
