# app/schemas/scan.py
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class GuestDetailIn(BaseModel):
    name: Optional[str] = Field(default=None, description="Guest full name")
    contact: Optional[str] = Field(default=None, description="Phone, email, or other notes")
    notes: Optional[str] = Field(default=None, description="Optional notes about the guest")


class GuestDetailOut(GuestDetailIn):
    id: UUID


class ScanIn(BaseModel):
    event_id: UUID
    member_id: Optional[UUID] = None
    pass_id: str
    pass_serial: Optional[str] = None
    mode: str = Field(default="in")

    # 👇 Added this so tests stop failing on missing "kind"
    kind: Optional[str] = Field(
        default="membership_pass",
        description="Type of scan: 'membership_pass' or 'event_ticket'",
    )

    guests: int = Field(default=0)
    scanned_by: Optional[str] = "unknown"
    guest_details: Optional[List[GuestDetailIn]] = None


class ScanOut(BaseModel):
    id: UUID
    scanned_at: datetime
    is_valid: bool
    validation_reason: Optional[str] = None
    guests: int
    kind: str
    membership_type: Optional[str] = None
    member_name: Optional[str] = None
    guest_details: List[GuestDetailOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
