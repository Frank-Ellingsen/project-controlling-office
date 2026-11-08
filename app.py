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
    .dim-box { background: #F8FAFC; border-left: 4px solid #005A9C; padding: 1rem; border-radius: 0 8px 8px 0; margin-bottom: 0.8rem; }
    .dim-title { font-size: 0.85rem; font-weight: 700; text-transform: uppercase; color: #002B49; margin-bottom: 0.3rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🏛️ Elkem ASA Technology — Project Controlling Office</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Fiskå R&D & Pilot Plant Portfolio | EIA-748 EVM | IFRS 15 | Dedikerte Dynamiske Prosjekt-Gantt</div>', unsafe_allow_html=True)

st.sidebar.header("🔍 Porteføljefilter")
selected_domain = st.sidebar.multiselect(
    "Teknologidomene / Lokasjon",
    options=["Prosessutvikling & Pilot (Fiskå)", "Ovnsteknologi & Automasjon", "Batterimaterialer & Karbon"],
    default=["Prosessutvikling & Pilot (Fiskå)", "Ovnsteknologi & Automasjon", "Batterimaterialer & Karbon"]
)

projects_df = pd.DataFrame([
    {
        "Project_ID": "CA-2045",
        "Project_Name": "Fiskå Carbon-Neutral Smelting Pilot Plant",
        "Domain": "Prosessutvikling & Pilot (Fiskå)",
        "CAM": "Dr. Håkon Olsen",
        "Grant": "Enova (Demonstrasjon)",
        "BAC_NOK": 45000000.0,
        "PV_NOK": 22500000.0,
        "EV_NOK": 21000000.0,
        "AC_NOK": 23400000.0,
        "CPI": 0.8974,
        "SPI": 0.9333,
        "EAC_NOK": 50142857.0,
        "PoC_Pct": 46.67,
        "Contract_Asset_NOK": 5333333.0,
        "Start_Date": "2024-01-01",
        "End_Date": "2025-06-30",
        "Status": "Forsinket / Over Budsjett (🔴)"
    },
    {
        "Project_ID": "CA-1042",
        "Project_Name": "Furnace Automation & Digital Twin System",
        "Domain": "Ovnsteknologi & Automasjon",
        "CAM": "Marianne Lie",
        "Grant": "Norges Forskningsråd (NFR)",
        "BAC_NOK": 10000000.0,
        "PV_NOK": 4000000.0,
        "EV_NOK": 3500000.0,
        "AC_NOK": 3800000.0,
        "CPI": 0.9211,
        "SPI": 0.8750,
        "EAC_NOK": 10857143.0,
        "PoC_Pct": 35.00,
        "Contract_Asset_NOK": 1375000.0,
        "Start_Date": "2024-02-15",
        "End_Date": "2024-12-31",
        "Status": "Kritisk Avvik (🔴)"
    },
    {
        "Project_ID": "CA-3080",
        "Project_Name": "NextGen Battery Anode Material R&D",
        "Domain": "Batterimaterialer & Karbon",
        "CAM": "Kjell Arne Bakke",
        "Grant": "SkatteFUNN (#298412)",
        "BAC_NOK": 15000000.0,
        "PV_NOK": 8000000.0,
        "EV_NOK": 8200000.0,
        "AC_NOK": 7900000.0,
        "CPI": 1.0380,
        "SPI": 1.0250,
        "EAC_NOK": 14451220.0,
        "PoC_Pct": 54.67,
        "Contract_Asset_NOK": 520000.0,
        "Start_Date": "2024-01-15",
        "End_Date": "2025-03-31",
        "Status": "On Schedule / Under Budget (🟢)"
    }
])

filtered_projects = projects_df[projects_df["Domain"].isin(selected_domain)]

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

tab1, tab2, tab3, tab4 = st.tabs([
    "📇 Prosjektkort & Dynamiske Gantt", 
    "📈 EVM & IFRS 15 Ytelse", 
    "🧾 ERP Transaksjons-Drilldown", 
    "🛡️ Governance & HITL Approval"
])

with tab1:
    st.subheader("📇 Prosjektkort & Dedikerte Dynamiske Gantt-kart")
    st.caption("Viser detaljerte 9-dimensjonale prosjektkort og dedikerte Gantt-tidslinjer per prosjekt.")

    for idx, p in filtered_projects.iterrows():
        with st.expander(f"📌 [{p['Project_ID']}] {p['Project_Name']} — (CPI: {p['CPI']:.3f} | SPI: {p['SPI']:.3f})", expanded=True):
            
            c_a, c_b, c_c = st.columns(3)
            with c_a:
                st.markdown(f'''<div class="dim-box"><div class="dim-title">1. Beskrivelse</div><p class="small">{p['Project_Name']} ved Fiskå pilotanlegg/lab.</p></div>''', unsafe_allow_html=True)
                st.markdown(f'''<div class="dim-box"><div class="dim-title">4. Time & Stage-Gate</div><p class="small">{p['Start_Date']} – {p['End_Date']}<br>Stage-Gate milepæler (Gate 1–5)</p></div>''', unsafe_allow_html=True)
                st.markdown(f'''<div class="dim-box"><div class="dim-title">7. Finance & IFRS 15</div><p class="small">PoC: {p['PoC_Pct']}%<br>Contract Asset: {p['Contract_Asset_NOK']/1e6:.2f} MNOK</p></div>''', unsafe_allow_html=True)
            with c_b:
                st.markdown(f'''<div class="dim-box"><div class="dim-title">2. Formål</div><p class="small">Forskning og industriell demonstrasjon for Elkem ASA Technology.</p></div>''', unsafe_allow_html=True)
                st.markdown(f'''<div class="dim-box"><div class="dim-title">5. Cost & EVM</div><p class="small">BAC: {p['BAC_NOK']/1e6:.1f}M | ACWP: {p['AC_NOK']/1e6:.1f}M<br>EAC: {p['EAC_NOK']/1e6:.1f}M</p></div>''', unsafe_allow_html=True)
                st.markdown(f'''<div class="dim-box"><div class="dim-title">8. Funding</div><p class="small">Offentlig tilskudd: {p['Grant']}</p></div>''', unsafe_allow_html=True)
            with c_c:
                st.markdown(f'''<div class="dim-box"><div class="dim-title">3. Scope (WBS)</div><p class="small">WBS elementer & Stage-Gate milepæler</p></div>''', unsafe_allow_html=True)
                st.markdown(f'''<div class="dim-box"><div class="dim-title">6. Quality & Compliance</div><p class="small">EIA-748, COSO 2013, ISA 805 / ISAE 3000</p></div>''', unsafe_allow_html=True)
                st.markdown(f'''<div class="dim-box"><div class="dim-title">9. Data Sources</div><p class="small">Inndata: SAP ERP, Timelister<br>Utdata: Enova/NFR Portal, Power BI</p></div>''', unsafe_allow_html=True)

            st.markdown("#### 🗓️ Dynamisk Gantt-kart")
            if p['Project_ID'] == "CA-2045":
                wbs_gantt = pd.DataFrame([
                    {"Task": "WBS 1.1 Pilot Design & HAZOP", "Start": "2024-01-01", "Finish": "2024-04-30", "Status": "Fullført (🟢)"},
                    {"Task": "WBS 1.2 Procurement Reactor Vessel", "Start": "2024-04-01", "Finish": "2024-11-15", "Status": "Kritisk Sti (🔴)"},
                    {"Task": "  └─ Refractory Lining Isolasjon", "Start": "2024-05-01", "Finish": "2024-10-01", "Status": "Kritisk Sti (🔴)"},
                    {"Task": "  └─ Optical Pyrometers & Sensors", "Start": "2024-06-15", "Finish": "2024-11-15", "Status": "Fullført (🟢)"},
                    {"Task": "🚩 Gate 3 Enova Approval", "Start": "2024-11-15", "Finish": "2024-11-20", "Status": "Stage-Gate (◆)"},
                    {"Task": "WBS 1.3 Hot Testing & Operations", "Start": "2024-11-20", "Finish": "2025-06-30", "Status": "Planlagt"}
                ])
            elif p['Project_ID'] == "CA-1042":
                wbs_gantt = pd.DataFrame([
                    {"Task": "WBS 2.1 Sensor & PLC Calibration", "Start": "2024-02-15", "Finish": "2024-06-30", "Status": "Fullført (🟢)"},
                    {"Task": "WBS 2.2 Neural Twin Training", "Start": "2024-06-01", "Finish": "2024-10-31", "Status": "Kritisk Sti (🔴)"},
                    {"Task": "🚩 Gate 4 Control Room Go-Live", "Start": "2024-12-01", "Finish": "2024-12-31", "Status": "Stage-Gate (◆)"}
                ])
            else:
                wbs_gantt = pd.DataFrame([
                    {"Task": "WBS 3.1 Anode Formulation", "Start": "2024-01-15", "Finish": "2024-07-31", "Status": "Fullført (🟢)"},
                    {"Task": "WBS 3.2 Cell Cycle Testing", "Start": "2024-07-01", "Finish": "2025-03-31", "Status": "On Schedule (🟢)"},
                    {"Task": "WBS 3.3 SkatteFUNN Audit", "Start": "2025-01-01", "Finish": "2025-03-31", "Status": "Planlagt"}
                ])

            fig_p = px.timeline(
                wbs_gantt, x_start="Start", x_end="Finish", y="Task", color="Status",
                title=f"Gantt-tidslinje for {p['Project_ID']}",
                color_discrete_map={
                    "Fullført (🟢)": "#28A745",
                    "On Schedule (🟢)": "#20C997",
                    "Kritisk Sti (🔴)": "#DC3545",
                    "Stage-Gate (◆)": "#6F42C1",
                    "Planlagt": "#6C757D"
                }
            )
            fig_p.update_yaxes(autorange="reversed", title="")
            fig_p.update_layout(height=260, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_p, use_container_width=True)

with tab2:
    st.subheader("📈 Earned Value Management (EIA-748) & IFRS 15 Analysis")
    selected_proj = st.selectbox("Velg prosjekt for dypdykk", options=filtered_projects["Project_ID"].tolist())
    p_data = filtered_projects[filtered_projects["Project_ID"] == selected_proj].iloc[0]
    
    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    col_e1.metric("Budsjett (BAC)", f"{p_data['BAC_NOK']/1e6:.2f} MNOK")
    col_e2.metric("Opptjent Verdi (EV)", f"{p_data['EV_NOK']/1e6:.2f} MNOK")
    col_e3.metric("Cost Variance (CV)", f"{(p_data['EV_NOK'] - p_data['AC_NOK'])/1e3:.0f} kNOK", delta=f"CPI: {p_data['CPI']:.3f}")
    col_e4.metric("Schedule Variance (SV)", f"{(p_data['EV_NOK'] - p_data['PV_NOK'])/1e3:.0f} kNOK", delta=f"SPI: {p_data['SPI']:.3f}")

with tab3:
    st.subheader("🧾 ERP Transaksjons-Drilldown (DuckDB Line-Item Taxonomy)")
    tx_df = pd.DataFrame([
        {"Bilag": "VND-99281", "Dato": "2024-10-14", "WBS": "CA-2045.2", "Beskrivelse": "Reaktor isolasjonskomponenter", "Leverandør": "Elkem Carbon AS", "Beløp (NOK)": 1450000.0, "SkatteFUNN Status": "N/A"},
        {"Bilag": "TIM-88210", "Dato": "2024-10-18", "WBS": "CA-3080.1", "Beskrivelse": "Lab-ingeniør 120t @ 550 kr/t", "Leverandør": "Intern Timeføring", "Beløp (NOK)": 66000.0, "SkatteFUNN Status": "⚠️ Justert til 530 kr/t"},
        {"Bilag": "TIM-88245", "Dato": "2024-10-28", "WBS": "CA-2045.1", "Beskrivelse": "Senior Forsker 80t @ 530 kr/t", "Leverandør": "Intern Timeføring", "Beløp (NOK)": 42400.0, "SkatteFUNN Status": "Godkjent"}
    ])
    st.dataframe(tx_df, use_container_width=True)

with tab4:
    st.subheader("🛡️ Governance & Human-in-the-Loop (HITL) Tollbooth")
    st.info("COSO 2013 & EU AI Act Art. 12 kryptografisk uforanderlig godkjenningslogg for EAC-prognoseendringer.")

st.markdown("---")
st.caption("🏛️ Elkem ASA Technology Controlling Office | Kristiansand, Norway | System Status: ONLINE 🟢")
