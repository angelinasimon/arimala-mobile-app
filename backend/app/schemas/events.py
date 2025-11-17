from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class EventIn(BaseModel):
    name: str
    starts_at: datetime
    ends_at: datetime | None = None
    location: str | None = None

class EventOut(BaseModel):
    id: UUID
    name: str
    starts_at: datetime
    ends_at: datetime | None
    location: str | None
    created_at: datetime

    class Config:
        orm_mode = True
