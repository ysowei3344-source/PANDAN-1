from fastapi import APIRouter

from ..mock_data import ACCOUNTS, TODAY_STATS, VIDEOS
from ..schemas import DashboardSummary, Platform, PlatformBreakdown, TodayStats

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/today", response_model=TodayStats)
def get_today_stats() -> TodayStats:
    return TODAY_STATS


@router.get("/summary", response_model=DashboardSummary)
def get_summary() -> DashboardSummary:
    platforms: list[Platform] = ["douyin", "video_channel", "xiaohongshu"]

    by_platform = []
    for platform in platforms:
        platform_accounts = [a for a in ACCOUNTS if a.platform == platform]
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
        total_accounts=len(ACCOUNTS),
        total_videos=len(VIDEOS),
        total_plays=sum(v.plays for v in VIDEOS),
        total_followers=sum(a.follower_count for a in ACCOUNTS),
        by_platform=by_platform,
        top_videos=top_videos,
    )
