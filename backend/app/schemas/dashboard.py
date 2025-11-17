from pydantic import BaseModel
from typing import Dict, Optional
from uuid import UUID

class MembershipBreakdown(BaseModel):
    members: int
    guests: int

class EventSummary(BaseModel):
    event_id: UUID
    total_check_ins: int
    total_guests: int
    by_membership_type: Dict[str, MembershipBreakdown]
