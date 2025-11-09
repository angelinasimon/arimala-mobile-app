from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models import models

api_router = APIRouter(prefix="/api/v1")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@api_router.get("/items")
def list_items(db: Session = Depends(get_db)):
    # Example endpoint to list items
    items = db.query(models.ExampleItem).all()
    return items
