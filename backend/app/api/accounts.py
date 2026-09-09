import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from .. import storage
from ..auth import require_role
from ..mock_data import VIDEOS
from ..schemas import Account, AccountCreateInput, AccountUpdateInput, VideoStat
from ..scraper_client import (
    SCRAPER_SERVICE_URL,
    SCRAPER_SERVICE_VIDEO_LIST_URL,
    ScraperError,
    call_scraper,
)

router = APIRouter(prefix="/api/accounts", tags=["accounts"])
logger = logging.getLogger(__name__)

# Platforms with a working video-list extractor (see ARCHIVE.md 9.11) —
# video_channel/xiaohongshu just get the profile-stat scrape below.
_VIDEO_LIST_PLATFORMS = {"douyin"}


def _auto_scrape_account(account_id: str, platform: str, url: str | None) -> None:
    """Runs in a background thread after the add/edit response has already
    gone back to the browser — the user shouldn't have to sit through a
    ~20s scrape just to save a pasted link. Best-effort: any scraper failure
    is logged and swallowed, leaving whatever the operator entered manually
    in place rather than surfacing an error after the fact."""
    if not url or not url.startswith("http") or not SCRAPER_SERVICE_URL:
        return

    updates: dict = {}
    try:
        result = call_scraper(SCRAPER_SERVICE_URL, {"platform": platform, "url": url})
        data = result.get("data") or {}
        for key in ("nickname", "avatar_url", "follower_count", "video_count"):
            value = data.get(key)
            if value not in (None, ""):
                updates[key] = value
    except ScraperError as e:
        logger.warning("auto-scrape profile failed for account %s: %s", account_id, e)

    if platform in _VIDEO_LIST_PLATFORMS:
        try:
            vresult = call_scraper(SCRAPER_SERVICE_VIDEO_LIST_URL, {"platform": platform, "url": url})
            items = vresult.get("items")
            if items:
                updates["recent_posts"] = items
        except ScraperError as e:
            logger.warning("auto-scrape video-list failed for account %s: %s", account_id, e)

    if not updates:
        return
    current = storage.get_account(account_id)
    if current is None:
        return
    storage.update_account(account_id, {**current.model_dump(), **updates})


@router.get("", response_model=list[Account])
def list_accounts() -> list[Account]:
    return storage.list_accounts()


@router.get("/{account_id}/videos", response_model=list[VideoStat])
def list_account_videos(account_id: str) -> list[VideoStat]:
    if storage.get_account(account_id) is None:
        raise HTTPException(status_code=404, detail="account not found")
    return [v for v in VIDEOS if v.account_id == account_id]


@router.post("", response_model=Account)
def create_account(
    payload: AccountCreateInput,
    background_tasks: BackgroundTasks,
    current: dict = Depends(require_role("super_admin")),
) -> Account:
    if storage.get_identity(payload.identity_id) is None:
        raise HTTPException(status_code=404, detail="identity not found")
    account = storage.create_account(payload.model_dump())
    storage.log_activity(current["id"], current["username"], "新增平台账号", f"{account.nickname}（{account.platform}）")
    background_tasks.add_task(_auto_scrape_account, account.id, account.platform, account.profile_url)
    return account


@router.put("/{account_id}", response_model=Account)
def update_account(
    account_id: str,
    payload: AccountUpdateInput,
    background_tasks: BackgroundTasks,
    current: dict = Depends(require_role("super_admin")),
) -> Account:
    account = storage.update_account(account_id, payload.model_dump())
    if account is None:
        raise HTTPException(status_code=404, detail="account not found")
    storage.log_activity(current["id"], current["username"], "编辑平台账号", account.nickname)
    background_tasks.add_task(_auto_scrape_account, account.id, account.platform, account.profile_url)
    return account


@router.delete("/{account_id}")
def delete_account(account_id: str, current: dict = Depends(require_role("super_admin"))) -> dict:
    account = storage.get_account(account_id)
    if account is None or not storage.delete_account(account_id):
        raise HTTPException(status_code=404, detail="account not found")
    storage.log_activity(current["id"], current["username"], "删除平台账号", account.nickname)
    return {"ok": True}
