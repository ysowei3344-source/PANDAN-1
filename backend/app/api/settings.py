from fastapi import APIRouter, Depends

from .. import storage
from ..auth import get_current_user
from ..schemas import Settings, SettingsInput

public_router = APIRouter(prefix="/api/settings", tags=["settings"])
admin_router = APIRouter(prefix="/api/admin/settings", tags=["settings"])


@public_router.get("", response_model=Settings)
def get_settings() -> Settings:
    return storage.get_settings()


@admin_router.put("", response_model=Settings, dependencies=[Depends(get_current_user)])
def update_settings(payload: SettingsInput) -> Settings:
    return storage.update_settings(payload.model_dump())
