import json
import os
import urllib.error
import urllib.request

# Internal scraper service (separate box, see ARCHIVE.md 九) — the bearer
# token lives only in this process's environment, never sent to the browser.
# SCRAPER_SERVICE_URL points at .../scraper-internal/scrape; the video-list
# endpoint lives as a sibling path on the same service.
SCRAPER_SERVICE_URL = os.environ.get("SCRAPER_SERVICE_URL", "")
SCRAPER_SERVICE_VIDEO_LIST_URL = (
    SCRAPER_SERVICE_URL.rsplit("/", 1)[0] + "/scrape-video-list" if SCRAPER_SERVICE_URL else ""
)
SCRAPER_SERVICE_TOKEN = os.environ.get("SCRAPER_SERVICE_TOKEN", "")


class ScraperError(Exception):
    """Raised for both "not configured" and "call failed" — callers that need
    to tell the two apart (e.g. to pick an HTTP status) can check the message,
    background callers can just log-and-skip either way."""


def call_scraper(url: str, payload: dict) -> dict:
    if not url or not SCRAPER_SERVICE_TOKEN:
        raise ScraperError("抓取服务没配置（SCRAPER_SERVICE_URL/SCRAPER_SERVICE_TOKEN 环境变量缺失）")
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {SCRAPER_SERVICE_TOKEN}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")
        try:
            detail = json.loads(detail).get("error", detail)
        except ValueError:
            pass
        raise ScraperError(f"抓取失败：{detail}") from e
    except Exception as e:
        raise ScraperError(f"抓取服务连不上：{e}") from e
