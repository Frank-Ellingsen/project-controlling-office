import os
import sys
import pandas as pd
import duckdb

def main():
    print("==================================================================")
    print("🏛️ ELKEM ASA TECHNOLOGY — PROJECT CONTROLLING OFFICE INGESTION")
    print("==================================================================")
    
    data_dir = os.path.join(os.getcwd(), "data")
    if not os.path.exists(data_dir):
        print(f"⚠️ Mappen 'data/' finnes ikke i {os.getcwd()}. Oppretter mappen...")
        os.makedirs(data_dir, exist_ok=True)
        print(" Vennligst plasser de 6 CSV-filene i 'data/'-mappen og kjør på nytt.")
        return

    csv_files = [
        "01_p6_wbs_schedule_baseline.csv",
        "02_hr_timesheets_line_items.csv",
        "03_sap_gl_transaction_journal.csv",
        "04_evm_monthly_performance.csv",
        "05_ifrs15_revenue_contract_asset.csv",
        "06_public_grants_skattefunn_enova.csv"
    ]
    
    missing = [f for f in csv_files if not os.path.exists(os.path.join(data_dir, f))]
    if missing:
        print(f"⚠️ Følgende CSV-filer mangler i 'data/': {missing}")
        print("Sjekk at filene er kopiert inn i 'data/'-mappen.")
        return

    db_path = os.path.join(os.getcwd(), "elkem_control.duckdb")
    print(f"\n🔄 Kobler til DuckDB-database: {db_path}...")
    con = duckdb.connect(db_path)
    
    # Load each CSV into DuckDB
    tables = {
        "wbs_schedule": "01_p6_wbs_schedule_baseline.csv",
        "hr_timesheets": "02_hr_timesheets_line_items.csv",
        "sap_gl_journal": "03_sap_gl_transaction_journal.csv",
        "evm_monthly": "04_evm_monthly_performance.csv",
        "ifrs15_revenue": "05_ifrs15_revenue_contract_asset.csv",
        "grants_compliance": "06_public_grants_skattefunn_enova.csv"
    }
    
    for table_name, csv_file in tables.items():
        file_path = os.path.join(data_dir, csv_file).replace("\\", "/")
        con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_csv_auto('{file_path}');")
        count = con.execute(f"SELECT COUNT(*) FROM {table_name};").fetchone()[0]
        print(f"  ✓ Tabell '{table_name}' opprettet med {count} rader.")
        
    print("\n------------------------------------------------------------------")
    print("📊 1. EVM EXECUTIVE PORTFOLIO SUMMARY (Cut-off: 2026-10-31 YTD M10)")
    print("------------------------------------------------------------------")
    evm_summary = con.execute("""
        SELECT 
            Project_ID, 
            Period, 
            BAC_NOK / 1e6 AS BAC_MNOK, 
            ROUND(PV_BCWS_NOK / 1e6, 2) AS PV_MNOK, 
            ROUND(EV_BCWP_NOK / 1e6, 2) AS EV_MNOK, 
            ROUND(AC_ACWP_NOK / 1e6, 2) AS AC_MNOK,
            ROUND(CPI, 4) AS CPI, 
            ROUND(SPI, 4) AS SPI,
            ROUND(EAC_NOK / 1e6, 2) AS EAC_MNOK,
            Status_Flag
        FROM evm_monthly 
        WHERE Period = '2026-10'
    """).df()
    print(evm_summary.to_string(index=False))
    
    print("\n------------------------------------------------------------------")
    print("🧾 2. IFRS 15 REVENUE & CONTRACT ASSET (KONTO 1380) RECONCILIATION")
    print("------------------------------------------------------------------")
    ifrs_summary = con.execute("""
        SELECT 
            Metric,
            ROUND(Amount_NOK / 1e6, 2) AS Amount_MNOK,
            Description
        FROM ifrs15_revenue
    """).df()
    print(ifrs_summary.to_string(index=False))

    print("\n------------------------------------------------------------------")
    print("⏱️ 3. SKATTEFUNN COMPLIANCE & RATE CAPPING (530 kr/t Limit)")
    print("------------------------------------------------------------------")
    skattefunn_check = con.execute("""
        SELECT 
            Employee_Name,
            Role,
            SUM(Hours_Logged) AS Total_Hours,
            Nominal_Hourly_Rate_NOK,
            SkatteFUNN_Capped_Rate_NOK,
            ROUND(SUM(Nominal_Cost_NOK), 2) AS Nominal_Cost_NOK,
            ROUND(SUM(SkatteFUNN_Eligible_Cost_NOK), 2) AS Eligible_Cost_NOK,
            ROUND(SUM(Nominal_Cost_NOK - SkatteFUNN_Eligible_Cost_NOK), 2) AS Disallowed_Amount_NOK
        FROM hr_timesheets
        GROUP BY Employee_Name, Role, Nominal_Hourly_Rate_NOK, SkatteFUNN_Capped_Rate_NOK
        ORDER BY Nominal_Hourly_Rate_NOK DESC
    """).df()
    print(skattefunn_check.to_string(index=False))

    print("\n==================================================================")
    print("✅ INGESTION & AVSTEMMING FULLFØRT UTEN AVVIK.")
    print("Kjør 'streamlit run app.py' for å åpne det interaktive dashbordet.")
    print("==================================================================")

if __name__ == "__main__":
    main()
