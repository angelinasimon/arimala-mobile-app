# app/routers/scan.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timezone

from app.db import get_db
from app.models.models import Scan, Member, Event, GuestDetail
from app.schemas.scan import ScanIn, ScanOut, GuestDetailOut
from app.services import passkit
from app.core.config import MEMBERSHIP_GUEST_LIMITS

router = APIRouter(prefix="/scan", tags=["Scan"])



@router.post("/", response_model=ScanOut)
def scan_pass(payload: ScanIn, db: Session = Depends(get_db)):
    # Input validation
    if payload.mode != "in":
        raise HTTPException(status_code=400, detail="Only mode='in' is supported.")

    if payload.kind not in ("membership_pass", "event_ticket"):
        raise HTTPException(status_code=400, detail="Invalid kind.")

    event = db.query(Event).filter(Event.id == payload.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")

    if payload.guests < 0:
        raise HTTPException(status_code=400, detail="Guests cannot be negative.")

    details_payload = payload.guest_details or []
    if details_payload and payload.guests not in (0, len(details_payload)):
        raise HTTPException(
            status_code=400,
            detail="guests must equal the number of guest_details entries or be omitted.",
        )

    guest_count = len(details_payload) if details_payload else payload.guests

    # Duplicate check
    duplicate = (
        db.query(Scan)
        .filter(
            Scan.event_id == payload.event_id,
            Scan.pass_id == payload.pass_id,
            Scan.mode == payload.mode,
        )
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="Duplicate scan detected.")

    # PassKit validation
    try:
        is_valid, reason, passkit_data = passkit.validate_pass(payload.pass_id)
    except passkit.PasskitValidationError as e:
        raise HTTPException(status_code=503, detail=str(e))

    # Guest limit enforcement
    member = None
    if payload.member_id:
        member = db.query(Member).filter(Member.id == payload.member_id).first()
        if not member:
            raise HTTPException(status_code=404, detail="Member not found.")

        max_guests = MEMBERSHIP_GUEST_LIMITS.get(member.membership_type.name, 0)
        if guest_count > max_guests:
            raise HTTPException(
                status_code=400,
                detail=f"{member.membership_type.value} members can only bring up to {max_guests} guests."
            )

    # Save the scan
    new_scan = Scan(
        id=uuid4(),
        event_id=payload.event_id,
        member_id=payload.member_id,
        pass_id=payload.pass_id,
        pass_serial=payload.pass_serial,
        mode=payload.mode,
        guests=guest_count,
        kind=payload.kind,
        is_valid=is_valid,
        validation_reason=reason,
        scanned_by=payload.scanned_by or "unknown",
        scanned_at=datetime.now(timezone.utc),
        passkit_payload=passkit_data,
    )

    if details_payload:
        new_scan.guest_details = [
            GuestDetail(
                id=uuid4(),
                scan=new_scan,
                name=detail.name,
                contact=detail.contact,
                notes=detail.notes,
            )
            for detail in details_payload
        ]

    db.add(new_scan)
    db.commit()
    db.refresh(new_scan)

    guest_detail_out = [
        GuestDetailOut(
            id=detail.id,
            name=detail.name,
            contact=detail.contact,
            notes=detail.notes,
        )
        for detail in new_scan.guest_details
    ]

    return ScanOut(
        id=new_scan.id,
        scanned_at=new_scan.scanned_at,
        is_valid=new_scan.is_valid,
        validation_reason=new_scan.validation_reason,
        guests=new_scan.guests,
        kind=new_scan.kind,
        membership_type=member.membership_type.value if member else None,
        member_name=member.full_name if member else None,
        guest_details=guest_detail_out,
    )
