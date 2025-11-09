from fastapi import FastAPI

from . import db  # import database setup (to be created)
from .api import routes  # import API routes (to be created)

app = FastAPI(title="Arimala Admin API")

# Include API routers (assuming routes.py will define an APIRouter)
app.include_router(routes.api_router)

# Optionally, add a simple health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}
