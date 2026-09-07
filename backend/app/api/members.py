from fastapi import APIRouter, Depends, HTTPException

from .. import storage
from ..auth import require_role
from ..schemas import Member

router = APIRouter(prefix="/api/admin/members", tags=["members"])


@router.get("", response_model=list[Member], dependencies=[Depends(require_role("super_admin"))])
def list_members() -> list[Member]:
    return storage.list_members()


@router.put("/{member_id}/status", response_model=Member)
def set_member_status(member_id: str, status: str, current: dict = Depends(require_role("super_admin"))) -> Member:
    if status not in ("active", "disabled"):
        raise HTTPException(status_code=400, detail="status must be active or disabled")
    member = storage.update_member_status(member_id, status)
    if member is None:
        raise HTTPException(status_code=404, detail="member not found")
    storage.log_activity(
        current["id"], current["username"],
        "启用会员" if status == "active" else "禁用会员",
        member.nickname,
    )
    return member
