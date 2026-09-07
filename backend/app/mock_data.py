from datetime import datetime, timedelta

from .schemas import (
    Account,
    AfterSalesRecord,
    Banner,
    Customer,
    Identity,
    Member,
    Order,
    Product,
    TodayStats,
    VideoStat,
)

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

# 前台会员——目前没有真实的注册流程，这批是占位数据，等 H5/小程序做了注册再换真实来源。
MEMBERS: list[Member] = [
    Member(
        id="mem-1", nickname="爱旅行的老张", phone_masked="138****2201", source="mini_program",
        registered_at=(_now - timedelta(days=12)).isoformat(), last_active_at=(_now - timedelta(hours=3)).isoformat(),
        status="active",
    ),
    Member(
        id="mem-2", nickname="房车小白", phone_masked="159****7734", source="h5",
        registered_at=(_now - timedelta(days=8)).isoformat(), last_active_at=(_now - timedelta(days=1)).isoformat(),
        status="active",
    ),
    Member(
        id="mem-3", nickname="周末去哪玩", phone_masked="187****5588", source="mini_program",
        registered_at=(_now - timedelta(days=25)).isoformat(), last_active_at=(_now - timedelta(days=6)).isoformat(),
        status="active",
    ),
    Member(
        id="mem-4", nickname="退休环游党", phone_masked="135****9012", source="h5",
        registered_at=(_now - timedelta(days=40)).isoformat(), last_active_at=(_now - timedelta(days=20)).isoformat(),
        status="disabled",
    ),
    Member(
        id="mem-5", nickname="带娃自驾家庭", phone_masked="177****3345", source="mini_program",
        registered_at=(_now - timedelta(days=3)).isoformat(), last_active_at=(_now - timedelta(hours=10)).isoformat(),
        status="active",
    ),
    Member(
        id="mem-6", nickname="改装发烧友", phone_masked="150****6678", source="h5",
        registered_at=(_now - timedelta(days=60)).isoformat(), last_active_at=(_now - timedelta(days=45)).isoformat(),
        status="disabled",
    ),
]

# 订单跟踪（M5）：产品 -> 客户（8 阶段，手动改）-> 订单（成交客户匹配产品）
# -> 售后（交付客户匹配产品）。没有真实订单系统对接前全靠人工维护，这批是演示数据。
PRODUCTS: list[Product] = [
    Product(
        id="prod-1", name="大通 V90 房车版", model="C型 6座", price=398000,
        description="紧凑型 C 型房车，适合家庭自驾露营，带独立卫浴。",
        created_at=(_now - timedelta(days=90)).isoformat(),
    ),
    Product(
        id="prod-2", name="江铃途睿欧 C型", model="C型 4座", price=598000,
        description="进口底盘，长途穿越首选，带太阳能板和大容量水箱。",
        created_at=(_now - timedelta(days=90)).isoformat(),
    ),
    Product(
        id="prod-3", name="上汽大通 RG10", model="B型 2座", price=328000,
        description="B型房车，灵活好开，适合城市通勤+周末露营两用。",
        created_at=(_now - timedelta(days=60)).isoformat(),
    ),
]

CUSTOMERS: list[Customer] = [
    Customer(
        id="cust-1", name="张先生", phone="139****1101", source="抖音私信",
        stage="initial_chat", assigned_to="牛牛", notes="问了下大通V90的价格，还在比较阶段",
        created_at=(_now - timedelta(days=1)).isoformat(), updated_at=(_now - timedelta(days=1)).isoformat(),
    ),
    Customer(
        id="cust-2", name="李女士", phone="138****2202", source="小红书私信",
        stage="deep_chat", assigned_to="牛牛", notes="聊了预算和用车场景，倾向B型",
        created_at=(_now - timedelta(days=3)).isoformat(), updated_at=(_now - timedelta(days=2)).isoformat(),
    ),
    Customer(
        id="cust-3", name="王先生", phone="137****3303", source="视频号私信",
        stage="phone_call", assigned_to="牛牛", notes="已电话沟通，约了本周视频看车",
        created_at=(_now - timedelta(days=5)).isoformat(), updated_at=(_now - timedelta(days=1)).isoformat(),
    ),
    Customer(
        id="cust-4", name="陈女士", phone="136****4404", source="抖音私信",
        stage="video_call", assigned_to="牛牛", notes="视频看过内饰，约到店试车",
        created_at=(_now - timedelta(days=7)).isoformat(), updated_at=(_now - timedelta(days=2)).isoformat(),
    ),
    Customer(
        id="cust-5", name="刘先生", phone="135****5505", source="朋友介绍",
        stage="car_viewing", assigned_to="牛牛", notes="到店试驾了大通V90，很满意，在考虑定金",
        created_at=(_now - timedelta(days=10)).isoformat(), updated_at=(_now - timedelta(hours=20)).isoformat(),
    ),
    Customer(
        id="cust-6", name="赵女士", phone="134****6606", source="小红书私信",
        stage="deposit", assigned_to="牛牛", notes="已付定金5000元，等提车安排",
        created_at=(_now - timedelta(days=14)).isoformat(), updated_at=(_now - timedelta(days=3)).isoformat(),
    ),
    Customer(
        id="cust-7", name="孙先生", phone="133****7707", source="抖音私信",
        stage="deal_closed", assigned_to="牛牛", notes="已签合同，等排产交车",
        created_at=(_now - timedelta(days=20)).isoformat(), updated_at=(_now - timedelta(days=5)).isoformat(),
    ),
    Customer(
        id="cust-8", name="周女士", phone="132****8808", source="视频号私信",
        stage="delivered", assigned_to="牛牛", notes="已提车，首保待安排",
        created_at=(_now - timedelta(days=45)).isoformat(), updated_at=(_now - timedelta(days=10)).isoformat(),
    ),
]

ORDERS: list[Order] = [
    Order(
        id="order-1", customer_id="cust-7", product_id="prod-1", amount=395000,
        signed_at=(_now - timedelta(days=5)).isoformat(), notes="谈价5000元优惠",
        created_at=(_now - timedelta(days=5)).isoformat(),
    ),
    Order(
        id="order-2", customer_id="cust-8", product_id="prod-2", amount=598000,
        signed_at=(_now - timedelta(days=30)).isoformat(), notes="",
        created_at=(_now - timedelta(days=30)).isoformat(),
    ),
]

AFTERSALES: list[AfterSalesRecord] = [
    AfterSalesRecord(
        id="as-1", customer_id="cust-8", product_id="prod-2", order_id="order-2",
        delivered_at=(_now - timedelta(days=10)).isoformat(), status="质保中",
        notes="交付时说明了保养周期，等首保预约",
        created_at=(_now - timedelta(days=10)).isoformat(), updated_at=(_now - timedelta(days=10)).isoformat(),
    ),
]
