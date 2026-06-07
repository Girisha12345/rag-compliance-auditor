from __future__ import annotations

from fastapi import APIRouter

from backend.config import get_settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }
