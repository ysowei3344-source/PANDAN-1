from fastapi import APIRouter

from .. import storage
from ..schemas import Tutorial, TutorialPlatform

router = APIRouter(prefix="/api/tutorials", tags=["tutorials"])


@router.get("", response_model=list[Tutorial])
def list_tutorials(platform: TutorialPlatform | None = None) -> list[Tutorial]:
    return storage.list_tutorials(platform)
