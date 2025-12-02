from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)
