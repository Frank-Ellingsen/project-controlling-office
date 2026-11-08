"""
DuckDB Local Analytics Store & Financial Data Warehouse
======================================================
Lightweight OLAP database integration for high-performance SQL queries
on time registrations, procurement actuals, WBS structures, and EVM S-curves.

Designed for local-first, low-cost analytical workloads (DuckDB).
"""

import os
from typing import Dict, Any, List, Optional
import duckdb
import pandas as pd


class DuckDBStore:
    """
    Local DuckDB OLAP database for project controlling, actuals aggregation,
    and WBS-level EVM analytics.
    """

    def __init__(self, db_path: str = "data/elkem_analytics.duckdb"):
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self.db_path = db_path
        self._init_schema()

    def get_connection(self):
        return duckdb.connect(self.db_path)

    def _init_schema(self):
        with self.get_connection() as conn:
            # 1. WBS Structure
            conn.execute("""
                CREATE TABLE IF NOT EXISTS wbs_nodes (
                    wbs_id VARCHAR PRIMARY KEY,
                    project_id VARCHAR,
                    name VARCHAR,
                    parent_id VARCHAR,
                    budget_bac DOUBLE
                );
            """)

            # 2. Time Registrations (Timer)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS time_entries (
                    entry_id VARCHAR PRIMARY KEY,
                    wbs_id VARCHAR,
                    employee_id VARCHAR,
                    work_date DATE,
                    hours_logged DOUBLE,
                    hourly_rate DOUBLE,
                    grant_eligible BOOLEAN DEFAULT TRUE
                );
            """)

            # 3. Procurement / Actuals (Innkjøp)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS procurement_actuals (
                    po_id VARCHAR PRIMARY KEY,
                    wbs_id VARCHAR,
                    vendor_name VARCHAR,
                    amount_nok DOUBLE,
                    booking_date DATE,
                    category VARCHAR
                );
            """)

            # 4. S-Curve & EVM Time Series Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fact_monthly_actuals (
                    id VARCHAR PRIMARY KEY,
                    project_id VARCHAR,
                    period_month VARCHAR NOT NULL,
                    monthly_pv DOUBLE NOT NULL,
                    monthly_ev DOUBLE NOT NULL,
                    monthly_ac DOUBLE NOT NULL,
                    cum_pv DOUBLE NOT NULL,
                    cum_ev DOUBLE NOT NULL,
                    cum_ac DOUBLE NOT NULL,
                    invoiced_amount DOUBLE DEFAULT 0.0
                );
            """)

    def seed_sample_data(self):
        """Populates sample WBS nodes, time entries, and procurement data."""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM procurement_actuals;")
            conn.execute("DELETE FROM time_entries;")
            conn.execute("DELETE FROM wbs_nodes;")
            conn.execute("DELETE FROM fact_monthly_actuals;")

            # WBS
            conn.execute("""
                INSERT INTO wbs_nodes VALUES
                ('WBS-1.2.4', 'CA-1042', 'Subsea Pilot Module Development', NULL, 10000000.0),
                ('WBS-2.1.0', 'CA-2088', 'Silicon Battery Anode R&D', NULL, 25000000.0),
                ('WBS-3.3.1', 'CA-3015', 'Fiskaa Furnace Digital Twin', NULL, 8000000.0);
            """)

            # Time Entries
            conn.execute("""
                INSERT INTO time_entries VALUES
                ('T-001', 'WBS-1.2.4', 'EMP-101', '2025-01-15', 160.0, 650.0, TRUE),
                ('T-002', 'WBS-1.2.4', 'EMP-102', '2025-01-20', 150.0, 520.0, TRUE),
                ('T-003', 'WBS-1.2.4', 'EMP-103', '2025-02-10', 170.0, 480.0, TRUE);
            """)

            # Procurement Actuals
            conn.execute("""
                INSERT INTO procurement_actuals VALUES
                ('PO-901', 'WBS-1.2.4', 'Kongsberg Maritime', 1500000.0, '2025-01-25', 'Pressure Testing Kit'),
                ('PO-902', 'WBS-1.2.4', 'Aker Solutions', 2000000.0, '2025-02-15', 'Pilot Sensor Array');
            """)

            # Monthly Actuals for S-Curve
            conn.execute("""
                INSERT INTO fact_monthly_actuals VALUES
                ('M-01', 'CA-1042', '2025-01', 500000, 480000, 490000, 500000, 480000, 490000, 0),
                ('M-02', 'CA-1042', '2025-02', 500000, 470000, 510000, 1000000, 950000, 1000000, 500000),
                ('M-03', 'CA-1042', '2025-03', 500000, 450000, 520000, 1500000, 1400000, 1520000, 0);
            """)

    def query_evm_actuals(self, project_id: str) -> Dict[str, Any]:
        """Beregner samlede faktiske kostnader (ACWP) for et prosjekt via CTE-aggregasjon for å unngå kartesisk vifteeffekt."""
        with self.get_connection() as conn:
            query = """
                WITH labor AS (
                    SELECT 
                        w.project_id,
                        COALESCE(SUM(t.hours_logged * t.hourly_rate), 0) AS labor_cost
                    FROM wbs_nodes w
                    JOIN time_entries t ON w.wbs_id = t.wbs_id
                    WHERE w.project_id = ?
                    GROUP BY w.project_id
                ),
                procurement AS (
                    SELECT 
                        w.project_id,
                        COALESCE(SUM(p.amount_nok), 0) AS procurement_cost
                    FROM wbs_nodes w
                    JOIN procurement_actuals p ON w.wbs_id = p.wbs_id
                    WHERE w.project_id = ?
                    GROUP BY w.project_id
                )
                SELECT 
                    w.project_id,
                    COALESCE(l.labor_cost, 0) AS labor_cost,
                    COALESCE(p.procurement_cost, 0) AS procurement_cost,
                    COALESCE(l.labor_cost, 0) + COALESCE(p.procurement_cost, 0) AS total_acwp
                FROM (SELECT DISTINCT project_id FROM wbs_nodes WHERE project_id = ?) w
                LEFT JOIN labor l ON w.project_id = l.project_id
                LEFT JOIN procurement p ON w.project_id = p.project_id;
            """
            res = conn.execute(query, [project_id, project_id, project_id]).fetchone()
            if res:
                return {
                    "project_id": res[0],
                    "labor_cost_nok": float(res[1]),
                    "procurement_cost_nok": float(res[2]),
                    "total_acwp_nok": float(res[3])
                }
            return {"project_id": project_id, "labor_cost_nok": 0.0, "procurement_cost_nok": 0.0, "total_acwp_nok": 0.0}

    def get_s_curve_data(self, project_id: str) -> pd.DataFrame:
        """Retrieves cumulative PV, EV, AC for S-Curve plotting."""
        with self.get_connection() as conn:
            query = """
                SELECT 
                    period_month,
                    cum_pv AS "Planned Value (PV)",
                    cum_ev AS "Earned Value (EV)",
                    cum_ac AS "Actual Cost (AC)"
                FROM fact_monthly_actuals
                WHERE project_id = ?
                ORDER BY period_month ASC;
            """
            return conn.execute(query, [project_id]).df()


# Alias for backward compatibility with previous design
FinanceDataStore = DuckDBStore


class DuckDBStoreManager:
    """
    Styrer den lokale OLAP DuckDB-databasen for Elkem Technology Controller Hub.
    Inkluderer WBS Control Accounts og transaksjonsledgere for FoU-tilskudd.
    """
    
    def __init__(self, db_path: str = "data/elkem_analytics.duckdb"):
        self.db_path = db_path
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self.init_tables()

    def get_connection(self):
        return duckdb.connect(self.db_path)

    def init_tables(self):
        conn = self.get_connection()
        try:
            # 1. WBS Control Accounts Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS wbs_control_accounts (
                    control_account_id VARCHAR PRIMARY KEY,
                    control_account_name VARCHAR,
                    project_domain VARCHAR,
                    cam_person VARCHAR,
                    grant_funding_body VARCHAR,
                    bac_nok DOUBLE,
                    contract_value_nok DOUBLE,
                    invoiced_to_date_nok DOUBLE,
                    status VARCHAR
                )
            """)

            # 2. Timecard & Actual Costs Ledger
            conn.execute("""
                CREATE TABLE IF NOT EXISTS actual_costs (
                    transaction_id VARCHAR PRIMARY KEY,
                    control_account_id VARCHAR,
                    period_date VARCHAR,
                    labor_cost_nok DOUBLE,
                    procurement_cost_nok DOUBLE,
                    subcontractor_cost_nok DOUBLE,
                    eligible_grant_cost_nok DOUBLE,
                    FOREIGN KEY (control_account_id) REFERENCES wbs_control_accounts(control_account_id)
                )
            """)

            # Insert sample Elkem R&D data if empty
            count = conn.execute("SELECT COUNT(*) FROM wbs_control_accounts").fetchone()[0]
            if count == 0:
                self._seed_sample_data(conn)
        finally:
            conn.close()

    def _seed_sample_data(self, conn):
        # Seed WBS Control Accounts
        conn.execute("""
            INSERT INTO wbs_control_accounts VALUES
            ('CA-2045', 'Fiskå Carbon-Neutral Smelting Pilot Plant', 'Process Development & Pilot Plant', 'Dr. Håkon Olsen', 'Enova', 45000000.0, 50000000.0, 18000000.0, 'ACTIVE'),
            ('CA-1042', 'Furnace Automation & Digital Twin System', 'Furnace Technology & Automation', 'Ingeniør Marianne Lie', 'NFR', 10000000.0, 12500000.0, 3000000.0, 'ACTIVE'),
            ('CA-3080', 'NextGen Battery Anode Material R&D', 'Silicon & Carbon Solutions', 'Kjell Arne Bakke', 'SkatteFUNN', 15000000.0, 16500000.0, 8500000.0, 'ACTIVE')
        """)

        # Seed Actual Costs Transactions
        conn.execute("""
            INSERT INTO actual_costs VALUES
            ('TX-1001', 'CA-2045', '2026-08-31', 12400000.0, 8000000.0, 3000000.0, 21400000.0),
            ('TX-1002', 'CA-1042', '2026-08-31', 2100000.0, 1200000.0, 500000.0, 3500000.0),
            ('TX-1003', 'CA-3080', '2026-08-31', 4500000.0, 2400000.0, 1000000.0, 7500000.0)
        """)

    def get_project_actuals(self, control_account_id: str) -> Dict[str, Any]:
        conn = self.get_connection()
        try:
            res = conn.execute("""
                SELECT 
                    w.control_account_id,
                    w.control_account_name,
                    w.project_domain,
                    w.cam_person,
                    w.grant_funding_body,
                    w.bac_nok,
                    COALESCE(SUM(a.labor_cost_nok), 0) as labor_cost_nok,
                    COALESCE(SUM(a.procurement_cost_nok), 0) as procurement_cost_nok,
                    COALESCE(SUM(a.subcontractor_cost_nok), 0) as subcontractor_cost_nok,
                    COALESCE(SUM(a.labor_cost_nok + a.procurement_cost_nok + a.subcontractor_cost_nok), 0) as total_acwp_nok
                FROM wbs_control_accounts w
                LEFT JOIN actual_costs a ON w.control_account_id = a.control_account_id
                WHERE w.control_account_id = ?
                GROUP BY w.control_account_id, w.control_account_name, w.project_domain, w.cam_person, w.grant_funding_body, w.bac_nok
            """, [control_account_id]).fetchone()

            if not res:
                return {}

            return {
                "control_account_id": res[0],
                "control_account_name": res[1],
                "project_domain": res[2],
                "cam_person": res[3],
                "grant_funding_body": res[4],
                "bac_nok": res[5],
                "labor_cost_nok": res[6],
                "procurement_cost_nok": res[7],
                "subcontractor_cost_nok": res[8],
                "total_acwp_nok": res[9]
            }
        finally:
            conn.close()


if __name__ == "__main__":
    store = DuckDBStore()
    store.seed_sample_data()
    print("DuckDB Store initialized and seeded!")
    print(store.query_evm_actuals("CA-1042"))
