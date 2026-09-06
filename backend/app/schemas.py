from datetime import datetime
from typing import Literal

from pydantic import BaseModel

Platform = Literal["douyin", "video_channel", "xiaohongshu"]


class Account(BaseModel):
    id: str
    platform: Platform
    nickname: str
    avatar_url: str | None = None
    follower_count: int
    video_count: int


class VideoStat(BaseModel):
    id: str
    account_id: str
    platform: Platform
    title: str
    thumbnail_url: str
    plays: int
    likes: int
    comments: int
    shares: int
    published_at: datetime
    deepseek_analysis: str


class Banner(BaseModel):
    id: str
    title: str
    subtitle: str
    image_url: str
    link_url: str | None = None
    sort_order: int


class BannerInput(BaseModel):
    title: str
    subtitle: str = ""
    image_url: str
    link_url: str | None = None
    sort_order: int = 0


class TodayStats(BaseModel):
    videos_published: int
    total_exposure: int
    dm_conversations: int
    wechat_added: int


Role = Literal["super_admin", "operator"]


class LoginInput(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: str
    username: str
    role: Role
    created_at: str


class UserCreateInput(BaseModel):
    username: str
    password: str
    role: Role = "operator"


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
