import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .schemas import Account, Banner, Identity, Member, Settings

DATA_DIR = Path(__file__).parent / "data"
BANNERS_FILE = DATA_DIR / "banners.json"
USERS_FILE = DATA_DIR / "users.json"
SESSIONS_FILE = DATA_DIR / "sessions.json"
SETTINGS_FILE = DATA_DIR / "settings.json"
ACTIVITY_FILE = DATA_DIR / "activity_log.json"
ACTIVITY_MAX_ENTRIES = 2000
MEMBERS_FILE = DATA_DIR / "members.json"
IDENTITIES_FILE = DATA_DIR / "identities.json"
ACCOUNTS_FILE = DATA_DIR / "accounts.json"


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


def update_user(user_id: str, data: dict) -> dict | None:
    users = list_users()
    for i, u in enumerate(users):
        if u["id"] == user_id:
            users[i] = {**u, **data}
            _write_json(USERS_FILE, users)
            return users[i]
    return None


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


# ---- Members (front-end registered users) ----

def _ensure_members_file() -> None:
    if not MEMBERS_FILE.exists():
        from .mock_data import MEMBERS

        _write_json(MEMBERS_FILE, [m.model_dump() for m in MEMBERS])


def list_members() -> list[Member]:
    _ensure_members_file()
    return [Member(**m) for m in _read_json(MEMBERS_FILE)]


def update_member_status(member_id: str, status: str) -> Member | None:
    _ensure_members_file()
    items = _read_json(MEMBERS_FILE)
    for i, m in enumerate(items):
        if m["id"] == member_id:
            items[i] = {**m, "status": status}
            _write_json(MEMBERS_FILE, items)
            return Member(**items[i])
    return None


# ---- Matrix identities + platform accounts ----
# Seeded once from mock_data on first read, then this file is the source of
# truth — editing/adding/deleting here is how real accounts replace the demo
# data, no code change needed.

def _ensure_identities_file() -> None:
    if not IDENTITIES_FILE.exists():
        from .mock_data import IDENTITIES

        _write_json(IDENTITIES_FILE, [i.model_dump() for i in IDENTITIES])


def _ensure_accounts_file() -> None:
    if not ACCOUNTS_FILE.exists():
        from .mock_data import ACCOUNTS

        _write_json(ACCOUNTS_FILE, [a.model_dump() for a in ACCOUNTS])


def list_identities() -> list[Identity]:
    _ensure_identities_file()
    return [Identity(**i) for i in _read_json(IDENTITIES_FILE)]


def get_identity(identity_id: str) -> Identity | None:
    return next((i for i in list_identities() if i.id == identity_id), None)


def create_identity(data: dict) -> Identity:
    _ensure_identities_file()
    items = _read_json(IDENTITIES_FILE)
    identity = {**data, "id": f"iden-{uuid.uuid4().hex[:8]}"}
    items.append(identity)
    _write_json(IDENTITIES_FILE, items)
    return Identity(**identity)


def update_identity(identity_id: str, data: dict) -> Identity | None:
    items = _read_json(IDENTITIES_FILE)
    for i, item in enumerate(items):
        if item["id"] == identity_id:
            items[i] = {**data, "id": identity_id}
            _write_json(IDENTITIES_FILE, items)
            return Identity(**items[i])
    return None


def delete_identity(identity_id: str) -> bool:
    items = _read_json(IDENTITIES_FILE)
    remaining = [i for i in items if i["id"] != identity_id]
    if len(remaining) == len(items):
        return False
    _write_json(IDENTITIES_FILE, remaining)
    return True


def list_accounts() -> list[Account]:
    _ensure_accounts_file()
    return [Account(**a) for a in _read_json(ACCOUNTS_FILE)]


def get_account(account_id: str) -> Account | None:
    return next((a for a in list_accounts() if a.id == account_id), None)


def create_account(data: dict) -> Account:
    _ensure_accounts_file()
    items = _read_json(ACCOUNTS_FILE)
    account = {**data, "id": f"acc-{uuid.uuid4().hex[:8]}"}
    items.append(account)
    _write_json(ACCOUNTS_FILE, items)
    return Account(**account)


def update_account(account_id: str, data: dict) -> Account | None:
    items = _read_json(ACCOUNTS_FILE)
    for i, item in enumerate(items):
        if item["id"] == account_id:
            items[i] = {**item, **data, "id": account_id}
            _write_json(ACCOUNTS_FILE, items)
            return Account(**items[i])
    return None


def delete_account(account_id: str) -> bool:
    items = _read_json(ACCOUNTS_FILE)
    remaining = [a for a in items if a["id"] != account_id]
    if len(remaining) == len(items):
        return False
    _write_json(ACCOUNTS_FILE, remaining)
    return True


def delete_accounts_by_identity(identity_id: str) -> None:
    items = _read_json(ACCOUNTS_FILE)
    remaining = [a for a in items if a["identity_id"] != identity_id]
    _write_json(ACCOUNTS_FILE, remaining)


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
