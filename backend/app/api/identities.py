from fastapi import APIRouter, Depends, HTTPException

from .. import storage, timeseries
from ..auth import MASTER_PASSCODE, get_current_user, require_role, verify_password
from ..mock_data import VIDEOS
from ..schemas import IdentityInput, IdentitySummary, VerifyPasscodeInput, VideoStat

router = APIRouter(prefix="/api/identities", tags=["identities"])

# No order-tracking system (M5) exists yet, so 总成交数 has nothing real to
# read from — approximate it as a fixed share of customers added, purely so
# the card isn't empty. Replace with a real conversion once M5 is wired up.
_MOCK_DEAL_CONVERSION_RATE = 0.15


def _summary(identity) -> IdentitySummary:
    accounts = [a for a in storage.list_accounts() if a.identity_id == identity.id]

    days = timeseries.get_daily_series(identity.id)
    total_ad_spend = round(sum(d["ad_spend"] for d in days), 2)
    total_customers_added = sum(d["wechat_added"] for d in days)
    total_deals_closed = round(total_customers_added * _MOCK_DEAL_CONVERSION_RATE)

    operator = next((u for u in storage.list_users() if identity.id in u.get("identity_ids", [])), None)

    return IdentitySummary(
        id=identity.id,
        name=identity.name,
        phone_number=identity.phone_number,
        operator_username=operator["username"] if operator else None,
        accounts=accounts,
        total_followers=sum(a.follower_count for a in accounts),
        total_videos=sum(a.video_count for a in accounts),
        total_ad_spend=total_ad_spend,
        total_customers_added=total_customers_added,
        total_deals_closed=total_deals_closed,
    )


@router.get("", response_model=list[IdentitySummary])
def list_identities() -> list[IdentitySummary]:
    return [_summary(i) for i in storage.list_identities()]


@router.get("/{identity_id}", response_model=IdentitySummary)
def get_identity(identity_id: str) -> IdentitySummary:
    identity = storage.get_identity(identity_id)
    if identity is None:
        raise HTTPException(status_code=404, detail="identity not found")
    return _summary(identity)


@router.get("/{identity_id}/videos", response_model=list[VideoStat])
def list_identity_videos(identity_id: str) -> list[VideoStat]:
    if storage.get_identity(identity_id) is None:
        raise HTTPException(status_code=404, detail="identity not found")
    account_ids = {a.id for a in storage.list_accounts() if a.identity_id == identity_id}
    return [v for v in VIDEOS if v.account_id in account_ids]


@router.post("/{identity_id}/verify-passcode")
def verify_identity_passcode(identity_id: str, payload: VerifyPasscodeInput, current: dict = Depends(get_current_user)) -> dict:
    identity = storage.get_identity(identity_id)
    if identity is None:
        raise HTTPException(status_code=404, detail="identity not found")

    if payload.passcode == MASTER_PASSCODE:
        storage.log_activity(current["id"], current["username"], "口令验证成功（万能码）", identity.name)
        return {"ok": True}

    for user in storage.list_users():
        if identity_id in user.get("identity_ids", []) and user.get("passcode_hash"):
            if verify_password(payload.passcode, user["passcode_salt"], user["passcode_hash"]):
                storage.log_activity(current["id"], current["username"], "口令验证成功", identity.name)
                return {"ok": True}

    storage.log_activity(current["id"], current["username"], "口令验证失败", identity.name)
    raise HTTPException(status_code=403, detail="管理口令不正确")


@router.post("", response_model=IdentitySummary)
def create_identity(payload: IdentityInput, current: dict = Depends(require_role("super_admin"))) -> IdentitySummary:
    operator = None
    if payload.operator_user_id:
        operator = storage.get_user(payload.operator_user_id)
        if operator is None:
            raise HTTPException(status_code=404, detail="operator not found")

    identity = storage.create_identity({"name": payload.name, "phone_number": payload.phone_number})

    if operator is not None:
        storage.add_user_identity(operator["id"], identity.id)

    storage.log_activity(current["id"], current["username"], "新增矩阵号", identity.name)
    return _summary(identity)


@router.put("/{identity_id}", response_model=IdentitySummary)
def update_identity(identity_id: str, payload: IdentityInput, current: dict = Depends(get_current_user)) -> IdentitySummary:
    identity = storage.update_identity(identity_id, {"name": payload.name, "phone_number": payload.phone_number})
    if identity is None:
        raise HTTPException(status_code=404, detail="identity not found")
    storage.log_activity(current["id"], current["username"], "编辑矩阵号", identity.name)
    return _summary(identity)


@router.delete("/{identity_id}")
def delete_identity(identity_id: str, current: dict = Depends(require_role("super_admin"))) -> dict:
    identity = storage.get_identity(identity_id)
    if identity is None or not storage.delete_identity(identity_id):
        raise HTTPException(status_code=404, detail="identity not found")
    storage.delete_accounts_by_identity(identity_id)
    storage.log_activity(current["id"], current["username"], "删除矩阵号", identity.name)
    return {"ok": True}
