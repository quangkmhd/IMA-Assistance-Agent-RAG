"""Router registry for API v1."""

from .admin import router as admin_router
from .cache import router as cache_router
from .events import router as events_router
from .health import router as health_router
from .ingestion import router as ingestion_router
from .meetings import router as meetings_router
from .query import router as query_router

__all__ = [
    "admin_router",
    "cache_router",
    "events_router",
    "health_router",
    "ingestion_router",
    "meetings_router",
    "query_router",
]
