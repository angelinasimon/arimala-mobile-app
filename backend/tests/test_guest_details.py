from unittest.mock import patch

from app.services import passkit


def test_guest_details_auto_sets_guest_count(client, test_event, test_member):
    payload = {
        "event_id": str(test_event.id),
        "member_id": str(test_member.id),
        "pass_id": test_member.pass_id,
        "pass_serial": None,
        "mode": "in",
        "kind": "membership_pass",
        "guests": 0,
        "guest_details": [
            {"name": "Guest One", "contact": "guest1@example.com"},
            {"name": "Guest Two", "contact": None, "notes": "VIP"},
        ],
        "scanned_by": "tester",
    }

    with patch.object(passkit, "validate_pass", return_value=(True, None, {"status": "ACTIVE"})):
        response = client.post("/api/v1/scan", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["guests"] == 2
    assert len(data["guest_details"]) == 2
    assert {g["name"] for g in data["guest_details"]} == {"Guest One", "Guest Two"}


def test_guest_details_count_mismatch_rejected(client, test_event, test_member):
    payload = {
        "event_id": str(test_event.id),
        "member_id": str(test_member.id),
        "pass_id": test_member.pass_id,
        "mode": "in",
        "kind": "membership_pass",
        "guests": 1,
        "guest_details": [{"name": "Guest One"}, {"name": "Guest Two"}],
        "scanned_by": "tester",
    }

    with patch.object(passkit, "validate_pass", return_value=(True, None, {"status": "ACTIVE"})):
        response = client.post("/api/v1/scan", json=payload)

    assert response.status_code == 400
    assert "guests must equal" in response.json()["detail"]


def test_event_ticket_scan_without_member(client, test_event):
    payload = {
        "event_id": str(test_event.id),
        "member_id": None,
        "pass_id": "EVENTPASS123",
        "mode": "in",
        "kind": "event_ticket",
        "guests": 0,
        "scanned_by": "tester",
    }

    with patch.object(passkit, "validate_pass", return_value=(True, None, {"status": "ACTIVE"})):
        response = client.post("/api/v1/scan", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "event_ticket"
    assert body["membership_type"] is None
    assert body["guest_details"] == []
