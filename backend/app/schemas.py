from datetime import datetime
from typing import Literal

from pydantic import BaseModel

Platform = Literal["douyin", "video_channel", "xiaohongshu"]


class Account(BaseModel):
    id: str
    platform: Platform
    nickname: str
    follower_count: int
    video_count: int


class VideoStat(BaseModel):
    id: str
    account_id: str
    platform: Platform
    title: str
    plays: int
    likes: int
    comments: int
    shares: int
    published_at: datetime


class PlatformBreakdown(BaseModel):
    platform: Platform
    account_count: int
    total_plays: int
    total_followers: int


class DashboardSummary(BaseModel):
    total_accounts: int
    total_videos: int
    total_plays: int
    total_followers: int
    by_platform: list[PlatformBreakdown]
    top_videos: list[VideoStat]
