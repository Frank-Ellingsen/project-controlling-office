"""
DuckDB Local Analytics Store (Root Compatibility Wrapper)
=========================================================
Re-exports from src.engine_compute.duckdb_store
"""

from src.engine_compute.duckdb_store import (
    DuckDBStore,
    FinanceDataStore,
    DuckDBStoreManager
)

__all__ = [
    "DuckDBStore",
    "FinanceDataStore",
    "DuckDBStoreManager"
]

if __name__ == "__main__":
    store = DuckDBStoreManager("data/elkem_analytics.duckdb")
    print("DuckDB Store initialized successfully!")
    print(store.get_project_actuals("CA-2045"))
