"""
Main Application Entrypoint
===========================
Exports FastAPI app for Uvicorn / Docker container.
"""

from src.api.main import app

__all__ = ["app"]

