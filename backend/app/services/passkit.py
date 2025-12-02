import os
import httpx
import logging
from typing import Tuple, Optional

from app.services.passkit_auth import make_passkit_jwt

logger = logging.getLogger(__name__)

IS_STUB_MODE = os.getenv("ENV", "prod") == "dev"
BASE_URL = os.getenv("PASSKIT_BASE_URL", "https://api.passkit.com")

class PasskitValidationError(Exception):
    pass

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
    if IS_STUB_MODE:
        return True, None, {"passId": pass_id, "status": "ACTIVE", "stub_mode": True}

    try:
        with passkit_client() as client:
            response = client.get(f"/pass/{pass_id}")
            response.raise_for_status()

            data = response.json()
            status = data.get("status", "").upper()

            if status == "REVOKED":
                return False, "Pass is revoked", data
            elif status == "EXPIRED":
                return False, "Pass is expired", data
            else:
                return True, None, data

    except httpx.HTTPStatusError as e:
        logger.error(f"PassKit HTTP error: {e.response.status_code} - {e.response.text}")
        raise PasskitValidationError(f"PassKit error: {e.response.status_code}")

    except httpx.RequestError as e:
        logger.error(f"PassKit network error: {e}")
        raise PasskitValidationError("Network error during PassKit validation")

    except Exception as e:
        logger.exception("Unexpected error during PassKit validation")
        raise PasskitValidationError("Unexpected internal error during pass validation")
