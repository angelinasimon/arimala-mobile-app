from datetime import datetime, timedelta, timezone

from app.models.models import Event


def _create_event(db, **kwargs):
    event = Event(**kwargs)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def test_list_events_active_only(client, db):
    now = datetime.now(timezone.utc)
    active = _create_event(
        db,
        name="Active Event",
        starts_at=now - timedelta(hours=1),
        ends_at=now + timedelta(hours=1),
        location="Hall A",
        created_at=now,
    )
    _create_event(
        db,
        name="Past Event",
        starts_at=now - timedelta(days=2),
        ends_at=now - timedelta(days=1),
        location="Hall B",
        created_at=now - timedelta(days=2),
    )
    _create_event(
        db,
        name="Upcoming Event",
        starts_at=now + timedelta(days=1),
        ends_at=now + timedelta(days=2),
        location="Hall C",
        created_at=now,
    )

    response = client.get("/api/v1/events?active_only=true")
    assert response.status_code == 200
    event_ids = {row["id"] for row in response.json()}
    assert str(active.id) in event_ids
    assert len(event_ids) == 1


def test_list_events_returns_all_when_not_filtered(client, db):
    now = datetime.now(timezone.utc)
    early = _create_event(
        db,
        name="Early Event",
        starts_at=now - timedelta(days=1),
        ends_at=now - timedelta(hours=12),
        location="Hall 1",
        created_at=now - timedelta(days=1),
    )
    late = _create_event(
        db,
        name="Late Event",
        starts_at=now + timedelta(days=1),
        ends_at=now + timedelta(days=2),
        location="Hall 2",
        created_at=now,
    )

    response = client.get("/api/v1/events")
    assert response.status_code == 200
    names = [row["name"] for row in response.json()]
    assert set(names) == {early.name, late.name}
