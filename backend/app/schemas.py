from datetime import datetime
from typing import Literal

from pydantic import BaseModel

Platform = Literal["douyin", "video_channel", "xiaohongshu"]


class Account(BaseModel):
    """One platform binding (抖音/视频号/小红书) under a matrix identity."""

    id: str
    identity_id: str
    platform: Platform
    nickname: str
    avatar_url: str | None = None
    follower_count: int
    video_count: int


class Identity(BaseModel):
    """A matrix account as the operator thinks about it: one phone number /
    one persona, synced across whichever platforms it's registered on."""

    id: str
    name: str
    phone_number: str


class IdentitySummary(BaseModel):
    id: str
    name: str
    phone_number: str
    accounts: list[Account]
    total_followers: int
    total_videos: int
    total_ad_spend: float
    total_customers_added: int
    total_deals_closed: int


class VideoStat(BaseModel):
    id: str
    account_id: str
    platform: Platform
    title: str
    thumbnail_url: str
    poster_url: str
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
    identity_id: str | None = None
    has_passcode: bool = False
    created_at: str


class UserCreateInput(BaseModel):
    username: str
    password: str
    role: Role = "operator"
    identity_id: str | None = None
    passcode: str | None = None


class ActivityLogEntry(BaseModel):
    id: str
    user_id: str
    username: str
    action: str
    detail: str = ""
    created_at: str


class VerifyPasscodeInput(BaseModel):
    passcode: str


class Settings(BaseModel):
    brand_name: str = "房车"


class SettingsInput(BaseModel):
    brand_name: str


class MetricSummary(BaseModel):
    value: float
    change_pct: float
    series: list[float]


class OverviewTrend(BaseModel):
    dates: list[str]
    plays: list[float]
    new_followers: list[float]


class OverviewDiagnosis(BaseModel):
    model: str
    generated_at: str
    based_on: str
    risk: str
    opportunity: str


class AccountOverview(BaseModel):
    account_id: str
    account_label: str
    period_days: int
    today_metrics: dict[str, MetricSummary]
    trend: OverviewTrend
    diagnosis: OverviewDiagnosis
    alerts: list[str]


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
