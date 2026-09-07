from fastapi import APIRouter, Depends

from .. import storage
from ..auth import get_current_user
from ..schemas import Settings, SettingsInput

public_router = APIRouter(prefix="/api/settings", tags=["settings"])
admin_router = APIRouter(prefix="/api/admin/settings", tags=["settings"])


@public_router.get("", response_model=Settings)
def get_settings() -> Settings:
    return storage.get_settings()


@admin_router.put("", response_model=Settings)
def update_settings(payload: SettingsInput, current: dict = Depends(get_current_user)) -> Settings:
    settings = storage.update_settings(payload.model_dump())
    storage.log_activity(current["id"], current["username"], "修改品牌名", payload.brand_name)
    return settings
