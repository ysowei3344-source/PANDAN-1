import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .schemas import (
    Account,
    Banner,
    Identity,
    Member,
    Order,
    Product,
    Settings,
    Tutorial,
)

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
TUTORIALS_FILE = DATA_DIR / "tutorials.json"
PRODUCTS_FILE = DATA_DIR / "products.json"
CUSTOMERS_FILE = DATA_DIR / "customers.json"
ORDERS_FILE = DATA_DIR / "orders.json"
AFTERSALES_FILE = DATA_DIR / "aftersales.json"


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
# identity_ids replaced the old singular identity_id (one operator can now
# manage several matrix identities). _normalize_user upgrades old records
# read from disk on the fly; any write drops the stale singular field.

def _normalize_user(user: dict) -> dict:
    if "identity_ids" in user:
        return user
    old = user.get("identity_id")
    return {**user, "identity_ids": [old] if old else []}


def list_users() -> list[dict]:
    return [_normalize_user(u) for u in _read_json(USERS_FILE)]


def get_user(user_id: str) -> dict | None:
    return next((u for u in list_users() if u["id"] == user_id), None)


def get_user_by_username(username: str) -> dict | None:
    return next((u for u in list_users() if u["username"] == username), None)


def create_user(user: dict) -> dict:
    users = _read_json(USERS_FILE)
    users.append(user)
    _write_json(USERS_FILE, users)
    return user


def update_user(user_id: str, data: dict) -> dict | None:
    users = _read_json(USERS_FILE)
    for i, u in enumerate(users):
        if u["id"] == user_id:
            users[i] = {**u, **data}
            _write_json(USERS_FILE, users)
            return _normalize_user(users[i])
    return None


def add_user_identity(user_id: str, identity_id: str) -> dict | None:
    users = _read_json(USERS_FILE)
    for i, u in enumerate(users):
        if u["id"] == user_id:
            ids = _normalize_user(u)["identity_ids"]
            if identity_id not in ids:
                ids = [*ids, identity_id]
            users[i] = {**u, "identity_ids": ids}
            users[i].pop("identity_id", None)
            _write_json(USERS_FILE, users)
            return users[i]
    return None


def remove_user_identity(user_id: str, identity_id: str) -> dict | None:
    users = _read_json(USERS_FILE)
    for i, u in enumerate(users):
        if u["id"] == user_id:
            ids = [x for x in _normalize_user(u)["identity_ids"] if x != identity_id]
            users[i] = {**u, "identity_ids": ids}
            users[i].pop("identity_id", None)
            _write_json(USERS_FILE, users)
            return users[i]
    return None


def delete_user(user_id: str) -> bool:
    users = _read_json(USERS_FILE)
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


# ---- Tutorials (使用教程管理 — 图文 how-to articles) ----

def list_tutorials(platform: str | None = None) -> list[Tutorial]:
    items = sorted(_read_json(TUTORIALS_FILE), key=lambda t: t.get("sort_order", 0))
    if platform is not None:
        items = [t for t in items if t["platform"] == platform]
    return [Tutorial(**t) for t in items]


def get_tutorial(tutorial_id: str) -> Tutorial | None:
    return next((t for t in list_tutorials() if t.id == tutorial_id), None)


def create_tutorial(data: dict) -> Tutorial:
    items = _read_json(TUTORIALS_FILE)
    now = datetime.now(timezone.utc).isoformat()
    tutorial = {**data, "id": f"tut-{uuid.uuid4().hex[:8]}", "created_at": now, "updated_at": now}
    items.append(tutorial)
    _write_json(TUTORIALS_FILE, items)
    return Tutorial(**tutorial)


def update_tutorial(tutorial_id: str, data: dict) -> Tutorial | None:
    items = _read_json(TUTORIALS_FILE)
    for i, item in enumerate(items):
        if item["id"] == tutorial_id:
            items[i] = {**item, **data, "id": tutorial_id, "updated_at": datetime.now(timezone.utc).isoformat()}
            _write_json(TUTORIALS_FILE, items)
            return Tutorial(**items[i])
    return None


def delete_tutorial(tutorial_id: str) -> bool:
    items = _read_json(TUTORIALS_FILE)
    remaining = [t for t in items if t["id"] != tutorial_id]
    if len(remaining) == len(items):
        return False
    _write_json(TUTORIALS_FILE, remaining)
    return True


# ---- Order tracking (products / customers / orders / after-sales) ----

def _ensure_products_file() -> None:
    if not PRODUCTS_FILE.exists():
        from .mock_data import PRODUCTS

        _write_json(PRODUCTS_FILE, [p.model_dump() for p in PRODUCTS])


def _normalize_product(p: dict) -> dict:
    if "main_image_urls" not in p:
        old_main = p.get("main_image_url")
        p = {**p, "main_image_urls": [old_main] if old_main else []}
    if "layout_urls" not in p:
        old_layout = p.get("layout_image_url")
        p = {**p, "layout_urls": [old_layout] if old_layout else []}
    if "optional_config" not in p:
        p = {**p, "optional_config": p.get("customer_notes", "")}
    return p


def list_products() -> list[Product]:
    _ensure_products_file()
    return [Product(**_normalize_product(p)) for p in _read_json(PRODUCTS_FILE)]


