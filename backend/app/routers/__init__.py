# app/routers/__init__.py
from fastapi import APIRouter
from app.routers import scan, events, dashboard

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(scan.router)
api_router.include_router(events.router)
api_router.include_router(dashboard.router)
