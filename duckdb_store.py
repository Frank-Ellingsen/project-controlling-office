"""
DuckDB Local Analytics Store (Root Compatibility Wrapper)
=========================================================
Re-exports from src.engine_compute.duckdb_store
"""

from src.engine_compute.duckdb_store import DuckDBStore, FinanceDataStore

if __name__ == "__main__":
    store = DuckDBStore()
    store.seed_sample_data()
    print("DuckDB Store initialized successfully!")
    print(store.query_evm_actuals("CA-1042"))
