"""
Qdrant Vector Ingestion Pipeline (Root Compatibility Wrapper)
=============================================================
Re-exports from src.engine_agents.ingest_kunnskapsbase
"""

import json
from src.engine_agents.ingest_kunnskapsbase import QdrantIngestPipeline

if __name__ == "__main__":
    pipeline = QdrantIngestPipeline()
    print("=== QDRANT INGEST PIPELINE CONFIG ===")
    print(json.dumps(pipeline.ingest_folder(), indent=2))
