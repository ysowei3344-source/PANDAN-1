from datetime import datetime, timedelta

from .schemas import Account, Banner, Identity, TodayStats, VideoStat

# 矩阵号：一个手机号/一个人设，内容同源分发到它注册的各个平台。
IDENTITIES: list[Identity] = [
    Identity(id="iden-1", name="房车老王探店", phone_number="138****0001"),
    Identity(id="iden-2", name="小房车改装日记", phone_number="139****0002"),
    Identity(id="iden-3", name="房车穷游图鉴", phone_number="137****0003"),
    Identity(id="iden-4", name="周末房车露营", phone_number="136****0004"),
    Identity(id="iden-5", name="房车维修老师傅", phone_number="135****0005"),
    Identity(id="iden-6", name="房车自驾中国", phone_number="134****0006"),
    Identity(id="iden-7", name="房车女生日记", phone_number="133****0007"),
    Identity(id="iden-8", name="房车亲子出行", phone_number="132****0008"),
    Identity(id="iden-9", name="房车老王探店小号", phone_number="131****0009"),
]

# 每个矩阵号名下的平台账号（同一身份在不同平台的绑定，昵称通常保持一致）。
ACCOUNTS: list[Account] = [
    Account(id="dy-01", identity_id="iden-1", platform="douyin", nickname="房车老王探店", follower_count=128400, video_count=214),
    Account(id="sph-01", identity_id="iden-1", platform="video_channel", nickname="房车老王探店", follower_count=31200, video_count=58),
    Account(id="xhs-06", identity_id="iden-1", platform="xiaohongshu", nickname="房车老王探店", follower_count=22000, video_count=40),

    Account(id="dy-02", identity_id="iden-2", platform="douyin", nickname="小房车改装日记", follower_count=52300, video_count=96),
    Account(id="xhs-07", identity_id="iden-2", platform="xiaohongshu", nickname="小房车改装日记", follower_count=18000, video_count=30),

    Account(id="xhs-01", identity_id="iden-3", platform="xiaohongshu", nickname="房车穷游图鉴", follower_count=76500, video_count=142),
    Account(id="dy-05", identity_id="iden-3", platform="douyin", nickname="房车穷游图鉴", follower_count=35000, video_count=60),

    Account(id="xhs-02", identity_id="iden-4", platform="xiaohongshu", nickname="周末房车露营", follower_count=19800, video_count=63),
    Account(id="dy-06", identity_id="iden-4", platform="douyin", nickname="周末房车露营", follower_count=12000, video_count=25),

    Account(id="dy-03", identity_id="iden-5", platform="douyin", nickname="房车维修老师傅", follower_count=41200, video_count=77),

    Account(id="sph-02", identity_id="iden-6", platform="video_channel", nickname="房车自驾中国", follower_count=12600, video_count=34),
    Account(id="dy-07", identity_id="iden-6", platform="douyin", nickname="房车自驾中国", follower_count=28000, video_count=50),

    Account(id="xhs-03", identity_id="iden-7", platform="xiaohongshu", nickname="房车女生日记", follower_count=28900, video_count=88),

    Account(id="xhs-04", identity_id="iden-8", platform="xiaohongshu", nickname="房车亲子出行", follower_count=15300, video_count=45),
    Account(id="dy-08", identity_id="iden-8", platform="douyin", nickname="房车亲子出行", follower_count=9500, video_count=18),

    Account(id="dy-04", identity_id="iden-9", platform="douyin", nickname="房车老王探店小号", follower_count=8600, video_count=21),
]

_now = datetime(2026, 9, 6, 10, 0, 0)

