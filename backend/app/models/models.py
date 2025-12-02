from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
import enum
import uuid
from datetime import datetime, timezone

from app.db import Base



class ExampleItem(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    # add other fields as needed

class MembershipType(enum.Enum):
    FAMILY = "Family"
    PATRON = "Patron"
    LIFE = "Life"
    INDIVIDUAL = "Individual"

class Event(Base):
    __tablename__ = "events"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    starts_at: Mapped[datetime]
    ends_at: Mapped[datetime | None] = mapped_column(nullable=True)
    location: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

class Member(Base):
    __tablename__ = "members"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str]
    email: Mapped[str | None]
    membership_type: Mapped[MembershipType]
    pass_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

class Scan(Base):
    __tablename__ = "scans"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("events.id"))
    member_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("members.id"), nullable=True)
    pass_id: Mapped[str]
    pass_serial: Mapped[str | None]
    mode: Mapped[str]  # "in" or "out"
    kind: Mapped[str] = mapped_column(String, default="membership_pass")
    guests: Mapped[int] = mapped_column(default=0)
    is_valid: Mapped[bool]
    validation_reason: Mapped[str | None]
    scanned_by: Mapped[str] = mapped_column(default="unknown")
    scanned_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    passkit_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    member = relationship("Member")
    event = relationship("Event")

    guest_details: Mapped[list["GuestDetail"]] = relationship(
        "GuestDetail",
        cascade="all, delete-orphan",
        back_populates="scan",
    )


class GuestDetail(Base):
    __tablename__ = "guest_details"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scans.id", ondelete="CASCADE"))
    name: Mapped[str | None]
    contact: Mapped[str | None]
    notes: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    scan: Mapped["Scan"] = relationship("Scan", back_populates="guest_details")

    
