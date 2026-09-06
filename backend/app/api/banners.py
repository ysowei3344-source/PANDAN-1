from fastapi import APIRouter

from ..mock_data import BANNERS
from ..schemas import Banner

router = APIRouter(prefix="/api/banners", tags=["banners"])


@router.get("", response_model=list[Banner])
def list_banners() -> list[Banner]:
    return sorted(BANNERS, key=lambda b: b.sort_order)
