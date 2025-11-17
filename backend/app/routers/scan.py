# app/routers/scan.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime

from app.db import SessionLocal
from app.models.models import Scan
from app.schemas.scan import ScanIn, ScanOut
from app.services.passkit import validate_pass

router = APIRouter(prefix="/scan", tags=["Scan"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/scan", response_model=ScanOut)
def scan_pass(payload: ScanIn, db: Session = Depends(get_db)):
    # 1. Check for duplicate scan
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
        raise HTTPException(status_code=400, detail="Duplicate scan detected.")

    # 2. Validate pass via PassKit API
    try:
        is_valid, reason, passkit_data = validate_pass(payload.pass_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PassKit validation failed: {e}")

    # 3. Save the scan
    new_scan = Scan(
        id=uuid4(),
        event_id=payload.event_id,
        member_id=payload.member_id,
        pass_id=payload.pass_id,
        pass_serial=payload.pass_serial,
        mode=payload.mode,
        guests=payload.guests,
        is_valid=is_valid,
        validation_reason=reason,
        scanned_by=payload.scanned_by or "unknown",
        scanned_at=datetime.utcnow(),
        passkit_payload=passkit_data,
    )

    db.add(new_scan)
    db.commit()
    db.refresh(new_scan)

    return ScanOut(
        id=new_scan.id,
        scanned_at=new_scan.scanned_at,
        is_valid=new_scan.is_valid,
        validation_reason=new_scan.validation_reason,
    )
