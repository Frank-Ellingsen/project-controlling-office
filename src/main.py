"""
Main Application Entrypoint
===========================
Exports FastAPI app for Uvicorn / Docker container.
Powered by openapi_server with interactive dashboard and complete OpenAPI 3.1 endpoints.
"""

from openapi_server import app

__all__ = ["app"]
