"""
Power BI Push Pipeline (Root Compatibility Wrapper)
===================================================
Re-exports from src.integrations.powerbi_push
"""

import json
from src.integrations.powerbi_push import PowerBIPushPipeline

if __name__ == "__main__":
    pbi = PowerBIPushPipeline()
    print("=== POWER BI PUSH PIPELINE RESULT ===")
    print(json.dumps(pbi.push_scurve_data("CA-1042"), indent=2))
