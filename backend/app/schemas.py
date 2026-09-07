from datetime import datetime
from typing import Literal

from pydantic import BaseModel

Platform = Literal["douyin", "video_channel", "xiaohongshu"]


class Account(BaseModel):
    """One platform binding (抖音/视频号/小红书) under a matrix identity.

    profile_url is the pasted homepage link for the account. There's no
    official open-data API for any of the three platforms yet (Douyin's
    open-platform data permission is still pending approval, see ARCHIVE.md),
    so nickname/follower_count/video_count stay manually entered until a real
    adapter can be wired up to pull them from profile_url instead."""

    id: str
    identity_id: str
    platform: Platform
    nickname: str
    avatar_url: str | None = None
    profile_url: str | None = None
    follower_count: int
    video_count: int


class Identity(BaseModel):
    """A matrix account as the operator thinks about it: one persona, synced
    across whichever platforms it's registered on. Matched to (at most) one
    internal operator account rather than tracking its own phone number —
    see User.identity_id."""

    id: str
    name: str
    phone_number: str | None = None


class IdentitySummary(BaseModel):
    id: str
    name: str
    phone_number: str | None = None
    accounts: list[Account]
    total_followers: int
    total_videos: int
    total_ad_spend: float
    total_customers_added: int
    total_deals_closed: int


class IdentityInput(BaseModel):
    name: str
    phone_number: str | None = None
    operator_user_id: str | None = None


class AccountCreateInput(BaseModel):
    identity_id: str
    platform: Platform
    nickname: str = ""
    avatar_url: str | None = None
    profile_url: str | None = None
    follower_count: int = 0
    video_count: int = 0


class AccountUpdateInput(BaseModel):
    nickname: str = ""
    avatar_url: str | None = None
    profile_url: str | None = None
    follower_count: int = 0
    video_count: int = 0


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
    identity_ids: list[str] = []
    has_passcode: bool = False
    created_at: str


class UserCreateInput(BaseModel):
    username: str
    password: str
    role: Role = "operator"
    identity_id: str | None = None
    passcode: str | None = None


class BindIdentityInput(BaseModel):
    identity_id: str


class ActivityLogEntry(BaseModel):
    id: str
    user_id: str
    username: str
    action: str
    detail: str = ""
    created_at: str


MemberSource = Literal["h5", "mini_program"]
MemberStatus = Literal["active", "disabled"]


class Member(BaseModel):
    """A front-end registered customer/member — distinct from admin console
    users (operators/super_admin). No real registration flow exists yet;
    this is seeded mock data standing in for it."""

    id: str
    nickname: str
    phone_masked: str
    source: MemberSource
    registered_at: str
    last_active_at: str
    status: MemberStatus


class VerifyPasscodeInput(BaseModel):
    passcode: str


TutorialPlatform = Literal["general", "douyin", "video_channel", "xiaohongshu"]


class Tutorial(BaseModel):
    """A 图文 how-to article shown from the '绑定教程' link next to a
    platform's profile-url field on the add-account form. platform='general'
    articles aren't tied to a specific one of the three."""

    id: str
    platform: TutorialPlatform = "general"
    title: str
    cover_image_url: str | None = None
    content: str
    sort_order: int = 0
    created_at: str
    updated_at: str


class TutorialInput(BaseModel):
    platform: TutorialPlatform = "general"
    title: str
    cover_image_url: str | None = None
    content: str
    sort_order: int = 0


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


# ---- Order tracking (M5) ----
# 产品信息 -> 客户信息 (8 手动阶段) -> 订单信息 (成交客户×产品的匹配结果)
# -> 售后运维 (交付客户×产品的匹配结果)。没有真实订单系统对接前，这一整套
# 都是人工在后台维护的记录，不是自动生成的。

class Product(BaseModel):
    id: str
    name: str  # 商品名称
    internal_code: str = ""  # 内部编码
    chassis_info: str = ""  # 底盘信息
    chassis_number: str = ""  # 底盘编号
    main_image_url: str | None = None  # 商品主图
    layout_image_url: str | None = None  # 配置布局图
    standard_config: str = ""  # 标准配置
    customer_notes: str = ""  # 客户备注
    created_at: str


class ProductInput(BaseModel):
    name: str
    internal_code: str = ""
    chassis_info: str = ""
    chassis_number: str = ""
    main_image_url: str | None = None
    layout_image_url: str | None = None
    standard_config: str = ""
    customer_notes: str = ""


CustomerStage = Literal[
    "initial_chat",  # 1 初聊客户
    "deep_chat",  # 2 深聊客户
    "phone_call",  # 3 电话客户
    "video_call",  # 4 视频客户
    "car_viewing",  # 5 看车客户
    "deposit",  # 6 定金客户
    "deal_closed",  # 7 成交客户
    "delivered",  # 8 交付客户
]


class Customer(BaseModel):
    id: str
    name: str
    phone: str = ""
    source: str = ""
    stage: CustomerStage = "initial_chat"
    assigned_to: str = ""
    notes: str = ""
    created_at: str
    updated_at: str


class CustomerInput(BaseModel):
    name: str
    phone: str = ""
    source: str = ""
    stage: CustomerStage = "initial_chat"
    assigned_to: str = ""
    notes: str = ""


class Order(BaseModel):
    """Created by manually matching a stage=deal_closed customer to a product."""

    id: str
    customer_id: str
    product_id: str
    amount: float = 0
    signed_at: str
    notes: str = ""
    created_at: str


class OrderInput(BaseModel):
    customer_id: str
    product_id: str
    amount: float = 0
    signed_at: str
    notes: str = ""


class AfterSalesRecord(BaseModel):
    """Created by manually matching a stage=delivered customer to a product."""

    id: str
    customer_id: str
    product_id: str
    order_id: str | None = None
    delivered_at: str
    status: str = "质保中"
    notes: str = ""
    created_at: str
    updated_at: str


class AfterSalesInput(BaseModel):
    customer_id: str
    product_id: str
    order_id: str | None = None
    delivered_at: str
    status: str = "质保中"
    notes: str = ""
