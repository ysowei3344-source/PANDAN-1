"""Create the first super_admin user.

Usage: .venv/bin/python scripts/seed_admin.py <username> <password>

Run once against a fresh deployment (empty app/data/users.json). Re-running
with a username that already exists is a no-op.
"""

import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import storage  # noqa: E402
from app.auth import hash_password  # noqa: E402


def main(username: str, password: str) -> None:
    if storage.get_user_by_username(username):
        print(f"user '{username}' already exists, skipping")
        return
    password_hash, salt = hash_password(password)
    storage.create_user(
        {
            "id": f"u-{uuid.uuid4().hex[:8]}",
            "username": username,
            "password_hash": password_hash,
            "salt": salt,
            "role": "super_admin",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    print(f"created super_admin '{username}'")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: seed_admin.py <username> <password>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
