from fastapi import FastAPI

from . import db  # import database setup (to be created)
from app.routers import api_router# import API routes (to be created)

app = FastAPI(title="Arimala Admin API")

# Include API routers (assuming routes.py will define an APIRouter)
app.include_router(api_router)

# Optionally, add a simple health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}
