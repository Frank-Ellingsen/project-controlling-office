"""
Unit Tests for COSO 2013 & EU AI Act Art. 12 Audit Logger
=========================================================
Tests append-only logging, SHA-256 hash chaining,
and cryptographic tamper detection.
"""

import unittest
import os
import json
import tempfile
from src.engine_agents.audit_logger import AuditLogger


class TestAuditLogger(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.logger = AuditLogger(log_dir=self.temp_dir)

    def tearDown(self):
        if os.path.exists(self.logger.log_file):
            try:
                os.remove(self.logger.log_file)
            except Exception:
                pass

    def test_log_event_and_hash_chain(self):
        # 1. First Entry (Genesis)
        e1 = self.logger.log_event(
            event_type="EVM_VARIANCE",
            control_account_id="CA-1042",
            actor="EVMCalculator",
            action="COST_SPIKE_DETECTED",
            details={"cpi": 0.92}
        )
        self.assertEqual(e1["previous_hash"], "0" * 64)
        self.assertIn("entry_hash", e1)

        # 2. Second Entry (Must chain from e1's hash)
        e2 = self.logger.log_event(
            event_type="HITL_APPROVAL",
            control_account_id="CA-1042",
            actor="Frank Ellingsen",
            action="EAC_APPROVED",
            details={"approved_amount": 10850000.0},
            hitl_status="APPROVED"
        )
        self.assertEqual(e2["previous_hash"], e1["entry_hash"])

        # 3. Integrity Check
        self.assertTrue(self.logger.verify_chain_integrity())

    def test_tamper_detection(self):
        # Create two valid entries
        self.logger.log_event(
            event_type="EVM_METRICS",
            control_account_id="CA-1042",
            actor="TestAgent",
            action="CHECK",
            details={"cpi": 1.0}
        )
        self.logger.log_event(
            event_type="EVM_METRICS",
            control_account_id="CA-2088",
            actor="TestAgent",
            action="CHECK",
            details={"cpi": 1.05}
        )
        self.assertTrue(self.logger.verify_chain_integrity())

        # Tamper with the log file by altering details in line 1
        with open(self.logger.log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        tampered = json.loads(lines[0])
        tampered["details"]["cpi"] = 0.50  # Fraudulent alteration
        lines[0] = json.dumps(tampered) + "\n"

        with open(self.logger.log_file, "w", encoding="utf-8") as f:
            f.writelines(lines)

        # Integrity verification must catch this tamper!
        self.assertFalse(self.logger.verify_chain_integrity())


if __name__ == "__main__":
    unittest.main()

