# tests/test_invalid_pass.py
from unittest.mock import patch
from app.services import passkit
import uuid

def test_invalid_pass(client, test_event, test_member):
    payload = {
        "event_id": str(test_event.id),
        "member_id": str(test_member.id),
        "pass_id": test_member.pass_id,
        "pass_serial": None,
        "mode": "in",
        "kind": "membership_pass",
        "guests": 1,
        "scanned_by": "tester"
    }

    # Simulate pass being expired
    with patch.object(passkit, "validate_pass", return_value=(False, "Pass is expired", {"status": "EXPIRED"})):
        response = client.post("/api/v1/scan", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["is_valid"] is False
    assert "expired" in body["validation_reason"].lower()
    assert body["guests"] == 1
    assert body["kind"] == "membership_pass"
    assert body["member_name"] == test_member.full_name
    assert body["guest_details"] == []
