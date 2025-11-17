# app/schemas/scan.py
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class ScanIn(BaseModel):
    event_id: UUID
    member_id: Optional[UUID] = None
    pass_id: str
    pass_serial: Optional[str] = None
    mode: str = Field(default="in")
    guests: int = Field(default=0)
    scanned_by: Optional[str] = "unknown"

class ScanOut(BaseModel):
    id: UUID
    scanned_at: datetime
    is_valid: bool
    validation_reason: Optional[str] = None
