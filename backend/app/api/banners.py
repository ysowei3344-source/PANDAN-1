from fastapi import APIRouter

from .. import storage
from ..schemas import Banner

router = APIRouter(prefix="/api/banners", tags=["banners"])


@router.get("", response_model=list[Banner])
def list_banners() -> list[Banner]:
    return storage.list_banners()
