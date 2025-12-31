from collections import defaultdict
from datetime import datetime
from typing import Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.models import Scan
from app.schemas.dashboard import (
    EventStats,
    EventSummary,
    MembershipBreakdown,
    ArrivalBucket,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _aggregate_by_membership(scans: List[Scan]) -> Dict[str, MembershipBreakdown]:
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

    return {
        k: MembershipBreakdown(members=v["members"], guests=v["guests"])
        for k, v in breakdown.items()
    }


def _bucket_arrivals(scans: List[Scan]) -> List[ArrivalBucket]:
    """
    Bucket arrivals by minute to power the arrival-time chart.
    """
    buckets: Dict[datetime, Dict[str, int]] = defaultdict(lambda: {"check_ins": 0, "guests": 0})
    for s in scans:
        bucket_time = s.scanned_at.replace(second=0, microsecond=0)
        buckets[bucket_time]["check_ins"] += 1
        buckets[bucket_time]["guests"] += s.guests

    return [
        ArrivalBucket(time=ts, check_ins=data["check_ins"], guests=data["guests"])
        for ts, data in sorted(buckets.items(), key=lambda item: item[0])
    ]


@router.get("/events/{event_id}/summary", response_model=EventSummary)
def event_summary(event_id: UUID, db: Session = Depends(get_db)):
    scans = db.query(Scan).filter(Scan.event_id == event_id, Scan.mode == "in").all()

    if not scans:
        raise HTTPException(status_code=404, detail="No scans found for this event.")

    total_check_ins = len(scans)
    total_guests = sum(s.guests for s in scans)

    by_type = _aggregate_by_membership(scans)

    return EventSummary(
        event_id=event_id,
        total_check_ins=total_check_ins,
        total_guests=total_guests,
        by_membership_type=by_type,
    )


@router.get("/events/{event_id}/stats", response_model=EventStats)
def event_stats(event_id: UUID, db: Session = Depends(get_db)):
    scans = db.query(Scan).filter(Scan.event_id == event_id, Scan.mode == "in").all()

    if not scans:
        raise HTTPException(status_code=404, detail="No scans found for this event.")

    total_check_ins = len(scans)
    total_guests = sum(s.guests for s in scans)

    by_type = _aggregate_by_membership(scans)
    arrivals = _bucket_arrivals(scans)

    return EventStats(
        event_id=event_id,
        total_check_ins=total_check_ins,
        total_guests=total_guests,
        by_membership_type=by_type,
        arrivals=arrivals,
    )
