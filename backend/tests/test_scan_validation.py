from unittest.mock import patch
from uuid import uuid4

from app.services import passkit


def test_scan_with_unknown_event(client, test_member):
    payload = {
        "event_id": str(uuid4()),
        "member_id": str(test_member.id),
        "pass_id": test_member.pass_id,
        "pass_serial": None,
        "mode": "in",
        "kind": "membership_pass",
        "guests": 0,
        "scanned_by": "tester",
    }

    with patch.object(passkit, "validate_pass", return_value=(True, None, {})):
        response = client.post("/api/v1/scan", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found."


def test_scan_with_unknown_member(client, test_event):
    payload = {
        "event_id": str(test_event.id),
        "member_id": str(uuid4()),
        "pass_id": "FAKEPASS999",
        "pass_serial": None,
        "mode": "in",
        "kind": "membership_pass",
        "guests": 0,
        "scanned_by": "tester",
    }

    with patch.object(passkit, "validate_pass", return_value=(True, None, {})):
        response = client.post("/api/v1/scan", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Member not found."
