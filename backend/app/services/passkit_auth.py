import os, time, hmac, hashlib, base64, json
API_KEY = os.getenv("PASSKIT_API_KEY", "")
API_SECRET = os.getenv("PASSKIT_API_SECRET", "")
USERNAME = os.getenv("PASSKIT_USERNAME", "")
def _b64url(b: bytes) -> str: return base64.urlsafe_b64encode(b).decode().rstrip("=")
def make_passkit_jwt(ttl_seconds: int = 120) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {"uid": API_KEY, "username": USERNAME, "iat": now - 10, "exp": now + ttl_seconds}
    h = _b64url(json.dumps(header, separators=(",", ":")).encode())
    p = _b64url(json.dumps(payload, separators=(",", ":")).encode())
    sig = hmac.new(API_SECRET.encode(), f"{h}.{p}".encode(), hashlib.sha256).digest()
    return f"{h}.{p}.{_b64url(sig)}"