from fastapi import APIRouter, Depends, HTTPException

from .. import storage
from ..auth import require_role
from ..mock_data import VIDEOS
from ..schemas import Account, AccountCreateInput, AccountUpdateInput, VideoStat

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.get("", response_model=list[Account])
def list_accounts() -> list[Account]:
    return storage.list_accounts()


@router.get("/{account_id}/videos", response_model=list[VideoStat])
def list_account_videos(account_id: str) -> list[VideoStat]:
    if storage.get_account(account_id) is None:
        raise HTTPException(status_code=404, detail="account not found")
    return [v for v in VIDEOS if v.account_id == account_id]


@router.post("", response_model=Account)
def create_account(payload: AccountCreateInput, current: dict = Depends(require_role("super_admin"))) -> Account:
    if storage.get_identity(payload.identity_id) is None:
        raise HTTPException(status_code=404, detail="identity not found")
    account = storage.create_account(payload.model_dump())
    storage.log_activity(current["id"], current["username"], "新增平台账号", f"{account.nickname}（{account.platform}）")
    return account


@router.put("/{account_id}", response_model=Account)
def update_account(account_id: str, payload: AccountUpdateInput, current: dict = Depends(require_role("super_admin"))) -> Account:
    account = storage.update_account(account_id, payload.model_dump())
    if account is None:
        raise HTTPException(status_code=404, detail="account not found")
    storage.log_activity(current["id"], current["username"], "编辑平台账号", account.nickname)
    return account


@router.delete("/{account_id}")
def delete_account(account_id: str, current: dict = Depends(require_role("super_admin"))) -> dict:
    account = storage.get_account(account_id)
    if account is None or not storage.delete_account(account_id):
        raise HTTPException(status_code=404, detail="account not found")
    storage.log_activity(current["id"], current["username"], "删除平台账号", account.nickname)
    return {"ok": True}
