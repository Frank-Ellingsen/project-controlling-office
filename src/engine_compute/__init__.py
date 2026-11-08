"""
Deterministic Calculation Engine
================================
EIA-748 Earned Value Management, IFRS 15 Revenue Recognition,
Norwegian Public Grant Computations (SkatteFUNN, Enova),
and DuckDB Analytical Data Store.

Core Axiom: Models Reason. Software Computes.
Zero LLM dependencies in this package.
"""

from .evm_calculator import EVMCalculator, EVMInput, EVMResult, EACType
from .grant_calculator import SkatteFUNNCalculator, SkatteFUNNInput, SkatteFUNNResult
from .duckdb_store import FinanceDataStore

__all__ = [
    "EVMCalculator",
    "EVMInput",
    "EVMResult",
    "EACType",
    "SkatteFUNNCalculator",
    "SkatteFUNNInput",
    "SkatteFUNNResult",
    "FinanceDataStore"
]
