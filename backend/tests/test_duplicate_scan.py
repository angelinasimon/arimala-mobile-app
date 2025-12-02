# tests/test_duplicate_scan.py
from unittest.mock import patch
from app.services import passkit
import uuid

def test_duplicate_scan(client, test_event, test_member):
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

    with patch.object(passkit, "validate_pass", return_value=(True, None, {"status": "ACTIVE"})):
        # First scan (should succeed)
        r1 = client.post("/api/v1/scan", json=payload)
        assert r1.status_code == 200

        # Second scan (should fail as duplicate)
        r2 = client.post("/api/v1/scan", json=payload)
        assert r2.status_code == 409
        assert "Duplicate" in r2.json()["detail"]
