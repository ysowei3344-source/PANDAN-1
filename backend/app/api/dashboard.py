from fastapi import APIRouter, Depends, HTTPException

from .. import storage, timeseries
from ..auth import get_current_user
from ..mock_data import TODAY_STATS, VIDEOS
from ..schemas import AccountOverview, DashboardSummary, Platform, PlatformBreakdown, TodayStats

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/today", response_model=TodayStats)
def get_today_stats() -> TodayStats:
    return TODAY_STATS


@router.get("/overview", response_model=AccountOverview, dependencies=[Depends(get_current_user)])
def get_overview(account_id: str = "all", period: int = 7) -> dict:
    if period not in (7, 30):
        raise HTTPException(status_code=400, detail="period must be 7 or 30")
    overview = timeseries.get_overview(account_id, period)
    if overview is None:
        raise HTTPException(status_code=404, detail="account not found")
    return overview


@router.get("/summary", response_model=DashboardSummary)
def get_summary() -> DashboardSummary:
    accounts = storage.list_accounts()
    platforms: list[Platform] = ["douyin", "video_channel", "xiaohongshu"]

    by_platform = []
    for platform in platforms:
        platform_accounts = [a for a in accounts if a.platform == platform]
        platform_videos = [v for v in VIDEOS if v.platform == platform]
        by_platform.append(
            PlatformBreakdown(
                platform=platform,
                account_count=len(platform_accounts),
                total_plays=sum(v.plays for v in platform_videos),
                total_followers=sum(a.follower_count for a in platform_accounts),
            )
        )

    top_videos = sorted(VIDEOS, key=lambda v: v.plays, reverse=True)[:5]

    return DashboardSummary(
        total_accounts=len(accounts),
        total_videos=len(VIDEOS),
        total_plays=sum(v.plays for v in VIDEOS),
        total_followers=sum(a.follower_count for a in accounts),
        by_platform=by_platform,
        top_videos=top_videos,
    )
