# app/routers/__init__.py
from fastapi import APIRouter


# ✅ Delay sub-router imports until after router is created
api_router = APIRouter(prefix="/api/v1")


from app.routers import scan, events, dashboard


api_router.include_router(scan.router)
api_router.include_router(events.router)
api_router.include_router(dashboard.router)