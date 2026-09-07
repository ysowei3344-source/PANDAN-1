import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .schemas import Banner, Settings

DATA_DIR = Path(__file__).parent / "data"
BANNERS_FILE = DATA_DIR / "banners.json"
USERS_FILE = DATA_DIR / "users.json"
SESSIONS_FILE = DATA_DIR / "sessions.json"
SETTINGS_FILE = DATA_DIR / "settings.json"
ACTIVITY_FILE = DATA_DIR / "activity_log.json"
ACTIVITY_MAX_ENTRIES = 2000


def _read_json(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, items: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


# ---- Banners ----

def _ensure_banners_file() -> None:
    if not BANNERS_FILE.exists():
        from .mock_data import BANNERS

        _write_json(BANNERS_FILE, [b.model_dump() for b in BANNERS])


def list_banners() -> list[Banner]:
    _ensure_banners_file()
    items = sorted(_read_json(BANNERS_FILE), key=lambda b: b["sort_order"])
    return [Banner(**b) for b in items]


def create_banner(data: dict) -> Banner:
    _ensure_banners_file()
    items = _read_json(BANNERS_FILE)
    banner = {**data, "id": f"b-{uuid.uuid4().hex[:8]}"}
    items.append(banner)
    _write_json(BANNERS_FILE, items)
    return Banner(**banner)


def update_banner(banner_id: str, data: dict) -> Banner | None:
    items = _read_json(BANNERS_FILE)
    for i, b in enumerate(items):
        if b["id"] == banner_id:
            items[i] = {**data, "id": banner_id}
            _write_json(BANNERS_FILE, items)
            return Banner(**items[i])
    return None


def delete_banner(banner_id: str) -> bool:
    items = _read_json(BANNERS_FILE)
    remaining = [b for b in items if b["id"] != banner_id]
    if len(remaining) == len(items):
        return False
    _write_json(BANNERS_FILE, remaining)
    return True


# ---- Users ----

def list_users() -> list[dict]:
    return _read_json(USERS_FILE)


def get_user(user_id: str) -> dict | None:
    return next((u for u in list_users() if u["id"] == user_id), None)


def get_user_by_username(username: str) -> dict | None:
    return next((u for u in list_users() if u["username"] == username), None)


def create_user(user: dict) -> dict:
    users = list_users()
    users.append(user)
    _write_json(USERS_FILE, users)
    return user


def delete_user(user_id: str) -> bool:
    users = list_users()
    remaining = [u for u in users if u["id"] != user_id]
    if len(remaining) == len(users):
        return False
    _write_json(USERS_FILE, remaining)
    return True


# ---- Settings ----

def get_settings() -> Settings:
    if not SETTINGS_FILE.exists():
        return Settings()
    return Settings(**json.loads(SETTINGS_FILE.read_text(encoding="utf-8")))


def update_settings(data: dict) -> Settings:
    settings = Settings(**data)
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(settings.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    return settings


# ---- Sessions ----

def create_session(token: str, user_id: str, expires_at: str) -> None:
    sessions = _read_json(SESSIONS_FILE)
    sessions.append({"token": token, "user_id": user_id, "expires_at": expires_at})
    _write_json(SESSIONS_FILE, sessions)


def get_session(token: str) -> dict | None:
    sessions = _read_json(SESSIONS_FILE)
    now = datetime.now(timezone.utc)
    for s in sessions:
        if s["token"] == token:
            if datetime.fromisoformat(s["expires_at"]) < now:
                return None
            return s
    return None


def delete_session(token: str) -> None:
    sessions = _read_json(SESSIONS_FILE)
    remaining = [s for s in sessions if s["token"] != token]
    _write_json(SESSIONS_FILE, remaining)


# ---- Activity log ----

def log_activity(user_id: str, username: str, action: str, detail: str = "") -> None:
    entries = _read_json(ACTIVITY_FILE)
    entries.append(
        {
            "id": f"log-{uuid.uuid4().hex[:10]}",
            "user_id": user_id,
            "username": username,
            "action": action,
            "detail": detail,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    if len(entries) > ACTIVITY_MAX_ENTRIES:
        entries = entries[-ACTIVITY_MAX_ENTRIES:]
    _write_json(ACTIVITY_FILE, entries)


def list_activity(limit: int = 200) -> list[dict]:
    entries = _read_json(ACTIVITY_FILE)
    return list(reversed(entries))[:limit]
