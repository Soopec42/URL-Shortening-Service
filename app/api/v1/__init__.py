from fastapi import APIRouter

from app.api.v1.short_urls import router as short_urls_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(short_urls_router)