def get_product(product_id: str) -> Product | None:
    return next((p for p in list_products() if p.id == product_id), None)


def create_product(data: dict) -> Product:
    _ensure_products_file()
    items = _read_json(PRODUCTS_FILE)
    product = {**data, "id": f"prod-{uuid.uuid4().hex[:8]}", "created_at": datetime.now(timezone.utc).isoformat()}
    items.append(product)
    _write_json(PRODUCTS_FILE, items)
    return Product(**product)


def update_product(product_id: str, data: dict) -> Product | None:
    items = _read_json(PRODUCTS_FILE)
    for i, p in enumerate(items):
        if p["id"] == product_id:
            items[i] = {**p, **data, "id": product_id}
            _write_json(PRODUCTS_FILE, items)
            return Product(**items[i])
    return None


def delete_product(product_id: str) -> bool:
    items = _read_json(PRODUCTS_FILE)
    remaining = [p for p in items if p["id"] != product_id]
    if len(remaining) == len(items):
        return False
    _write_json(PRODUCTS_FILE, remaining)
    return True


ORDERS_MIGRATED_MARKER = DATA_DIR / ".orders_v2_migrated"


def _migrate_legacy_customers_orders_aftersales() -> list[dict]:
    """One-time merge of the old customers.json + orders.json + aftersales.json
    (customer tracked separately, matched to an order only once deal_closed)
    into the new unified orders.json (one record per customer opportunity,
    created directly, stage adjusted in place). Runs once, gated by
    ORDERS_MIGRATED_MARKER, so re-running the app never re-merges or
    clobbers anything written under the new shape."""
    customers = _read_json(CUSTOMERS_FILE) if CUSTOMERS_FILE.exists() else []
    legacy_orders = _read_json(ORDERS_FILE) if ORDERS_FILE.exists() else []
    legacy_aftersales = _read_json(AFTERSALES_FILE) if AFTERSALES_FILE.exists() else []
    order_by_customer = {o["customer_id"]: o for o in legacy_orders if "customer_id" in o}
    aftersales_by_customer = {a["customer_id"]: a for a in legacy_aftersales if "customer_id" in a}

    merged = []
    for c in customers:
        o = order_by_customer.get(c["id"], {})
        a = aftersales_by_customer.get(c["id"], {})
        merged.append({
            "id": c["id"].replace("cust-", "order-", 1) if c["id"].startswith("cust-") else f"order-{uuid.uuid4().hex[:8]}",
            "name": c.get("name", ""),
            "phone": c.get("phone", ""),
            "source": c.get("source", ""),
            "financial_status": c.get("financial_status", ""),
            "product_id": o.get("product_id") or c.get("intended_product_id"),
            "stage": c.get("stage", "initial_chat"),
            "assigned_to": c.get("assigned_to") or "",
            "ai_wechat": c.get("ai_wechat", ""),
            "notes": c.get("notes", ""),
            "amount": o.get("amount", 0),
            "signed_at": o.get("signed_at"),
            "delivered_at": a.get("delivered_at"),
            "aftersales_status": a.get("status", ""),
            "aftersales_notes": a.get("notes", ""),
            "created_at": c.get("created_at", datetime.now(timezone.utc).isoformat()),
            "updated_at": c.get("updated_at", c.get("created_at", datetime.now(timezone.utc).isoformat())),
        })
    return merged


def _ensure_orders_file() -> None:
    if ORDERS_MIGRATED_MARKER.exists():
        if not ORDERS_FILE.exists():
            _write_json(ORDERS_FILE, [])
        return
    if CUSTOMERS_FILE.exists() or ORDERS_FILE.exists() or AFTERSALES_FILE.exists():
        _write_json(ORDERS_FILE, _migrate_legacy_customers_orders_aftersales())
    else:
        from .mock_data import ORDERS as MOCK_ORDERS

        _write_json(ORDERS_FILE, [o.model_dump() for o in MOCK_ORDERS])
    ORDERS_MIGRATED_MARKER.write_text("done", encoding="utf-8")


def list_orders() -> list[Order]:
    _ensure_orders_file()
    return [Order(**o) for o in _read_json(ORDERS_FILE)]


def get_order(order_id: str) -> Order | None:
    return next((o for o in list_orders() if o.id == order_id), None)


def create_order(data: dict) -> Order:
    _ensure_orders_file()
    items = _read_json(ORDERS_FILE)
    now = datetime.now(timezone.utc).isoformat()
    order = {**data, "id": f"order-{uuid.uuid4().hex[:8]}", "created_at": now, "updated_at": now}
    items.append(order)
    _write_json(ORDERS_FILE, items)
    return Order(**order)


def update_order(order_id: str, data: dict) -> Order | None:
    items = _read_json(ORDERS_FILE)
    for i, o in enumerate(items):
        if o["id"] == order_id:
            items[i] = {**o, **data, "id": order_id, "updated_at": datetime.now(timezone.utc).isoformat()}
            _write_json(ORDERS_FILE, items)
            return Order(**items[i])
    return None


def delete_order(order_id: str) -> bool:
    items = _read_json(ORDERS_FILE)
    remaining = [o for o in items if o["id"] != order_id]
    if len(remaining) == len(items):
        return False
    _write_json(ORDERS_FILE, remaining)
    return True


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
