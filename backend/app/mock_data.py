from datetime import datetime, timedelta

from .schemas import Account, VideoStat

ACCOUNTS: list[Account] = [
    Account(id="dy-01", platform="douyin", nickname="房车老王探店", follower_count=128400, video_count=214),
    Account(id="dy-02", platform="douyin", nickname="小房车改装日记", follower_count=52300, video_count=96),
    Account(id="sph-01", platform="video_channel", nickname="老王房车生活", follower_count=31200, video_count=58),
    Account(id="xhs-01", platform="xiaohongshu", nickname="房车穷游图鉴", follower_count=76500, video_count=142),
    Account(id="xhs-02", platform="xiaohongshu", nickname="周末房车露营", follower_count=19800, video_count=63),
]

_now = datetime(2026, 9, 6, 10, 0, 0)

VIDEOS: list[VideoStat] = [
    VideoStat(
        id="v-1001", account_id="dy-01", platform="douyin",
        title="30万预算能买到什么样的房车？实拍对比",
        plays=1_280_000, likes=86_400, comments=3_120, shares=9_800,
        published_at=_now - timedelta(days=2),
    ),
    VideoStat(
        id="v-1002", account_id="dy-01", platform="douyin",
        title="自驾房车穿越无人区，第3天差点没油",
        plays=642_000, likes=41_200, comments=1_860, shares=4_300,
        published_at=_now - timedelta(days=5),
    ),
    VideoStat(
        id="v-1003", account_id="dy-02", platform="douyin",
        title="房车改装：花8000块把厢式货车改成移动的家",
        plays=318_000, likes=22_100, comments=980, shares=2_150,
        published_at=_now - timedelta(days=1),
    ),
    VideoStat(
        id="v-1004", account_id="sph-01", platform="video_channel",
        title="带爸妈第一次坐房车，他们的反应笑死了",
        plays=204_000, likes=15_600, comments=740, shares=1_320,
        published_at=_now - timedelta(days=3),
    ),
    VideoStat(
        id="v-1005", account_id="xhs-01", platform="xiaohongshu",
        title="穷游房车攻略｜人均500元玩转川西",
        plays=156_000, likes=12_800, comments=560, shares=980,
        published_at=_now - timedelta(days=4),
    ),
    VideoStat(
        id="v-1006", account_id="xhs-02", platform="xiaohongshu",
        title="周末带娃露营，房车里的小厨房太治愈了",
        plays=88_000, likes=6_400, comments=310, shares=420,
        published_at=_now - timedelta(hours=18),
    ),
]
