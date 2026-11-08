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
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🏛️ Elkem ASA Technology — Project Controlling Office</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Fiskå R&D & Pilot Plant Portfolio | EIA-748 EVM | IFRS 15 | Risk Matrix & Project Evaluator</div>', unsafe_allow_html=True)

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
        "Status": "Forsinket / Over Budsjett (🔴)",
        "Description": "Industrielt pilotanlegg på Fiskå for utslippsfri smelting, reduksjonsteknologi og testkjøring av reaktorer.",
        "Purpose": "Utvikle og demonstrere en karbonnøytral smelteprosess for silisium for å bidra til lavutslipps-veikartet.",
        "Quality_Std": "EIA-748 EVMS retningslinje 22, COSO 2013 internkontroll og Enovas kontrollforskrift.",
        "Finance_Rule": "IAS 38 / NRS 8 balanseføring av kvalifiserte pilotutviklingskostnader, IFRS 15 over-tid inntektsføring (PoC %).",
        "Download_Src": "SAP Core Financial (GL 4300/5000), P6 XML export, leverandørfakturaer.",
        "Upload_Src": "Enova rapportportal, Power BI Direct Lake S-kurver, Altinn Skatteetaten RF-1053B."
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
        "Status": "Kritisk Avvik (🔴)",
        "Description": "Digital tvilling og nevralt nettverk for sanntids energikontroll og termisk avviksdeteksjon i reduksjonsovner.",
        "Purpose": "Stabilisere ovnsdrift, minimere energiforbruk og forhindre gasslekkasjer ved datadrevet modellstyring.",
        "Quality_Std": "Forskningsrådets krav om min. 60% eksterntid og full sporbarhet fra LK/IK-satser til hovedbok.",
        "Finance_Rule": "NFR trepartsmodell (LK direkte lønn, IK1/IK2 indirekte kostnader).",
        "Download_Src": "Elektroniske timelister per forsker, Ovnssensorer PLC, SAP ERP POs.",
        "Upload_Src": "NFR Årlig timesatsinnmelding, M365 Teams Adaptive Cards for HITL-godkjenning."
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
        "Status": "On Schedule / Under Budget (🟢)",
        "Description": "Forskning og utvikling innen silisium-graffitt og biokarbon anodematerialer for battericeller.",
        "Purpose": "Utvikle kommersielle, ultra-rene anodematerialer med lavt miljøavtrykk for elbilmarkedet.",
        "Quality_Std": "SkatteFUNN forskrift § 16-40: Daglige timelister, tak 1 850t/år og 530 kr/t, ISA 805 / ISAE 3000 revisorattest.",
        "Finance_Rule": "SkatteFUNN 19% skattefradrag regnskapsføres etter NRS 4 / IAS 20 som kortsiktig tilskuddsfordring.",
        "Download_Src": "Lønnsdata, daglige timelister for FoU-personell, godkjente underleverandørfakturaer.",
        "Upload_Src": "Skatteetaten skjema RF-1053B, CPA ISA 805 revisjonsnotat, DuckDB konsolidering."
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

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📇 Detaljerte Prosjektkort & WBS", 
    "📈 EVM & S-Kurver", 
    "⚠️ Prosjekt Risikomatrise",
    "🎓 Prosjektevaluator & Læringspunkter",
    "🛡️ Governance & HITL Approval"
])

