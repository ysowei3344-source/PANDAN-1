from fastapi import APIRouter, Depends, Header, HTTPException

from .. import storage
from ..auth import create_session, get_current_user, verify_password
from ..schemas import LoginInput, UserOut

router = APIRouter(prefix="/api/admin/auth", tags=["auth"])


def _public(user: dict) -> dict:
    return {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "identity_ids": user.get("identity_ids", []),
        "created_at": user["created_at"],
    }


@router.post("/login")
def login(payload: LoginInput) -> dict:
    user = storage.get_user_by_username(payload.username)
    if user is None or not verify_password(payload.password, user["salt"], user["password_hash"]):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_session(user["id"])
    storage.log_activity(user["id"], user["username"], "登录")
    return {"token": token, "user": _public(user)}


@router.post("/logout")
def logout(authorization: str | None = Header(default=None)) -> dict:
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ")
        session = storage.get_session(token)
        if session:
            user = storage.get_user(session["user_id"])
            if user:
                storage.log_activity(user["id"], user["username"], "退出登录")
        storage.delete_session(token)
    return {"ok": True}


@router.get("/me", response_model=UserOut)
def me(user: dict = Depends(get_current_user)) -> dict:
    return _public(user)
