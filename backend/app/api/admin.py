import json
import os
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from .. import storage
from ..auth import get_current_user
from ..schemas import Banner, BannerInput, ScrapeProfileInput, Tutorial, TutorialInput

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Internal scraper service (separate box, see ARCHIVE.md 九) — the bearer
# token lives only in this process's environment, never sent to the browser.
# SCRAPER_SERVICE_URL points at .../scraper-internal/scrape; the video-list
# endpoint lives as a sibling path on the same service.
SCRAPER_SERVICE_URL = os.environ.get("SCRAPER_SERVICE_URL", "")
SCRAPER_SERVICE_VIDEO_LIST_URL = SCRAPER_SERVICE_URL.rsplit("/", 1)[0] + "/scrape-video-list" if SCRAPER_SERVICE_URL else ""
SCRAPER_SERVICE_TOKEN = os.environ.get("SCRAPER_SERVICE_TOKEN", "")


def _call_scraper(url: str, payload: dict) -> dict:
    if not url or not SCRAPER_SERVICE_TOKEN:
        raise HTTPException(status_code=503, detail="抓取服务没配置（SCRAPER_SERVICE_URL/SCRAPER_SERVICE_TOKEN 环境变量缺失）")
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
        raise HTTPException(status_code=502, detail=f"抓取失败：{detail}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"抓取服务连不上：{e}")

STATIC_DIR = Path(__file__).parent.parent / "static"
ALLOWED_UPLOAD_EXT = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
}


@router.get("/banners", response_model=list[Banner], dependencies=[Depends(get_current_user)])
def admin_list_banners() -> list[Banner]:
    return storage.list_banners()


@router.post("/banners", response_model=Banner)
def admin_create_banner(payload: BannerInput, current: dict = Depends(get_current_user)) -> Banner:
    banner = storage.create_banner(payload.model_dump())
    storage.log_activity(current["id"], current["username"], "新增轮播图", banner.title)
    return banner


@router.put("/banners/{banner_id}", response_model=Banner)
def admin_update_banner(banner_id: str, payload: BannerInput, current: dict = Depends(get_current_user)) -> Banner:
    banner = storage.update_banner(banner_id, payload.model_dump())
    if banner is None:
        raise HTTPException(status_code=404, detail="banner not found")
    storage.log_activity(current["id"], current["username"], "编辑轮播图", banner.title)
    return banner


@router.delete("/banners/{banner_id}")
def admin_delete_banner(banner_id: str, current: dict = Depends(get_current_user)) -> dict[str, bool]:
    if not storage.delete_banner(banner_id):
        raise HTTPException(status_code=404, detail="banner not found")
    storage.log_activity(current["id"], current["username"], "删除轮播图", banner_id)
    return {"ok": True}


@router.get("/tutorials", response_model=list[Tutorial], dependencies=[Depends(get_current_user)])
def admin_list_tutorials() -> list[Tutorial]:
    return storage.list_tutorials()


@router.post("/tutorials", response_model=Tutorial)
def admin_create_tutorial(payload: TutorialInput, current: dict = Depends(get_current_user)) -> Tutorial:
    tutorial = storage.create_tutorial(payload.model_dump())
    storage.log_activity(current["id"], current["username"], "新增教程", tutorial.title)
    return tutorial


@router.put("/tutorials/{tutorial_id}", response_model=Tutorial)
def admin_update_tutorial(tutorial_id: str, payload: TutorialInput, current: dict = Depends(get_current_user)) -> Tutorial:
    tutorial = storage.update_tutorial(tutorial_id, payload.model_dump())
    if tutorial is None:
        raise HTTPException(status_code=404, detail="tutorial not found")
    storage.log_activity(current["id"], current["username"], "编辑教程", tutorial.title)
    return tutorial


@router.delete("/tutorials/{tutorial_id}")
def admin_delete_tutorial(tutorial_id: str, current: dict = Depends(get_current_user)) -> dict[str, bool]:
    if not storage.delete_tutorial(tutorial_id):
        raise HTTPException(status_code=404, detail="tutorial not found")
    storage.log_activity(current["id"], current["username"], "删除教程", tutorial_id)
    return {"ok": True}


@router.post("/scrape-profile")
def admin_scrape_profile(payload: ScrapeProfileInput, current: dict = Depends(get_current_user)) -> dict:
    result = _call_scraper(SCRAPER_SERVICE_URL, {"platform": payload.platform, "url": payload.url})
    storage.log_activity(current["id"], current["username"], "抓取平台账号信息", f"{payload.platform} {payload.url}")
    return result


@router.post("/scrape-video-list")
def admin_scrape_video_list(payload: ScrapeProfileInput, current: dict = Depends(get_current_user)) -> dict:
    """Best-effort recent-posts preview (cover + likes only, see RecentPost).
    Currently only implemented for douyin — other platforms 400 from the
    scraper service itself."""
    result = _call_scraper(SCRAPER_SERVICE_VIDEO_LIST_URL, {"platform": payload.platform, "url": payload.url})
    storage.log_activity(current["id"], current["username"], "抓取作品预览", f"{payload.platform} {payload.url}")
    return result


@router.post("/upload")
async def admin_upload_image(file: UploadFile = File(...), current: dict = Depends(get_current_user)) -> dict[str, str]:
    ext = Path(file.filename or "").suffix.lower() or ".png"
    if ext not in ALLOWED_UPLOAD_EXT:
        raise HTTPException(status_code=400, detail="unsupported file type")

    uploads_dir = STATIC_DIR / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    name = f"{uuid.uuid4().hex}{ext}"
    content = await file.read()
    (uploads_dir / name).write_bytes(content)
    storage.log_activity(current["id"], current["username"], "上传文件", name)
    return {"url": f"/static/uploads/{name}"}