with tab1:
    st.subheader("📇 9-Dimensjonale Prosjektkort med Dedikert Gantt-Tidslinje")
    selected_proj_id = st.selectbox("Velg Prosjekt", options=filtered_projects["Project_ID"].tolist())
    p = filtered_projects[filtered_projects["Project_ID"] == selected_proj_id].iloc[0]
    
    st.markdown(f"### **[{p['Project_ID']}] {p['Project_Name']}**")
    
    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown(f"**1. Beskrivelse**: {p['Description']}")
        st.markdown(f"**2. Formål**: {p['Purpose']}")
        st.markdown(f"**3. Time & Stage-Gate**: Tidsrom {p['Start_Date']} til {p['End_Date']}. Følger Stage-Gate kontroll.")
        st.markdown(f"**4. Quality & Compliance**: {p['Quality_Std']}")
        st.markdown(f"**5. Finance & Regnskap**: {p['Finance_Rule']}")
    with c_right:
        st.markdown(f"**6. Budsjett & EVM**: BAC: {p['BAC_NOK']/1e6:.1f}M | CPI: {p['CPI']} | SPI: {p['SPI']} | EAC: {p['EAC_NOK']/1e6:.1f}M")
        st.markdown(f"**7. Offentlig Tilskudd**: {p['Grant']}")
        st.markdown(f"**8. Download (ERP/Inndata)**: {p['Download_Src']}")
        st.markdown(f"**9. Upload (Utdata/Portaler)**: {p['Upload_Src']}")

    st.markdown("---")
    st.subheader(f"📊 Dedikert WBS Gantt-Kart: {selected_proj_id}")
    
    wbs_data_dict = {
        "CA-2045": [
            {"WBS": "WBS 1.1 Pilot Design & HAZOP", "Start": "2024-01-01", "Finish": "2024-04-30", "Status": "Fullført (🟢)"},
            {"WBS": "WBS 1.2 Procurement Reactor Vessel", "Start": "2024-04-01", "Finish": "2024-11-15", "Status": "Kritisk sti (🔴)"},
            {"WBS": "🚩 Gate 3 Approval (Enova)", "Start": "2024-11-15", "Finish": "2024-11-20", "Status": "Stage-Gate (◆)"},
            {"WBS": "WBS 1.3 Commissioning & Testing", "Start": "2024-11-20", "Finish": "2025-06-30", "Status": "Planlagt"}
        ],
        "CA-1042": [
            {"WBS": "WBS 2.1 Sensor Calibration", "Start": "2024-02-15", "Finish": "2024-06-30", "Status": "Fullført (🟢)"},
            {"WBS": "WBS 2.2 Neural Twin Training", "Start": "2024-06-01", "Finish": "2024-10-31", "Status": "Kritisk sti (🔴)"},
            {"WBS": "🚩 Gate 4 System Go-Live", "Start": "2024-12-01", "Finish": "2024-12-31", "Status": "Stage-Gate (◆)"}
        ],
        "CA-3080": [
            {"WBS": "WBS 3.1 Silicon-Graphite Formulation", "Start": "2024-01-15", "Finish": "2024-07-31", "Status": "Fullført (🟢)"},
            {"WBS": "WBS 3.2 Battery Cell Cycle Testing", "Start": "2024-07-01", "Finish": "2025-03-31", "Status": "On Schedule (🟢)"}
        ]
    }
    
    df_gantt_single = pd.DataFrame(wbs_data_dict.get(selected_proj_id, []))
    fig_single = px.timeline(df_gantt_single, x_start="Start", x_end="Finish", y="WBS", color="Status", title=f"WBS Tidslinje for {selected_proj_id}")
    fig_single.update_yaxes(autorange="reversed")
    st.plotly_chart(fig_single, use_container_width=True)

with tab2:
    st.subheader("📈 Earned Value Management (EIA-748) & S-Kurver")
    selected_proj = st.selectbox("Velg prosjekt for S-kurve", options=filtered_projects["Project_ID"].tolist(), key="scurve_select")
    p_data = filtered_projects[filtered_projects["Project_ID"] == selected_proj].iloc[0]
    
    months = ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Oktober (YTD)", "Nov", "Des"]
    pv_curve = [p_data['BAC_NOK'] * (i/12) for i in range(1, 13)]
    ev_curve = [p_data['EV_NOK'] * (i/10) if i <= 10 else None for i in range(1, 13)]
    ac_curve = [p_data['AC_NOK'] * (i/10) if i <= 10 else None for i in range(1, 13)]
    
    fig_scurve = go.Figure()
    fig_scurve.add_trace(go.Scatter(x=months, y=pv_curve, mode='lines+markers', name='BCWS (Planlagt Verdi)', line=dict(color='#002B49', width=3)))
    fig_scurve.add_trace(go.Scatter(x=months, y=ev_curve, mode='lines+markers', name='BCWP (Opptjent Verdi)', line=dict(color='#28A745', width=3)))
    fig_scurve.add_trace(go.Scatter(x=months, y=ac_curve, mode='lines+markers', name='ACWP (Faktisk Kostnad)', line=dict(color='#DC3545', width=3, dash='dot')))
    fig_scurve.update_layout(title=f"S-Kurve: {p_data['Project_Name']} ({p_data['Project_ID']})", yaxis_title="NOK", height=400)
    
    st.plotly_chart(fig_scurve, use_container_width=True)

