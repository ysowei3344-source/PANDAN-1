import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from .. import storage
from ..auth import hash_password, require_role
from ..schemas import UserCreateInput, UserOut

router = APIRouter(prefix="/api/admin/users", tags=["users"])


def _public(user: dict) -> dict:
    return {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "created_at": user["created_at"],
    }


@router.get("", response_model=list[UserOut], dependencies=[Depends(require_role("super_admin"))])
def list_users() -> list[dict]:
    return [_public(u) for u in storage.list_users()]


@router.post("", response_model=UserOut, dependencies=[Depends(require_role("super_admin"))])
def create_user(payload: UserCreateInput) -> dict:
    if storage.get_user_by_username(payload.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    password_hash, salt = hash_password(payload.password)
    user = {
        "id": f"u-{uuid.uuid4().hex[:8]}",
        "username": payload.username,
        "password_hash": password_hash,
        "salt": salt,
        "role": payload.role,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    storage.create_user(user)
    return _public(user)


@router.delete("/{user_id}")
def delete_user(user_id: str, current: dict = Depends(require_role("super_admin"))) -> dict:
    if user_id == current["id"]:
        raise HTTPException(status_code=400, detail="不能删除自己")
    if not storage.delete_user(user_id):
        raise HTTPException(status_code=404, detail="user not found")
    return {"ok": True}
