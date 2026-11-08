"""
Development Bootstrap Script
============================
Initializes local environment, builds DuckDB tables, and verifies system readiness.

Usage:
    python scripts/bootstrap_dev.py
"""

import os
import sys

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def check_env():
    env_file = ".env"
    if not os.path.exists(env_file):
        print("  -> Creating .env from defaults")
        with open(".env", "w", encoding="utf-8") as dst:
            dst.write(
                "LOG_LEVEL=INFO\n"
                "OLLAMA_HOST=http://127.0.0.1:11434\n"
                "OLLAMA_MODEL=llama3.1\n"
                "EMBEDDING_MODEL=nomic-embed-text\n"
                "QDRANT_HOST=http://127.0.0.1:6333\n"
            )
    else:
        print("  -> .env file verified.")

def init_duckdb():
    from src.engine_compute.duckdb_store import DuckDBStore
    os.makedirs("data", exist_ok=True)
    db_path = "data/elkem_analytics.duckdb"
    store = DuckDBStore(db_path=db_path)
    store.seed_sample_data()
    print(f"  -> DuckDB database initialized at {db_path} with WBS, Time Entries, Procurement and S-Curve tables.")

def main():
    print("=====================================================")
    print("   ELKEM CONTROLLER HUB — DEV BOOTSTRAP INITIALIZER  ")
    print("=====================================================")
    
    print("\n[BOOTSTRAP] Step 1: Checking environment config...")
    check_env()
    
    print("\n[BOOTSTRAP] Step 2: Initializing DuckDB storage...")
    init_duckdb()
    
    print("\n=====================================================")
    print(" ✅ Bootstrap complete!")
    print(" Next steps:")
    print("   1. Start Docker containers : docker compose up --build")
    print("   2. Launch Streamlit UI     : streamlit run src/ui_frontend/app.py")
    print("   3. Access FastAPI Docs     : http://localhost:8000/docs")
    print("=====================================================")

if __name__ == "__main__":
    main()