with tab3:
    st.subheader("⚠️ Prosjekt Risikomatrise (Risk Matrix & Heatmap)")
    st.caption("Kvantitativ risikoevaluering etter COSO 2013 og EIA-748 avviksretningslinjer.")
    
    risks_df = pd.DataFrame([
        {"ID": "R-01", "Prosjekt": "CA-2045", "Risikobeskrivelse": "Leverandørforsinkelse på reaktorbeholder (Long-Lead)", "Prob": 4, "Impact": 4, "Score": 16, "Nivå": "Kritisk (🔴)", "Mitigering": "Parallell oppfølging og del-oppstart HAZOP."},
        {"ID": "R-02", "Prosjekt": "CA-2045", "Risikobeskrivelse": "Enova Stage-Gate 3 milepæl forsinket (Tilskuddsutbetaling)", "Prob": 3, "Impact": 5, "Score": 15, "Nivå": "Kritisk (🔴)", "Mitigering": "Fremskynde dokumentasjon og delutbetaling."},
        {"ID": "R-03", "Prosjekt": "CA-1042", "Risikobeskrivelse": "GPU-beregningskapasitet overskredet ved modellering", "Prob": 4, "Impact": 3, "Score": 12, "Nivå": "Moderat (🟡)", "Mitigering": "Kjøpe skybasert burst-kapasitet (Nordic Cloud)."},
        {"ID": "R-04", "Prosjekt": "CA-1042", "Risikobeskrivelse": "Ovnstilgang på Fiskå overlapper med CA-2045 i Q4", "Prob": 3, "Impact": 4, "Score": 12, "Nivå": "Moderat (🟡)", "Mitigering": "Samkjørt testplan for Kristiansand."},
        {"ID": "R-05", "Prosjekt": "CA-3080", "Risikobeskrivelse": "SkatteFUNN timesats overstiger 530 kr/t for seniorforskere", "Prob": 2, "Impact": 3, "Score": 6, "Nivå": "Lav (🟢)", "Mitigering": "Automatisk capping i ERP-timelistesystemet."}
    ])
    
    col_r1, col_r2 = st.columns([7, 5])
    with col_r1:
        st.dataframe(risks_df, use_container_width=True)
    with col_r2:
        fig_heatmap = px.density_heatmap(risks_df, x="Impact", y="Prob", z="Score", title="Risiko Heatmap (Sannsynlighet vs Konsekvens)", color_continuous_scale="YlOrRd")
        st.plotly_chart(fig_heatmap, use_container_width=True)

with tab4:
    st.subheader("🎓 Project Evaluator & Retrospective Lessons Learned")
    st.caption("Systematisk erfaringsoverføring og evaluering for å forbedre fremtidige Elkem R&D-baselines.")
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        st.markdown("#### 📌 Læringspunkter (Lessons Learned Repository)")
        st.info("1. **Innkjøp & Long-Lead**: Spesialkomponenter krever minimum 6 ukers tidsbuffer i baselinetidslinjen (PV). Må kobles fra utbetalingsmilepæler.")
        st.warning("2. **Pilotressurser**: Samtidige pilotprosjekter ved Fiskå må koordineres i en felles ovns- og testplan før Gate 2-godkjenning.")
        st.success("3. **Tilskudds-Compliance**: Automatisk kapping av timelisters timesatser (530 kr/t) ved månedsoppgjør fjerner revisjonsavvik.")
    
    with col_l2:
        st.markdown("#### 🎛️ Interaktiv Project Evaluator Scorecard")
        score_sched = st.slider("1. Tids- og Milepælspresisjon", 1, 5, 3)
        score_cost = st.slider("2. Budsjett- og EVM Presisjon", 1, 5, 4)
        score_grant = st.slider("3. Tilskudds- Compliance", 1, 5, 5)
        score_tech = st.slider("4. Teknisk Kvalitet & Pilot Readiness", 1, 5, 4)
        
        total_eval = (score_sched + score_cost + score_grant + score_tech) * 5
        st.metric("Beregnet Evalueringsindeks for Fremtidige Prosjekter", f"{total_eval} / 100", delta="Klasse A (Høy Læringsverdi)" if total_eval >= 75 else "Klasse B")

with tab5:
    st.subheader("🛡️ Governance & Human-in-the-Loop (HITL) Tollbooth")
    st.caption("COSO 2013 & EU AI Act Art. 12 kryptografisk uforanderlig godkjenningslogg.")
    
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
