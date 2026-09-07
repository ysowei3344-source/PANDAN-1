import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from .. import storage
from ..auth import get_current_user
from ..schemas import Banner, BannerInput, Tutorial, TutorialInput

router = APIRouter(prefix="/api/admin", tags=["admin"])

STATIC_DIR = Path(__file__).parent.parent / "static"
ALLOWED_IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}


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


@router.post("/upload")
async def admin_upload_image(file: UploadFile = File(...), current: dict = Depends(get_current_user)) -> dict[str, str]:
    ext = Path(file.filename or "").suffix.lower() or ".png"
    if ext not in ALLOWED_IMAGE_EXT:
        raise HTTPException(status_code=400, detail="unsupported file type")

    uploads_dir = STATIC_DIR / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    name = f"{uuid.uuid4().hex}{ext}"
    content = await file.read()
    (uploads_dir / name).write_bytes(content)
    storage.log_activity(current["id"], current["username"], "上传图片", name)
    return {"url": f"/static/uploads/{name}"}
