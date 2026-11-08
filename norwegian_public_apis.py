"""
Norwegian Public APIs Integration Module (Root Compatibility Wrapper)
======================================================================
Re-exports from src.integrations.norwegian_public_apis
"""

from src.integrations.norwegian_public_apis import (
    PublicRegistryConnector,
    GrantRegistryConnector
)

if __name__ == "__main__":
    print("--- VENDOR CHECK ---")
    print(PublicRegistryConnector.verify_vendor("922995481"))
    print("\n--- GRANT STATUS ---")
    print(GrantRegistryConnector.get_grant_status("GRANT-2024-1042"))
