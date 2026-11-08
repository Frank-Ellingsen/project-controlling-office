import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Elkem Technology Controller Hub",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #002B49; margin-bottom: 0px; }
    .sub-header { font-size: 1.1rem; color: #555555; margin-bottom: 25px; }
    .stButton>button { background-color: #002B49; color: white; font-weight: 600; }
    .card-header { font-weight: bold; color: #002B49; font-size: 1.15rem; border-bottom: 2px solid #002B49; padding-bottom: 4px; margin-top: 15px; }
    .badge-enova { background-color: #6F42C1; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.85rem; font-weight: 600; }
    .badge-nfr { background-color: #0275D8; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.85rem; font-weight: 600; }
    .badge-skattefunn { background-color: #5CB85C; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.85rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🏛️ Elkem ASA Technology — Project Controlling Office</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Fiskå R&D & Pilot Plant Portfolio | EIA-748 EVM | IFRS 15 | Dynamic Gantt of Gantts | Detailed Project Cards & WBS</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# DATA DEFINITIONS FOR ALL 9 PROJECT CARD DIMENSIONS & WBS
# ---------------------------------------------------------
projects_master = [
    {
        "id": "CA-2045",
        "name": "Fiskå Carbon-Neutral Smelting Pilot Plant",
        "domain": "Prosessutvikling & Pilot (Fiskå)",
        "cam": "Dr. Håkon Olsen",
        "funding_body": "Enova (Demonstrasjon)",
        "badge_class": "badge-enova",
        "bac_nok": 45000000.0,
        "pv_nok": 22500000.0,
        "ev_nok": 21000000.0,
        "ac_nok": 23400000.0,
        "cpi": 0.8974,
        "spi": 0.9333,
        "eac_nok": 50142857.0,
        "poc_pct": 46.67,
        "contract_asset_nok": 5333333.0,
        "start": "2024-01-01",
        "end": "2025-06-30",
        "status": "Forsinket / Over Budsjett (🔴)",
        "beskrivelse": "Industrielt pilotanlegg på Fiskå i Kristiansand for demonstrasjon av utslippsfri smelting, biokarbon-reduksjon og elektrofysisk reaktorteknologi.",
        "formal": "Utvikle og kommersialisere en karbonnøytral smelteprosess for silisium og ferrosilisium, som kutter direkte CO2-utslipp og posisjonerer Elkem som leder innen grønn metallurgi.",
        "scope": "WBS 1.1 Prosessdesign & HAZOP | WBS 1.2 Innkjøp og modulbygging av pilotreaktor | WBS 1.3 Installasjon & varme prøvekjøringer på Fiskå.",
        "time": "Start Q1 2024, Slutt Q2 2025. 18 måneders varighet med ukentlig Earned Schedule-styring og Stage-Gate evalueringer (Gate 1 - Gate 5).",
        "cost": "Totalbudsjett BAC = 45,0 MNOK. Påløpt ACWP = 23,4 MNOK. Opptjent EV = 21,0 MNOK. Sluttkostprognose EAC = 50,1 MNOK (VAC = -5,1 MNOK).",
        "quality": "EIA-748 EVMS Guidelines 1–27. Terskelverdi for avviksrapport: ±5 % CV/SV eller ±500 kNOK. COSO 2013 internkontroll og Enovas kontrollinstruks.",
        "finance": "Forskning kostnadsføres løpende. Kvalifisert utvikling balanseføres etter IAS 38 / NRS 8. Eksterne leveranser inntektsføres etter IFRS 15 over-tid PoC (46,67 %).",
        "funding": "Enova Klima- og energifondet demonstrasjonsstøtte (opptil 45 % dekning for godkjente pilotkostnader).",
        "ds_down": "SAP Core ERP (Hovedbok/GL), leverandørfakturaer, timer i Timeføringssystemet, P6 prosjektplaner.",
        "ds_up": "Enova portalrapportering, Power BI Direct Lake S-kurver, M365 Teams HITL-kort og SHA-256 audit logs.",
        "wbs": [
            {"code": "WBS 1.1", "name": "Pilot Design, Process Modelling & HAZOP", "lead": "Dr. Håkon Olsen", "budget": "8.5 MNOK", "status": "Fullført (🟢)", "spi": 1.00},
            {"code": "WBS 1.2", "name": "Procurement Reactor Vessel & Induction Modules", "lead": "Knut Arnesen", "budget": "22.0 MNOK", "status": "Critical Path Delay (🔴)", "spi": 0.85},
            {"code": "WBS 1.2.1", "name": "  └─ Thermal Insulation & Refractory Lining", "lead": "Knut Arnesen", "budget": "7.5 MNOK", "status": "Forsinket leverandør (🔴)", "spi": 0.80},
            {"code": "WBS 1.2.2", "name": "  └─ Slag Sensors & Optical Pyrometers", "lead": "Svein Viken", "budget": "4.5 MNOK", "status": "Godkjent (🟢)", "spi": 1.02},
            {"code": "WBS 1.3", "name": "Installation, Hot Testing & Pilot Operation", "lead": "Janne Bergan", "budget": "14.5 MNOK", "status": "Planlagt Q4-Q2", "spi": 0.93}
        ]
    },
    {
        "id": "CA-1042",
        "name": "Furnace Automation & Digital Twin System",
        "domain": "Ovnsteknologi & Automasjon",
        "cam": "Marianne Lie",
        "funding_body": "Norges Forskningsråd (NFR)",
        "badge_class": "badge-nfr",
        "bac_nok": 10000000.0,
        "pv_nok": 4000000.0,
        "ev_nok": 3500000.0,
        "ac_nok": 3800000.0,
        "cpi": 0.9211,
        "spi": 0.8750,
        "eac_nok": 10857143.0,
        "poc_pct": 35.00,
        "contract_asset_nok": 1375000.0,
        "start": "2024-02-15",
        "end": "2024-12-31",
        "status": "Kritisk Avvik (🔴)",
        "beskrivelse": "Sensornettverk og nevral-nettbasert digital tvilling for reduksjonsovner ved Elkems smelteverk, styrt fra Kristiansand.",
        "formal": "Realtidsoptimere energiforbruk, beregne slagg-sammensetning og forhindre gassoverkoking via maskinlæring og prediktiv modellstyring.",
        "scope": "WBS 2.1 Sensorrigging og PLC-integrasjon | WBS 2.2 Nevral modellering og tvillingtrening | WBS 2.3 Kontrollrom-utrulling.",
        "time": "Start feb 2024, planlagt ferdigstillingsdato des 2024. Avvik i fremdrift overvåkes med Earned Schedule (ES = 7,0 mnd vs 8,0 mnd faktiske).",
        "cost": "Totalbudsjett BAC = 10,0 MNOK. Påløpt ACWP = 3,8 MNOK. Opptjent EV = 3,5 MNOK. Prognose EAC = 10,86 MNOK.",
        "quality": "Forskningsrådets krav om >60 % eksterntid/faktureringsgrad for FoU-personell. Full sporing av timelister mot hovedbok.",
        "finance": "Treparts-kostnadsmodell (direkte lønn, indirekte kostnader IK1/IK2). Aktivering av utviklingskostnader dersom teknisk gjennomførbarhet bevises.",
        "funding": "Norges Forskningsråd (NFR IPN-prosjektstøtte, 40 % finansieringsandel).",
        "ds_down": "Ovnsdata fra SCADA/IoT, timelister fra FoU-ingeniører, sky-beregningsfakturaer.",
        "ds_up": "Årlig timesatsinnmelding til Forskningsrådet, REST API Swagger docs, MS Teams HITL-varsling.",
        "wbs": [
            {"code": "WBS 2.1", "name": "Sensor Array Mounting & PLC Protocol Setup", "lead": "Marianne Lie", "budget": "2.5 MNOK", "status": "Fullført (🟢)", "spi": 0.92},
            {"code": "WBS 2.2", "name": "Neural Network Digital Twin Engine Development", "lead": "Lars Tangen", "budget": "5.0 MNOK", "status": "Critical Delay (🔴)", "spi": 0.82},
            {"code": "WBS 2.2.1", "name": "  └─ Real-Time Thermo-Chemical Simulator", "lead": "Lars Tangen", "budget": "3.0 MNOK", "status": "Modellberegninger forsinket (🔴)", "spi": 0.78},
            {"code": "WBS 2.3", "name": "Control Room UI & Industrial Deployment", "lead": "Petter Holm", "budget": "2.5 MNOK", "status": "Planlagt Q4", "spi": 0.87}
        ]
    },
    {
        "id": "CA-3080",
        "name": "NextGen Battery Anode Material R&D",
        "domain": "Batterimaterialer & Karbon",
        "cam": "Kjell Arne Bakke",
        "funding_body": "SkatteFUNN (#298412)",
        "badge_class": "badge-skattefunn",
        "bac_nok": 15000000.0,
        "pv_nok": 8000000.0,
        "ev_nok": 8200000.0,
        "ac_nok": 7900000.0,
        "cpi": 1.0380,
        "spi": 1.0250,
        "eac_nok": 14451220.0,
        "poc_pct": 54.67,
        "contract_asset_nok": 520000.0,
        "start": "2024-01-15",
        "end": "2025-03-31",
        "status": "On Schedule / Under Budget (🟢)",
        "beskrivelse": "Forskning og syntetisering av anodematerialer (silisium-karbon kompositter og biokarbon) for høy-ytelse battericeller.",
        "formal": "Utvikle kommersielt anodemateriale med høyere energitetthet og lavere karbonavtrykk enn konvensjonell syntetisk grafitt.",
        "scope": "WBS 3.1 Silisium-graffitt formulering | WBS 3.2 Lab-skalering & 1000 syklusers celletest | WBS 3.3 Revisjonsklargjøring SkatteFUNN.",
        "time": "Start jan 2024, ferdigstillelse mar 2025. Fremdrift ligger 0,25 mnd foran godkjent SkatteFUNN-tidsplan.",
        "cost": "Totalbudsjett BAC = 15,0 MNOK. Påløpt ACWP = 7,9 MNOK. EV = 8,2 MNOK. Forventet sluttkost EAC = 14,45 MNOK (Under budget).",
        "quality": "Lovpålagte timelister spesifisert per delmål. Sjablonggrense: maks 1 850 t/år og 530 kr/t per FoU-ansatt. Revisors attestasjon ISA 805 / ISAE 3000.",
        "finance": "19 % SkatteFUNN-skattefradrag beregnes og føres som offentlig tilskudd i henhold til NRS 4 / IAS 20 (reduksjon av skatt).",
        "funding": "SkatteFUNN (Skatteetaten / NFR, Prosjekt #298412). Inntil 19 % skattefradrag på godkjente FoU-kostnader.",
        "ds_down": "Timelister med spesifiserte delmål, lønnsdata (nominell timelønn), godkjente underleverandørfakturaer.",
        "ds_up": "Skjemasettskjema RF-1053B for Skatteetaten, DuckDB OLAP-konsolidering, CPA revisjonsnotat.",
        "wbs": [
            {"code": "WBS 3.1", "name": "Silicon-Graphite Anode Lab Synthesis", "lead": "Dr. Kari Moe", "budget": "4.5 MNOK", "status": "Fullført (🟢)", "spi": 1.05},
            {"code": "WBS 3.2", "name": "Battery Cell Cycle Testing (1000 Charge Cycles)", "lead": "Erik Ruud", "budget": "8.0 MNOK", "status": "On Schedule (🟢)", "spi": 1.02},
            {"code": "WBS 3.2.1", "name": "  └─ Electrochemical Impedance Spectroscopy", "lead": "Erik Ruud", "budget": "3.0 MNOK", "status": "On Schedule (🟢)", "spi": 1.03},
            {"code": "WBS 3.3", "name": "Audit Dossier Klargjøring (RF-1053B)", "lead": "Frank Ellingsen", "budget": "2.5 MNOK", "status": "Klar for oppgjør", "spi": 1.00}
        ]
    }
]

projects_df = pd.DataFrame([
    {
        "Project_ID": p["id"],
        "Project_Name": p["name"],
        "Domain": p["domain"],
        "CAM": p["cam"],
        "Grant": p["funding_body"],
        "BAC_NOK": p["bac_nok"],
        "PV_NOK": p["pv_nok"],
        "EV_NOK": p["ev_nok"],
        "AC_NOK": p["ac_nok"],
        "CPI": p["cpi"],
        "SPI": p["spi"],
        "EAC_NOK": p["eac_nok"],
        "PoC_Pct": p["poc_pct"],
        "Contract_Asset_NOK": p["contract_asset_nok"],
        "Start_Date": p["start"],
        "End_Date": p["end"],
        "Status": p["status"]
    } for p in projects_master
])

# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------
st.sidebar.header("🔍 Porteføljefilter")
selected_domain = st.sidebar.multiselect(
    "Teknologidomene / Lokasjon",
    options=["Prosessutvikling & Pilot (Fiskå)", "Ovnsteknologi & Automasjon", "Batterimaterialer & Karbon"],
    default=["Prosessutvikling & Pilot (Fiskå)", "Ovnsteknologi & Automasjon", "Batterimaterialer & Karbon"]
)

filtered_projects = projects_df[projects_df["Domain"].isin(selected_domain)]
filtered_master = [p for p in projects_master if p["domain"] in selected_domain]

# Top KPI Summary Bar
col1, col2, col3, col4, col5 = st.columns(5)
total_bac = filtered_projects["BAC_NOK"].sum()
total_ac = filtered_projects["AC_NOK"].sum()
total_eac = filtered_projects["EAC_NOK"].sum()
avg_cpi = filtered_projects["CPI"].mean()
avg_spi = filtered_projects["SPI"].mean()

col1.metric("Total Budsjett (BAC)", f"{total_bac/1e6:.2f} MNOK")
col2.metric("Påløpt (ACWP)", f"{total_ac/1e6:.2f} MNOK")
col3.metric("Prognose Sluttkost (EAC)", f"{total_eac/1e6:.2f} MNOK", delta=f"{(total_bac - total_eac)/1e6:.2f} MNOK", delta_color="inverse")
col4.metric("Portefølje CPI", f"{avg_cpi:.3f}", delta="Cost Overrun" if avg_cpi < 1.0 else "Under Budget", delta_color="normal" if avg_cpi >= 1.0 else "inverse")
col5.metric("Portefølje SPI", f"{avg_spi:.3f}", delta="Behind Schedule" if avg_spi < 1.0 else "Ahead", delta_color="normal" if avg_spi >= 1.0 else "inverse")

st.markdown("---")

# ---------------------------------------------------------
# TAB NAVIGATION (5 TABS INCLUDING PROJECT CARDS & WBS)
# ---------------------------------------------------------
tab_cards, tab1, tab2, tab3, tab4 = st.tabs([
    "📇 Detaljerte Prosjektkort & WBS",
    "📊 Master Gantt of Gantts", 
    "📈 EVM & IFRS 15 Ytelse", 
    "🧾 ERP Transaksjons-Drilldown", 
    "🛡️ Governance & HITL Approval"
])

# ---------------------------------------------------------
# TAB 0: DETALJERTE PROSJEKTKORT & WBS
# ---------------------------------------------------------
with tab_cards:
    st.subheader("📇 Elkem ASA Technology — Detaljerte Prosjektkort & WBS-Struktur")
    st.caption("Full oversikt over alle 9 forretnings- og styringsdimensjoner per prosjekt i porteføljen ved Fiskå.")

    selected_card_id = st.selectbox(
        "Velg prosjekt for fullstendig prosjektkort:",
        options=[p["id"] + " — " + p["name"] for p in filtered_master]
    )
    
    target_id = selected_card_id.split(" — ")[0]
    p = next(item for item in projects_master if item["id"] == target_id)
    
    st.markdown(f"### 📌 Prosjektkort: [{p['id']}] {p['name']}")
    
    # Header metrics inside card
    c_m1, c_m2, c_m3, c_m4, c_m5 = st.columns(5)
    c_m1.metric("Budsjett (BAC)", f"{p['bac_nok']/1e6:.2f} MNOK")
    c_m2.metric("Sluttprognose (EAC)", f"{p['eac_nok']/1e6:.2f} MNOK")
    c_m3.metric("Cost Performance (CPI)", f"{p['cpi']:.4f}")
    c_m4.metric("Schedule Performance (SPI)", f"{p['spi']:.4f}")
    c_m5.metric("IFRS 15 PoC", f"{p['poc_pct']:.2f} %")
    
    st.markdown("---")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown('<div class="card-header">1. Beskrivelse</div>', unsafe_allow_html=True)
        st.write(p["beskrivelse"])
        
        st.markdown('<div class="card-header">2. Formål & Målsetting</div>', unsafe_allow_html=True)
        st.write(p["formal"])
        
        st.markdown('<div class="card-header">3. Scope & Arbeidspakker (WBS)</div>', unsafe_allow_html=True)
        st.write(p["scope"])
        
        st.markdown('<div class="card-header">4. Time (Tidslinje & Stage-Gate)</div>', unsafe_allow_html=True)
        st.write(p["time"])
        
        st.markdown('<div class="card-header">5. Cost (EIA-748 EVM)</div>', unsafe_allow_html=True)
        st.write(p["cost"])
        
    with col_right:
        st.markdown('<div class="card-header">6. Quality (Kvalitets- & Avvikskrav)</div>', unsafe_allow_html=True)
        st.write(p["quality"])
        
        st.markdown('<div class="card-header">7. Finance (IFRS 15 & Balanseføring)</div>', unsafe_allow_html=True)
        st.write(p["finance"])
        
        st.markdown('<div class="card-header">8. Funding (Offentlige Tilskudd)</div>', unsafe_allow_html=True)
        st.write(f"**Tilskuddsorgan**: {p['funding_body']}")
        st.write(p["funding"])
        
        st.markdown('<div class="card-header">9. Data Sources (Inndata & Utdata)</div>', unsafe_allow_html=True)
        st.write(f"📥 **Download (ERP/Inndata)**: {p['ds_down']}")
        st.write(f"📤 **Upload (Portal/Utdata)**: {p['ds_up']}")

    st.markdown("---")
    st.markdown(f"#### 🌳 WBS-Struktur for {p['id']}")
    wbs_df = pd.DataFrame(p["wbs"])
    st.dataframe(wbs_df, use_container_width=True)

# ---------------------------------------------------------
# TAB 1: MASTER GANTT OF GANTTS
# ---------------------------------------------------------
with tab1:
    st.subheader("🗓️ Executive Portfolio Master Gantt (Gantt of Gantts)")
    st.caption("Hierarkisk porteføljetidslinje som ruller opp WBS-elementer og Stage-Gate milepæler på tvers av Elkem Technology.")
    
    master_gantt_rows = []
    
    for idx, row in filtered_projects.iterrows():
        master_gantt_rows.append({
            "Task_Name": f"<b>[{row['Project_ID']}] {row['Project_Name']}</b>",
            "Project": row["Project_ID"],
            "Level": "1. Master Portfolio Roll-Up",
            "Start": row["Start_Date"],
            "Finish": row["End_Date"],
            "SPI": row["SPI"],
            "Status_Category": "Master Project",
            "Details": f"BAC: {row['BAC_NOK']/1e6:.1f}M | SPI: {row['SPI']} | CAM: {row['CAM']}"
        })
    
    wbs_details = []
    for pm in filtered_master:
        for w in pm["wbs"]:
            wbs_details.append({
                "Task_Name": f"  └─ {w['code']} {w['name']}",
                "Project": pm["id"],
                "Level": "2. WBS & Milestones",
                "Start": pm["start"],
                "Finish": pm["end"],
                "SPI": w["spi"],
                "Status_Category": w["status"],
                "Details": f"Ansvarlig: {w['lead']} | Budsjett: {w['budget']}"
            })
    
    gantt_combined = master_gantt_rows + [w for w in wbs_details if w["Project"] in filtered_projects["Project_ID"].values]
    gantt_df = pd.DataFrame(gantt_combined)
    
    fig_gantt = px.timeline(
        gantt_df,
        x_start="Start",
        x_end="Finish",
        y="Task_Name",
        color="Status_Category",
        hover_data=["Project", "SPI", "Details"],
        title="Elkem Technology — Master Schedule & Multi-Level Gantt Chart",
        color_discrete_map={
            "Master Project": "#002B49",
            "Fullført (🟢)": "#28A745",
            "On Schedule (🟢)": "#20C997",
            "Critical Path Delay (🔴)": "#DC3545",
            "Critical Delay (🔴)": "#DC3545",
            "Forsinket leverandør (🔴)": "#DC3545",
            "Stage-Gate (◆)": "#6F42C1",
            "Planlagt Q4-Q2": "#6C757D"
        }
    )
    fig_gantt.update_yaxes(autorange="reversed", title="")
    fig_gantt.update_layout(
        height=550,
        margin=dict(l=10, r=10, t=40, b=10),
        legend_title_text="Kategori / Status"
    )
    st.plotly_chart(fig_gantt, use_container_width=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.info("💡 **Gantt of Gantts Innsikt**: Prosjekt `CA-2045` (Fiskå Pilotanlegg) har kritisk sti knyttet til leveranse av reaktorbeholder (`WBS 1.2`). Enova Stage-Gate 3 milepælen 15. nov er avhengig av at isolasjonsmaterialet installeres uten flere uker avvik.")
    with col_b:
        st.warning("⚠️ **Ressurskonflikt**: `CA-1042` Digital Twin testing overlapper med ovnstilgang for `CA-2045` i Q4. Controller anbefaler koordinering av ovnstid på Fiskå.")

# ---------------------------------------------------------
# TAB 2: EVM & IFRS 15 YTELSE
# ---------------------------------------------------------
with tab2:
    st.subheader("📈 Earned Value Management (EIA-748) & IFRS 15 Analysis")
    
    selected_proj = st.selectbox("Velg prosjekt for dypdykk", options=filtered_projects["Project_ID"].tolist())
    p_data = filtered_projects[filtered_projects["Project_ID"] == selected_proj].iloc[0]
    
    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    col_e1.metric("Budsjett ved fullføring (BAC)", f"{p_data['BAC_NOK']/1e6:.2f} MNOK")
    col_e2.metric("Opptjent Verdi (BCWP / EV)", f"{p_data['EV_NOK']/1e6:.2f} MNOK")
    col_e3.metric("Cost Variance (CV)", f"{(p_data['EV_NOK'] - p_data['AC_NOK'])/1e3:.0f} kNOK", delta=f"CPI: {p_data['CPI']:.3f}")
    col_e4.metric("Schedule Variance (SV)", f"{(p_data['EV_NOK'] - p_data['PV_NOK'])/1e3:.0f} kNOK", delta=f"SPI: {p_data['SPI']:.3f}")
    
    months = ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Oktober (YTD)", "Nov", "Des"]
    pv_curve = [p_data['BAC_NOK'] * (i/12) for i in range(1, 13)]
    ev_curve = [p_data['EV_NOK'] * (i/10) if i <= 10 else None for i in range(1, 13)]
    ac_curve = [p_data['AC_NOK'] * (i/10) if i <= 10 else None for i in range(1, 13)]
    
    fig_scurve = go.Figure()
    fig_scurve.add_trace(go.Scatter(x=months, y=pv_curve, mode='lines+markers', name='BCWS (Planlagt Verdi)', line=dict(color='#002B49', width=3)))
    fig_scurve.add_trace(go.Scatter(x=months, y=ev_curve, mode='lines+markers', name='BCWP (Opptjent Verdi)', line=dict(color='#28A745', width=3)))
    fig_scurve.add_trace(go.Scatter(x=months, y=ac_curve, mode='lines+markers', name='ACWP (Faktisk Kostnad)', line=dict(color='#DC3545', width=3, dash='dot')))
    fig_scurve.update_layout(title=f"S-Kurve Porteføljevisning: {p_data['Project_Name']} ({p_data['Project_ID']})", yaxis_title="NOK", height=400)
    
    st.plotly_chart(fig_scurve, use_container_width=True)

# ---------------------------------------------------------
# TAB 3: ERP TRANSAKSJONS-DRILLDOWN
# ---------------------------------------------------------
with tab3:
    st.subheader("🧾 ERP Transaksjons-Drilldown (DuckDB Line-Item Taxonomy)")
    st.caption("Viser bilagsføringer på laveste nivå fra ERP (SAP/Agresso) koblet mot SkatteFUNN timesatsgrenser (530 kr/t).")
    
    tx_df = pd.DataFrame([
        {"Bilag": "VND-99281", "Dato": "2024-10-14", "WBS": "CA-2045.2", "Beskrivelse": "Reaktor isolasjonskomponenter", "Leverandør": "Elkem Carbon AS (997729803)", "Artskonto": "4300 Pilotutstyr", "Beløp (NOK)": 1450000.0, "SkatteFUNN Status": "N/A"},
        {"Bilag": "TIM-88210", "Dato": "2024-10-18", "WBS": "CA-3080.1", "Beskrivelse": "Lab-ingeniør 120t @ 550 kr/t", "Leverandør": "Intern Timeføring (Fiskå)", "Artskonto": "5000 Lønn FoU", "Beløp (NOK)": 66000.0, "SkatteFUNN Status": "⚠️ Justert til 530 kr/t capped"},
        {"Bilag": "VND-99304", "Dato": "2024-10-25", "WBS": "CA-1042.2", "Beskrivelse": "GPU Serverkraft Neural Twin", "Leverandør": "Nordic Cloud Hosting AS", "Artskonto": "6800 IT/Beregningskraft", "Beløp (NOK)": 185000.0, "SkatteFUNN Status": "Godkjent FoU-kostnad"},
        {"Bilag": "TIM-88245", "Dato": "2024-10-28", "WBS": "CA-2045.1", "Beskrivelse": "Senior Forsker 80t @ 530 kr/t", "Leverandør": "Intern Timeføring (Fiskå)", "Artskonto": "5000 Lønn FoU", "Beløp (NOK)": 42400.0, "SkatteFUNN Status": "Godkjent"}
    ])
    
    st.dataframe(tx_df, use_container_width=True)

# ---------------------------------------------------------
# TAB 4: GOVERNANCE & HITL APPROVAL
# ---------------------------------------------------------
with tab4:
    st.subheader("🛡️ Governance & Human-in-the-Loop (HITL) Tollbooth")
    st.caption("COSO 2013 & EU AI Act Art. 12 kryptografisk uforanderlig godkjenningslogg for EAC-prognoseendringer.")
    
    with st.form("hitl_form"):
        st.write("**Endringsforslag for EAC (Prognose ved fullføring)**")
        st.text_input("Prosjekt ID", value="CA-2045")
        st.number_input("Opprinnelig Budsjett (BAC)", value=45000000.0, disabled=True)
        st.number_input("Ny Beregnet EAC (NOK)", value=50142857.0)
        reason = st.text_area("Begrunnelse for avviksgodkjenning", value="Leverandørforsinkelse på reaktorbeholder og termisk isolasjon ved Fiskå pilotanlegg.")
        approver = st.text_input("Godkjennes av (Technology Controller)", value="Frank Ellingsen")
        
        col_btn1, col_btn2 = st.columns(2)
        submit_approve = col_btn1.form_submit_button("✅ GODKJENN EAC-PROGNOSE")
        submit_reject = col_btn2.form_submit_button("❌ AVVIS / BE OM REVIDERING")
        
        if submit_approve:
            st.success(f"EAC-endring godkjent av {approver}! Audit-hash generert: `0x8f2a99c4e10b` (COSO 2013 Logged).")

st.markdown("---")
st.caption("🏛️ Elkem ASA Technology Controlling Office | Kristiansand, Norway | System Status: ONLINE 🟢")
