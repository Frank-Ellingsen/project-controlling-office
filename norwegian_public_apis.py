"""
Norwegian Public APIs Connector (Root Compatibility Wrapper)
============================================================
Re-exports from src.integrations.norwegian_public_apis
"""

import json
from src.integrations.norwegian_public_apis import (
    PublicRegistryConnector,
    GrantRegistryConnector,
    NorwegianPublicAPIsManager
)

__all__ = [
    "PublicRegistryConnector",
    "GrantRegistryConnector",
    "NorwegianPublicAPIsManager"
]

if __name__ == "__main__":
    api_mgr = NorwegianPublicAPIsManager()
    print("--- VENDOR BRREG CHECK ---")
    print(json.dumps(api_mgr.verify_vendor_brreg("997729803"), indent=2, ensure_ascii=False))

    print("\n--- SKATTEFUNN COMPLIANCE CHECK ---")
    print(json.dumps(api_mgr.check_skattefunn_rf1053b_compliance("298412", 550.0, 1900.0, 18000000.0), indent=2, ensure_ascii=False))
