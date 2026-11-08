"""
Agent Orchestration & LLM Engine
================================
Dual-mode Chat Router, Intent Classifier, Model Provider Manager,
Vector DB Ingestion Pipeline, and COSO 2013 / EU AI Act Audit Logger.
"""

from .orchestrator import OrchestratorRouter, IntentType
from .llm_provider import ModelProviderManager
from .ingest_kunnskapsbase import QdrantIngestPipeline
from .audit_logger import AuditLogger

__all__ = [
    "OrchestratorRouter",
    "IntentType",
    "ModelProviderManager",
    "QdrantIngestPipeline",
    "AuditLogger"
]
