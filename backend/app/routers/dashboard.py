from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from collections import defaultdict

from app.db import SessionLocal, get_db
from app.models.models import Scan
from app.schemas.dashboard import EventSummary, MembershipBreakdown

router = APIRouter(prefix="/dashboard", tags=["dashboard"])



@router.get("/events/{event_id}/summary", response_model=EventSummary)
def event_summary(event_id: UUID, db: Session = Depends(get_db)):
    scans = db.query(Scan).filter(Scan.event_id == event_id, Scan.mode == "in").all()

    if not scans:
        raise HTTPException(status_code=404, detail="No scans found for this event.")

    total_check_ins = len(scans)
    total_guests = sum(s.guests for s in scans)

    breakdown = defaultdict(lambda: {"members": 0, "guests": 0})

    for s in scans:
        if s.member and s.member.membership_type:
            member_type = s.member.membership_type.value
        elif s.passkit_payload:
            member_type = s.passkit_payload.get("member_type", "Unknown")
        else:
            member_type = "Unknown"
        breakdown[member_type]["members"] += 1
        breakdown[member_type]["guests"] += s.guests

    by_type = {
        k: MembershipBreakdown(members=v["members"], guests=v["guests"])
        for k, v in breakdown.items()
    }

    return EventSummary(
        event_id=event_id,
        total_check_ins=total_check_ins,
        total_guests=total_guests,
        by_membership_type=by_type
    )
