from fastapi import APIRouter

from app.api.v1.complaints import router as complaints_router
from app.api.v1.health import router as health_router
from app.api.v1.knowledge import router as knowledge_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router, tags=["health"])
api_router.include_router(complaints_router, tags=["complaints"])
api_router.include_router(knowledge_router, tags=["knowledge"])

__all__ = ["api_router"]
