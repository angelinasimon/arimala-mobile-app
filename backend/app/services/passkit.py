import os
import httpx
from typing import Tuple, Optional

from app.services.passkit_auth import make_passkit_jwt

BASE_URL = os.getenv("PASSKIT_BASE_URL", "https://api.passkit.com")

def passkit_client() -> httpx.Client:
    jwt = make_passkit_jwt(ttl_seconds=60)
    return httpx.Client(
        base_url=BASE_URL,
        headers={
            "Authorization": f"Bearer {jwt}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        timeout=float(os.getenv("HTTP_TIMEOUT_SECONDS", "5")),
    )

def validate_pass(pass_id: str) -> Tuple[bool, Optional[str], Optional[dict]]:
    """
    Validate a digital pass via the PassKit API.
    Returns:
        (is_valid, reason_if_invalid, payload_dict_or_none)
    """
    try:
        with passkit_client() as client:
            response = client.get(f"/pass/{pass_id}")

        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "").upper()

            if status == "REVOKED":
                return False, "Pass is revoked", data
            elif status == "EXPIRED":
                return False, "Pass is expired", data
            else:
                return True, None, data

        elif response.status_code == 404:
            return False, "Pass not found", None

        else:
            return False, f"Unexpected PassKit error ({response.status_code})", None

    except httpx.RequestError as e:
        return False, f"HTTP error: {e}", None

    except Exception as e:
        return False, f"Internal validation error: {e}", None
