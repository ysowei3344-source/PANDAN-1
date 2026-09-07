import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from .. import storage
from ..auth import hash_password, require_role
from ..schemas import ActivityLogEntry, BindIdentityInput, UserCreateInput, UserOut, UserUpdateInput

router = APIRouter(prefix="/api/admin/users", tags=["users"])


def _public(user: dict) -> dict:
    return {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "identity_ids": user.get("identity_ids", []),
        "has_passcode": bool(user.get("passcode_hash")),
        "created_at": user["created_at"],
    }


@router.get("", response_model=list[UserOut], dependencies=[Depends(require_role("super_admin"))])
def list_users() -> list[dict]:
    return [_public(u) for u in storage.list_users()]


@router.post("", response_model=UserOut)
def create_user(payload: UserCreateInput, current: dict = Depends(require_role("super_admin"))) -> dict:
    if storage.get_user_by_username(payload.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    password_hash, salt = hash_password(payload.password)

    passcode_hash = passcode_salt = None
    if payload.passcode:
        passcode_hash, passcode_salt = hash_password(payload.passcode)

    user = {
        "id": f"u-{uuid.uuid4().hex[:8]}",
        "username": payload.username,
        "password_hash": password_hash,
        "salt": salt,
        "role": payload.role,
        "identity_ids": [payload.identity_id] if payload.identity_id else [],
        "passcode_hash": passcode_hash,
        "passcode_salt": passcode_salt,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    storage.create_user(user)
    storage.log_activity(current["id"], current["username"], "创建账号", f"{payload.username}（{payload.role}）")
    return _public(user)


@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: str, payload: UserUpdateInput, current: dict = Depends(require_role("super_admin"))) -> dict:
    user = storage.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")

    updates: dict = {}
    if payload.username and payload.username != user["username"]:
        existing = storage.get_user_by_username(payload.username)
        if existing and existing["id"] != user_id:
            raise HTTPException(status_code=400, detail="用户名已存在")
        updates["username"] = payload.username
    if payload.password:
        password_hash, salt = hash_password(payload.password)
        updates["password_hash"] = password_hash
        updates["salt"] = salt
    if payload.passcode:
        passcode_hash, passcode_salt = hash_password(payload.passcode)
        updates["passcode_hash"] = passcode_hash
        updates["passcode_salt"] = passcode_salt

    if not updates:
        return _public(user)
    updated = storage.update_user(user_id, updates)
    storage.log_activity(current["id"], current["username"], "编辑账号", updated["username"])
    return _public(updated)


@router.delete("/{user_id}")
def delete_user(user_id: str, current: dict = Depends(require_role("super_admin"))) -> dict:
    if user_id == current["id"]:
        raise HTTPException(status_code=400, detail="不能删除自己")
    target = storage.get_user(user_id)
    if not storage.delete_user(user_id):
        raise HTTPException(status_code=404, detail="user not found")
    storage.log_activity(current["id"], current["username"], "删除账号", target["username"] if target else user_id)
    return {"ok": True}


@router.post("/{user_id}/identities", response_model=UserOut)
def bind_identity(user_id: str, payload: BindIdentityInput, current: dict = Depends(require_role("super_admin"))) -> dict:
    identity = storage.get_identity(payload.identity_id)
    if identity is None:
        raise HTTPException(status_code=404, detail="identity not found")
    user = storage.add_user_identity(user_id, payload.identity_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    storage.log_activity(current["id"], current["username"], "绑定矩阵号", f"{user['username']} ← {identity.name}")
    return _public(user)


@router.delete("/{user_id}/identities/{identity_id}", response_model=UserOut)
def unbind_identity(user_id: str, identity_id: str, current: dict = Depends(require_role("super_admin"))) -> dict:
    identity = storage.get_identity(identity_id)
    user = storage.remove_user_identity(user_id, identity_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    storage.log_activity(current["id"], current["username"], "解绑矩阵号", f"{user['username']} ← {identity.name if identity else identity_id}")
    return _public(user)


@router.get("/activity-log", response_model=list[ActivityLogEntry], dependencies=[Depends(require_role("super_admin"))])
def get_activity_log() -> list[dict]:
    return storage.list_activity(limit=300)
