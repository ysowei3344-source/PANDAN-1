import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, Header, HTTPException

from . import storage

SESSION_TTL = timedelta(days=7)


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 200_000)
    return digest.hex(), salt


def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    digest, _ = hash_password(password, salt)
    return hmac.compare_digest(digest, expected_hash)


def create_session(user_id: str) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = (datetime.now(timezone.utc) + SESSION_TTL).isoformat()
    storage.create_session(token, user_id, expires_at)
    return token


def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    token = authorization.removeprefix("Bearer ")
    session = storage.get_session(token)
    if session is None:
        raise HTTPException(status_code=401, detail="invalid or expired session")
    user = storage.get_user(session["user_id"])
    if user is None:
        raise HTTPException(status_code=401, detail="user not found")
    return user


def require_role(*roles: str):
    def _check(user: dict = Depends(get_current_user)) -> dict:
        if roles and user["role"] not in roles:
            raise HTTPException(status_code=403, detail="insufficient permissions")
        return user

    return _check
