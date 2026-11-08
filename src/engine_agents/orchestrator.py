"""
Multi-Agent Orchestrator & Dual-Mode Chat Router
================================================
Handles natural language questions by routing between:
1. Structured Data Engine (SQL / EVM / Financial Compute)
2. VectorDB RAG (Elkem Kunnskapsbase / Policies / Grants)
3. Hybrid Mode (Combines live numbers with policy rules)
4. Action Request (HITL gate for external integrations)
"""

from typing import Dict, Any, List
import json


class IntentType:
    STRUCTURED_DATA = "STRUCTURED_DATA"  # EVM, CPI/SPI, Cost, Actuals, EAC
    VECTOR_RAG = "VECTOR_RAG"            # IFRS 15, Enova, SkatteFUNN, Stage-Gate rules
    HYBRID = "HYBRID"                    # Compliance check on live project numbers
    ACTION_REQUEST = "ACTION_REQUEST"    # Create PowerPoint, sync to Teams, trigger API


class OrchestratorRouter:
    """
    Ruter innkommende spørsmål fra Chat-grensesnittet (Streamlit/Teams/Office)
    til riktig underagent.
    """
    
    def __init__(self):
        # Nøkkelord for utledningslogikk (Intent Classification)
        self.data_keywords = ["cpi", "spi", "eac", "bcws", "bcwp", "acwp", "kostnad", "avvik", "budsjett", "faktisk"]
        self.rag_keywords = ["regel", "regelverk", "retningslinje", "ifrs", "ias", "skattefunn", "enova", "krav", "stage-gate"]
        self.action_keywords = ["powerpoint", "teams", "faktura", "altinn", "skatteetaten", "send", "opprett", "rapport"]

    def classify_intent(self, query: str) -> str:
        q_lower = query.lower()
        has_data = any(k in q_lower for k in self.data_keywords)
        has_rag = any(k in q_lower for k in self.rag_keywords)
        has_action = any(k in q_lower for k in self.action_keywords)

        if has_action:
            return IntentType.ACTION_REQUEST
        if has_data and has_rag:
            return IntentType.HYBRID
        elif has_data:
            return IntentType.STRUCTURED_DATA
        else:
            return IntentType.VECTOR_RAG

    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        intent = self.classify_intent(query)
        
        response = {
            "query": query,
            "intent": intent,
            "routing_target": None,
            "execution_plan": []
        }

        if intent == IntentType.STRUCTURED_DATA:
            response["routing_target"] = "evm_data_agent"
            response["execution_plan"] = [
                "1. Ekstraher prosjekt-ID og datofelt fra spørsmål",
                "2. Kjør SQL/Python-spørring mot EVM Compute Engine",
                "3. Generer strukturert tabell og nøkkeltallsanalyse"
            ]

        elif intent == IntentType.VECTOR_RAG:
            response["routing_target"] = "rag_kunnskapsbase_agent"
            response["execution_plan"] = [
                "1. Generer Qdrant hybrid vector embeddings",
                "2. Hent relevante passasjer fra Elkem Kunnskapsbase (Drive)",
                "3. Syntetiser kildebelagt svar med kildehenvisninger"
            ]

        elif intent == IntentType.HYBRID:
            response["routing_target"] = "hybrid_compliance_agent"
            response["execution_plan"] = [
                "1. Hent faktiske prosjekttall fra EVM Compute Engine",
                "2. Søk etter relevante grenseverdier og krav i Qdrant VectorDB",
                "3. Verifiser samsvar og formuler avviksrapport med anbefalte tiltak"
            ]

        elif intent == IntentType.ACTION_REQUEST:
            response["routing_target"] = "integration_action_agent"
            response["execution_plan"] = [
                "1. Identifiser ekstern integrasjon (Teams / Power BI / Skatteetaten / PowerPoint)",
                "2. Bygg datalast eller meldingsobjekt",
                "3. Send til HITL (Human-in-the-Loop) tollbooth for godkjenning før eksekvering"
            ]

        return response


if __name__ == "__main__":
    router = OrchestratorRouter()
    sample_query = "Er avviket på CPI for prosjekt CA-1042 innenfor Enova sine retningslinjer for godkjente FoU-kostnader?"
    print(json.dumps(router.process_query(sample_query), indent=2, ensure_ascii=False))

