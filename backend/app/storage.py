import json
import uuid
from pathlib import Path

from .schemas import Banner

DATA_FILE = Path(__file__).parent / "data" / "banners.json"


def _ensure_file() -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        from .mock_data import BANNERS

        _write([b.model_dump() for b in BANNERS])


def _read() -> list[dict]:
    _ensure_file()
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def _write(items: list[dict]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def list_banners() -> list[Banner]:
    items = sorted(_read(), key=lambda b: b["sort_order"])
    return [Banner(**b) for b in items]


def create_banner(data: dict) -> Banner:
    items = _read()
    banner = {**data, "id": f"b-{uuid.uuid4().hex[:8]}"}
    items.append(banner)
    _write(items)
    return Banner(**banner)


def update_banner(banner_id: str, data: dict) -> Banner | None:
    items = _read()
    for i, b in enumerate(items):
        if b["id"] == banner_id:
            items[i] = {**data, "id": banner_id}
            _write(items)
            return Banner(**items[i])
    return None


def delete_banner(banner_id: str) -> bool:
    items = _read()
    remaining = [b for b in items if b["id"] != banner_id]
    if len(remaining) == len(items):
        return False
    _write(remaining)
    return True
