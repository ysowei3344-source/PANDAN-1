import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from .. import storage
from ..auth import get_current_user
from ..schemas import Banner, BannerInput

router = APIRouter(prefix="/api/admin", tags=["admin"])

STATIC_DIR = Path(__file__).parent.parent / "static"
ALLOWED_IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}


@router.get("/banners", response_model=list[Banner], dependencies=[Depends(get_current_user)])
def admin_list_banners() -> list[Banner]:
    return storage.list_banners()


@router.post("/banners", response_model=Banner, dependencies=[Depends(get_current_user)])
def admin_create_banner(payload: BannerInput) -> Banner:
    return storage.create_banner(payload.model_dump())


@router.put("/banners/{banner_id}", response_model=Banner, dependencies=[Depends(get_current_user)])
def admin_update_banner(banner_id: str, payload: BannerInput) -> Banner:
    banner = storage.update_banner(banner_id, payload.model_dump())
    if banner is None:
        raise HTTPException(status_code=404, detail="banner not found")
    return banner


@router.delete("/banners/{banner_id}", dependencies=[Depends(get_current_user)])
def admin_delete_banner(banner_id: str) -> dict[str, bool]:
    if not storage.delete_banner(banner_id):
        raise HTTPException(status_code=404, detail="banner not found")
    return {"ok": True}


@router.post("/upload", dependencies=[Depends(get_current_user)])
async def admin_upload_image(file: UploadFile = File(...)) -> dict[str, str]:
    ext = Path(file.filename or "").suffix.lower() or ".png"
    if ext not in ALLOWED_IMAGE_EXT:
        raise HTTPException(status_code=400, detail="unsupported file type")

    uploads_dir = STATIC_DIR / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    name = f"{uuid.uuid4().hex}{ext}"
    content = await file.read()
    (uploads_dir / name).write_bytes(content)
    return {"url": f"/static/uploads/{name}"}
