# tests/test_valid_scan.py
from unittest.mock import patch
from app.services import passkit
import uuid

def test_valid_scan(client, test_event, test_member):
    payload = {
        "event_id": str(test_event.id),
        "member_id": str(test_member.id),
        "pass_id": test_member.pass_id,
        "pass_serial": None,
        "mode": "in",
        "kind": "membership_pass",
        "guests": 2,
        "scanned_by": "tester"
    }

    with patch.object(passkit, "validate_pass", return_value=(True, None, {"status": "ACTIVE"})):
        response = client.post("/api/v1/scan", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["is_valid"] is True
    assert body["guests"] == 2
    assert body["kind"] == "membership_pass"
    assert body["membership_type"] == "Family"
    assert body["member_name"] == test_member.full_name
    assert body["guest_details"] == []
