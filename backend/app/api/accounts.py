from fastapi import APIRouter, HTTPException

from ..mock_data import ACCOUNTS, VIDEOS
from ..schemas import Account, VideoStat

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.get("", response_model=list[Account])
def list_accounts() -> list[Account]:
    return ACCOUNTS


@router.get("/{account_id}/videos", response_model=list[VideoStat])
def list_account_videos(account_id: str) -> list[VideoStat]:
    if not any(a.id == account_id for a in ACCOUNTS):
        raise HTTPException(status_code=404, detail="account not found")
    return [v for v in VIDEOS if v.account_id == account_id]
