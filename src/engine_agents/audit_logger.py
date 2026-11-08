"""
COSO 2013 & EU AI Act Art. 12 Audit Logger
==========================================
Maintains an immutable, tamper-evident, append-only log chain
for all agentic decisions, financial model executions, and
Human-in-the-Loop (HITL) approval gates.
"""

import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


class AuditLogger:
    """
    Cryptographically chained audit logger complying with:
    - COSO 2013 Internal Controls
    - EU AI Act Art. 12 Record-Keeping Requirements for High-Risk AI
    """

    def __init__(self, log_dir: Optional[str] = None):
        if log_dir is None:
            self.log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/audit_logs"))
        else:
            self.log_dir = log_dir

        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "audit_trail.jsonl")

    def _get_last_entry_hash(self) -> str:
        """Retrieves the SHA-256 hash of the most recent audit entry (genesis hash if empty)."""
        if not os.path.exists(self.log_file):
            return "0" * 64

        last_line = ""
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    last_line = line.strip()

        if not last_line:
            return "0" * 64

        try:
            data = json.loads(last_line)
            return data.get("entry_hash", "0" * 64)
        except Exception:
            return "0" * 64

    def log_event(
        self,
        event_type: str,           # e.g., "EVM_CALCULATION", "HITL_APPROVAL", "GRANT_AUDIT"
        control_account_id: str,
        actor: str,                # e.g., "Frank Ellingsen", "Variance_Agent_v1"
        action: str,               # e.g., "EAC_PROGNOSIS_ADJUSTMENT"
        details: Dict[str, Any],
        hitl_status: str = "AUTO"  # "AUTO", "PENDING_APPROVAL", "APPROVED", "REJECTED"
    ) -> Dict[str, Any]:
        """
        Appends a hash-chained audit event to the JSONL log file.
        """
        prev_hash = self._get_last_entry_hash()
        timestamp = datetime.now(timezone.utc).isoformat()

        entry_payload = {
            "timestamp": timestamp,
            "event_type": event_type,
            "control_account_id": control_account_id,
            "actor": actor,
            "action": action,
            "details": details,
            "hitl_status": hitl_status,
            "previous_hash": prev_hash
        }

        # Calculate entry hash
        serialized = json.dumps(entry_payload, sort_keys=True)
        entry_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        entry_payload["entry_hash"] = entry_hash

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry_payload) + "\n")

        return entry_payload

    def verify_chain_integrity(self) -> bool:
        """
        Verifies the cryptographic hash chain of the entire audit log.
        Returns True if intact, False if tampered.
        """
        if not os.path.exists(self.log_file):
            return True

        expected_prev_hash = "0" * 64
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                if not line.strip():
                    continue
                entry = json.loads(line)
                actual_prev = entry.get("previous_hash")
                entry_hash = entry.get("entry_hash")

                if actual_prev != expected_prev_hash:
                    return False

                # Recompute hash
                payload_copy = dict(entry)
                payload_copy.pop("entry_hash", None)
                serialized = json.dumps(payload_copy, sort_keys=True)
                recomputed = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

                if recomputed != entry_hash:
                    return False

                expected_prev_hash = entry_hash

        return True

    def get_recent_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns the most recent N audit entries."""
        if not os.path.exists(self.log_file):
            return []

        entries = []
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))

        return entries[-limit:]