VIDEOS: list[VideoStat] = [
    VideoStat(
        id="v-1001", account_id="dy-01", platform="douyin",
        title="30万预算能买到什么样的房车？实拍对比",
        thumbnail_url="/static/thumbnails/v-1001.svg",
        poster_url="/static/posters/v-1001.svg",
        plays=1_280_000, likes=86_400, comments=3_120, shares=9_800,
        published_at=_now - timedelta(days=2),
        deepseek_analysis="开头3秒用价格悬念抓住停留，中段对比镜头切换节奏偏快（平均1.8秒/镜），建议后续同类选题保留这个节奏；评论区高频词是「落地价」「贷款」，可以在下一条里单独做一条金融方案的选题。",
    ),
    VideoStat(
        id="v-1002", account_id="dy-01", platform="douyin",
        title="自驾房车穿越无人区，第3天差点没油",
        thumbnail_url="/static/thumbnails/v-1002.svg",
        poster_url="/static/posters/v-1002.svg",
        plays=642_000, likes=41_200, comments=1_860, shares=4_300,
        published_at=_now - timedelta(days=5),
        deepseek_analysis="冲突点（差点没油）出现在第8秒，比同账号均值提前了5秒，完播率因此高于账号平均水平；结尾没有引导私信，建议补一个「想知道路线怎么规划」的钩子。",
    ),
    VideoStat(
        id="v-1003", account_id="dy-02", platform="douyin",
        title="房车改装：花8000块把厢式货车改成移动的家",
        thumbnail_url="/static/thumbnails/v-1003.svg",
        poster_url="/static/posters/v-1003.svg",
        plays=318_000, likes=22_100, comments=980, shares=2_150,
        published_at=_now - timedelta(days=1),
        deepseek_analysis="标题里的具体金额（8000块）是本条互动率高于历史均值的主要因素，评论区大量追问「材料清单」，建议出一条清单向的图文作为承接。",
    ),
    VideoStat(
        id="v-1004", account_id="sph-01", platform="video_channel",
        title="带爸妈第一次坐房车，他们的反应笑死了",
        thumbnail_url="/static/thumbnails/v-1004.svg",
        poster_url="/static/posters/v-1004.svg",
        plays=204_000, likes=15_600, comments=740, shares=1_320,
        published_at=_now - timedelta(days=3),
        deepseek_analysis="情感类选题在视频号上的分享率明显高于抖音同类内容，转发驱动的曝光占比约35%；父母视角的真实反应是核心卖点，建议做成系列。",
    ),
    VideoStat(
        id="v-1005", account_id="xhs-01", platform="xiaohongshu",
        title="穷游房车攻略｜人均500元玩转川西",
        thumbnail_url="/static/thumbnails/v-1005.svg",
        poster_url="/static/posters/v-1005.svg",
        plays=156_000, likes=12_800, comments=560, shares=980,
        published_at=_now - timedelta(days=4),
        deepseek_analysis="「人均500元」是标题党型钩子，收藏率显著高于点赞率（收藏/点赞比 1.4），说明用户当攻略在存，建议正文补充详细的路线图和费用清单以提升转化。",
    ),
    VideoStat(
        id="v-1006", account_id="xhs-02", platform="xiaohongshu",
        title="周末带娃露营，房车里的小厨房太治愈了",
        thumbnail_url="/static/thumbnails/v-1006.svg",
        poster_url="/static/posters/v-1006.svg",
        plays=88_000, likes=6_400, comments=310, shares=420,
        published_at=_now - timedelta(hours=18),
        deepseek_analysis="生活方式类内容，评论区以「求同款」「哪里改装」为主，是明确的获客信号，建议客服话术里预置这条视频的引导加微信文案。",
    ),
]

BANNERS: list[Banner] = [
    Banner(
        id="b-1", title="矩阵账号数据周报", subtitle="5 个账号 · 本周已生成",
        image_url="/static/banners/banner-1.svg", link_url=None, sort_order=1,
    ),
    Banner(
        id="b-2", title="对标拆解模板已更新", subtitle="新增 12 套可复用分镜模板",
        image_url="/static/banners/banner-2.svg", link_url=None, sort_order=2,
    ),
    Banner(
        id="b-3", title="AI 视频生成内测", subtitle="图生视频 / 文生视频 预约申请中",
        image_url="/static/banners/banner-3.svg", link_url=None, sort_order=3,
    ),
]

TODAY_STATS = TodayStats(
    videos_published=14,
    total_exposure=1_860_000,
    dm_conversations=86,
    wechat_added=23,
)
