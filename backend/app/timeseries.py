"""Deterministic mock daily time series for the 经营分析总览 overview page.

Real numbers will eventually come from the platform-scraping pipeline (M1).
Until then this generates a stable (seeded, not random-each-restart) 30-day
history per account so the overview page has something realistic to show.
"""

import math
import random
from datetime import datetime, timedelta, timezone

from .mock_data import ACCOUNTS

DAYS = 30
METRIC_KEYS = ["plays", "likes", "comments", "shares", "completion_rate", "new_followers"]


def _account_seed(account_id: str) -> int:
    return sum(ord(c) for c in account_id) * 1013 + 7


def _daily_series(account_id: str, follower_count: int) -> list[dict]:
    rng = random.Random(_account_seed(account_id))
    scale = max(follower_count, 5000) / 50000
    days = []
    for i in range(DAYS):
        base_plays = rng.uniform(4000, 9000) * scale
        wave = 1 + 0.25 * math.sin(i / 7 * math.pi)
        drift = 1 + i * 0.01
        plays = base_plays * wave * drift
        likes = plays * rng.uniform(0.05, 0.09)
        comments = plays * rng.uniform(0.003, 0.008)
        shares = plays * rng.uniform(0.006, 0.015)
        completion_rate = rng.uniform(0.28, 0.52)
        new_followers = plays * rng.uniform(0.002, 0.006)
        days.append(
            {
                "plays": round(plays),
                "likes": round(likes),
                "comments": round(comments),
                "shares": round(shares),
                "completion_rate": round(completion_rate, 4),
                "new_followers": round(new_followers),
            }
        )
    return days


def get_daily_series(account_id: str) -> list[dict]:
    if account_id == "all":
        per_account = [_daily_series(a.id, a.follower_count) for a in ACCOUNTS]
        if not per_account:
            return []
        combined = []
        for day_idx in range(DAYS):
            day_rows = [p[day_idx] for p in per_account]
            combined.append(
                {
                    "plays": sum(r["plays"] for r in day_rows),
                    "likes": sum(r["likes"] for r in day_rows),
                    "comments": sum(r["comments"] for r in day_rows),
                    "shares": sum(r["shares"] for r in day_rows),
                    "completion_rate": round(sum(r["completion_rate"] for r in day_rows) / len(day_rows), 4),
                    "new_followers": sum(r["new_followers"] for r in day_rows),
                }
            )
        return combined

    account = next((a for a in ACCOUNTS if a.id == account_id), None)
    if account is None:
        return []
    return _daily_series(account.id, account.follower_count)


def _metric_summary(days: list[dict], key: str, period: int) -> dict:
    recent = days[-period:]
    previous = days[-2 * period : -period] if len(days) >= 2 * period else days[:period]

    if key == "completion_rate":
        value = round(sum(d[key] for d in recent) / len(recent), 4)
        prev_avg = sum(d[key] for d in previous) / len(previous) if previous else value
        change_pct = round((value - prev_avg) * 100, 1)
    else:
        value = sum(d[key] for d in recent)
        previous_sum = sum(d[key] for d in previous) or 1
        change_pct = round((value - previous_sum) / previous_sum * 100, 1)

    return {"value": value, "change_pct": change_pct, "series": [d[key] for d in recent]}


def _diagnosis(account_label: str, metrics: dict) -> dict:
    plays_change = metrics["plays"]["change_pct"]
    completion_change = metrics["completion_rate"]["change_pct"]
    followers_change = metrics["new_followers"]["change_pct"]

    if plays_change >= 0:
        risk = (
            f"完播率环比{'上升' if completion_change >= 0 else '下降'}{abs(completion_change)}pct，"
            f"{'继续保持当前的开头节奏和选题方向。' if completion_change >= 0 else '建议排查近期视频的前3秒留存，是否存在开场拖沓的问题。'}"
        )
        opportunity = (
            f"{account_label}播放量环比增长{plays_change}%，涨粉数同步增长{followers_change}%，"
            f"说明当前内容方向和曝光的人群比较匹配，建议加大同类选题的更新频率。"
        )
    else:
        risk = (
            f"播放量环比下降{abs(plays_change)}%，且涨粉数{'同步下滑' if followers_change < 0 else '尚未受明显影响'}，"
            f"建议检查近期发布时间是否规律、封面点击率是否异常。"
        )
        opportunity = (
            f"完播率环比{'上升' if completion_change >= 0 else '下降'}{abs(completion_change)}pct，"
            f"{'内容本身留存没有问题，大概率是流量分发出了问题，可以尝试重新起量。' if completion_change >= 0 else '需要优先优化内容节奏再考虑加大投放。'}"
        )

    return {
        "model": "DeepSeek-V3",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "based_on": "近7天数据" if account_label else "近7天数据",
        "risk": risk,
        "opportunity": opportunity,
    }


def _alerts(account_label: str, metrics: dict) -> list[str]:
    alerts = []
    if metrics["completion_rate"]["change_pct"] < -1.5:
        alerts.append(f"「{account_label}」完播率环比下降{abs(metrics['completion_rate']['change_pct'])}pct，高于预警线")
    if metrics["plays"]["change_pct"] < -10:
        alerts.append(f"「{account_label}」播放量环比下降{abs(metrics['plays']['change_pct'])}%，需要关注")
    return alerts


def get_overview(account_id: str, period: int) -> dict | None:
    days = get_daily_series(account_id)
    if not days:
        return None

    if account_id == "all":
        account_label = "全部账号"
    else:
        account = next((a for a in ACCOUNTS if a.id == account_id), None)
        account_label = account.nickname if account else account_id

    metrics = {key: _metric_summary(days, key, period) for key in METRIC_KEYS}

    today = datetime.now(timezone.utc)
    all_dates = [(today - timedelta(days=DAYS - 1 - i)).strftime("%m/%d") for i in range(DAYS)]
    trend_days = days[-period:]
    trend_dates = all_dates[-period:]

    return {
        "account_id": account_id,
        "account_label": account_label,
        "period_days": period,
        "metrics": metrics,
        "trend": {
            "dates": trend_dates,
            "plays": [d["plays"] for d in trend_days],
            "new_followers": [d["new_followers"] for d in trend_days],
        },
        "diagnosis": _diagnosis(account_label, metrics),
        "alerts": _alerts(account_label, metrics),
    }
