from datetime import datetime
from typing import Literal

from pydantic import BaseModel

Platform = Literal["douyin", "video_channel", "xiaohongshu"]


class RecentPost(BaseModel):
    """A lightweight preview of one recent post, scraped from the platform's
    profile grid. Deliberately thin — only cover_url/likes are reliably
    available (see ARCHIVE.md 9.10/9.11); no title/plays/comments/id/link,
    so this is NOT the same thing as a full VideoStat record."""

    cover_url: str
    likes: int | None = None


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
    recent_posts: list[RecentPost] = []


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
    operator_username: str | None = None
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
    recent_posts: list[RecentPost] = []


class AccountUpdateInput(BaseModel):
    nickname: str = ""
    avatar_url: str | None = None
    profile_url: str | None = None
    follower_count: int = 0
    video_count: int = 0
    recent_posts: list[RecentPost] = []


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
    avatar_url: str | None = None
    created_at: str


class UserCreateInput(BaseModel):
    username: str
    password: str
    role: Role = "operator"
    identity_id: str | None = None
    passcode: str | None = None
    avatar_url: str | None = None


class UserUpdateInput(BaseModel):
    """All fields optional — only what's provided gets changed.
    password/passcode are write-only resets, never round-tripped back out."""

    username: str | None = None
    password: str | None = None
    passcode: str | None = None
    avatar_url: str | None = None  # "" clears the avatar, None leaves it unchanged


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


class VerifySalesPasscodeInput(BaseModel):
    sales_username: str
    passcode: str


class ScrapeProfileInput(BaseModel):
    platform: Platform
    url: str


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


class DecorBlock(BaseModel):
    id: str
    type: str  # image | grid_nav | notice | rich_text | spacer | divider
    props: dict = {}
    enabled: bool = True


class DecorPage(BaseModel):
    app: str
    page_key: str
    blocks: list[DecorBlock] = []
    updated_at: str | None = None


class DecorPageInput(BaseModel):
    blocks: list[DecorBlock] = []


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
# 商品信息 独立维护；一个 Order 从创建起就同时是"客户"和"订单"——销售直接
# 手动录入客户信息 + 匹配商品，八个阶段(1-8)的变化都在同一条记录上调整，
# 不再有"先建客户、成交了才建订单"的两段式流程。没有真实订单系统对接前，
# 这一整套都是人工在后台/销售端手动维护的记录，不是自动生成的。

class ProductCategory(BaseModel):
    id: str
    name: str
    icon_url: str | None = None
    sort_order: int = 0
    created_at: str


class ProductCategoryInput(BaseModel):
    name: str
    icon_url: str | None = None
    sort_order: int = 0


class Product(BaseModel):
    id: str
    name: str  # 商品名称
    internal_code: str = ""  # 内部编码
    category_id: str | None = None  # 商品分类
    price: float = 0  # 商品价格
    chassis_info: str = ""  # 底盘信息
    chassis_number: str = ""  # 底盘编号
    main_image_urls: list[str] = []  # 商品主图，支持多张，列表页轮播展示
    layout_urls: list[str] = []  # 配置布局，支持多张图片或文档，最多5个
    standard_config: str = ""  # 标准配置
    optional_config: str = ""  # 增选配置
    created_at: str


class ProductInput(BaseModel):
    name: str
    internal_code: str = ""
    category_id: str | None = None
    price: float = 0
    chassis_info: str = ""
    chassis_number: str = ""
    main_image_urls: list[str] = []
    layout_urls: list[str] = []
    standard_config: str = ""
    optional_config: str = ""


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

# 独立于 CustomerStage 的另一条进度线——"订单状态"，用图标表示，跟单猿
# 手动推进，跟客户阶段并存，互不影响。
OrderStatus = Literal[
    "negotiating",  # 💬 洽谈中
    "small_deposit",  # 🥈 付小订
    "full_deposit",  # 🥇 付大定
    "in_production",  # 🔨 生产中
    "completed",  # 🚗 已完工
    "delivered",  # 🎉 已交付
]


