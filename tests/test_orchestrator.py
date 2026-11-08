"""
Unit Tests for Multi-Agent Orchestrator & Router
================================================
Verifies intent classification across:
- Structured data (EVM, actuals, CPI/SPI)
- Vector RAG (IFRS 15, IAS 38, Enova, SkatteFUNN)
- Hybrid compliance queries
- Action requests (PowerPoint, Teams, ERP export)
"""

import unittest
from src.engine_agents.orchestrator import OrchestratorRouter, IntentType


class TestOrchestratorRouter(unittest.TestCase):

    def setUp(self):
        self.router = OrchestratorRouter()

    def test_structured_data_intent(self):
        query = "Hva er CPI og EAC for prosjekt CA-1042?"
        intent = self.router.classify_intent(query)
        self.assertEqual(intent, IntentType.STRUCTURED_DATA)
        
        res = self.router.process_query(query)
        self.assertEqual(res["routing_target"], "evm_data_agent")

    def test_vector_rag_intent(self):
        query = "Hva er reglene for SkatteFUNN godkjenning og krav til dokumentasjon?"
        intent = self.router.classify_intent(query)
        self.assertEqual(intent, IntentType.VECTOR_RAG)

        res = self.router.process_query(query)
        self.assertEqual(res["routing_target"], "rag_kunnskapsbase_agent")

    def test_hybrid_intent(self):
        query = "Er kostnad på prosjektet i henhold til Enova sine retningslinjer for FoU?"
        intent = self.router.classify_intent(query)
        self.assertEqual(intent, IntentType.HYBRID)

        res = self.router.process_query(query)
        self.assertEqual(res["routing_target"], "hybrid_compliance_agent")

    def test_action_request_intent(self):
        query = "Send varsel til Teams og opprett en PowerPoint rapport for prosjektgjennomgangen"
        intent = self.router.classify_intent(query)
        self.assertEqual(intent, IntentType.ACTION_REQUEST)

        res = self.router.process_query(query)
        self.assertEqual(res["routing_target"], "integration_action_agent")


if __name__ == "__main__":
    unittest.main()

