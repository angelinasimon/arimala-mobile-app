# tests/test_guest_limit.py
from unittest.mock import patch
from app.services import passkit
import uuid

def test_guest_limit_exceeded(client, test_event, test_member):
    payload = {
        "event_id": str(test_event.id),
        "member_id": str(test_member.id),
        "pass_id": test_member.pass_id,
        "pass_serial": None,
        "mode": "in",
        "kind": "membership_pass",
        "guests": 10,
        "scanned_by": "tester"
    }

    with patch.object(passkit, "validate_pass", return_value=(True, None, {"status": "ACTIVE"})):
        response = client.post("/api/v1/scan", json=payload)

    assert response.status_code == 400
    assert "only bring up to" in response.json()["detail"]
