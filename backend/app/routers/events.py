from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from uuid import UUID

from app.db import get_db
from app.models.models import Event
from app.schemas.events import EventIn, EventOut

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=EventOut)
def create_event(event_in: EventIn, db: Session = Depends(get_db)):
    event = Event(**event_in.dict())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/", response_model=list[EventOut])
def list_events(
    active_only: bool = False,
    as_of: datetime | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Event)

    if active_only:
        reference = as_of or datetime.now(timezone.utc)
        query = query.filter(
            Event.starts_at <= reference,
            or_(Event.ends_at.is_(None), Event.ends_at >= reference),
        )

    return query.order_by(Event.starts_at.desc()).all()


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: UUID, db: Session = Depends(get_db)):
    event = db.query(Event).get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