class Order(BaseModel):
    """One record per customer opportunity, created directly by a 销售 (not
    gated behind reaching any particular stage first). Tracks the customer's
    info, which product they're matched to, and their 1-8 stage all in one
    place; amount/signed_at fill in once stage reaches deal_closed,
    aftersales_status/aftersales_notes once it reaches delivered. Every order
    must belong to a 销售 (assigned_to) — there is no such thing as an
    unassigned order."""

    id: str
    name: str  # 客户姓名
    phone: str = ""
    avatar_url: str | None = None  # 客户头像
    city: str = ""  # 客户城市
    gender: str = ""  # 客户性别（称呼），例如"大哥"/"美女"
    source: str = ""  # 来源渠道
    financial_status: str = ""  # 经济状况
    product_id: str | None = None  # 意向/匹配车型
    chassis_number: str = ""  # 车架号（这台车实际的车架号，跟 Product.chassis_number 模板号是两回事）
    stage: CustomerStage = "initial_chat"
    order_status: OrderStatus = "negotiating"  # 独立于 stage 的图标进度
    assigned_to: str  # 归属销售，必填
    ai_wechat: str = ""
    notes: str = ""
    amount: float = 0  # 成交金额
    signed_at: str | None = None  # 成交日期
    delivered_at: str | None = None  # 交付日期
    aftersales_status: str = ""  # 售后状态，例如"质保中"
    aftersales_notes: str = ""
    last_reminded_at: str | None = None  # 上次"维护"跟进记录的时间，用于展示"已提醒"状态点
    created_at: str
    updated_at: str


class OrderInput(BaseModel):
    name: str
    phone: str = ""
    avatar_url: str | None = None
    city: str = ""
    gender: str = ""
    source: str = ""
    financial_status: str = ""
    product_id: str | None = None
    chassis_number: str = ""
    stage: CustomerStage = "initial_chat"
    order_status: OrderStatus = "negotiating"
    assigned_to: str
    ai_wechat: str = ""
    notes: str = ""
    amount: float = 0
    signed_at: str | None = None
    delivered_at: str | None = None
    aftersales_status: str = ""
    aftersales_notes: str = ""
    last_reminded_at: str | None = None


# ---- 销售日志记录：跟单猿日志 ----
# 每个销售跟单猿自己填的工作日志，跟 Order 一样按 username（对应
# Order.assigned_to）关联，看别人的日志需要对应销售跟单猿的管理口令
# （复用 orders 那套 verify-sales-passcode，同一个口令）。"跟单猿业绩"不是
# 独立存储，是前端直接拿 /orders 数据按 assigned_to 分组统计出来的。

class WorkLog(BaseModel):
    id: str
    username: str  # 填写人，对应 User.username / Order.assigned_to
    today_work: str = ""  # 今日工作内容
    issues: str = ""  # 遇到的问题
    tomorrow_plan: str = ""  # 明日计划
    created_at: str
    updated_at: str


class WorkLogInput(BaseModel):
    today_work: str = ""
    issues: str = ""
    tomorrow_plan: str = ""


# ---- AI创作平台（数字人+产品 分镜短视频生成） ----
# 一个 CreativeProject = 一张人物照片 + 一个商品 + 目标时长，先机械/模板生成
# 脚本文案，按 7 秒一段切成 CreativeShot 列表，每个分镜单独调用即梦
# （script_template.py / jimeng_client.py 是两个占位适配层，等真 LLM／即梦
# API文档到位后只改那两个文件，这里的数据模型和流转状态不用跟着变）。

JobStatus = Literal["draft", "queued", "generating", "done", "failed"]


class CreativeShot(BaseModel):
    index: int
    start_sec: int
    end_sec: int
    narration: str = ""  # 台词/口播文案
    visual_desc: str = ""  # 画面描述，给视频生成用的提示词
    status: JobStatus = "draft"
    video_url: str | None = None
    jimeng_task_id: str | None = None
    error_message: str | None = None
    generated_at: str | None = None


class CreativeProject(BaseModel):
    id: str
    name: str
    person_photo_url: str = ""
    product_id: str | None = None
    duration_seconds: int = 15
    script_text: str = ""
    shots: list[CreativeShot] = []
    status: JobStatus = "draft"  # draft 直到脚本生成；compose 成功后 done
    final_video_url: str | None = None
    created_by: str = ""
    created_at: str
    updated_at: str


class CreativeProjectInput(BaseModel):
    name: str
    person_photo_url: str = ""
    product_id: str | None = None
    duration_seconds: int = 15


class CreativeScriptEditInput(BaseModel):
    script_text: str
    shots: list[CreativeShot]
