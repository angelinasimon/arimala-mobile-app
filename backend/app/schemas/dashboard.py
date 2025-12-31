from pydantic import BaseModel
from typing import Dict, List
from uuid import UUID
from datetime import datetime


class MembershipBreakdown(BaseModel):
    members: int
    guests: int


class ArrivalBucket(BaseModel):
    time: datetime
    check_ins: int
    guests: int


class EventSummary(BaseModel):
    event_id: UUID
    total_check_ins: int
    total_guests: int
    by_membership_type: Dict[str, MembershipBreakdown]


class EventStats(EventSummary):
    arrivals: List[ArrivalBucket]
