from fastapi import APIRouter

from ..mock_data import VIDEOS
from ..schemas import Platform, VideoStat

router = APIRouter(prefix="/api/videos", tags=["videos"])


@router.get("", response_model=list[VideoStat])
def list_videos(platform: Platform | None = None) -> list[VideoStat]:
    if platform is None:
        return VIDEOS
    return [v for v in VIDEOS if v.platform == platform]
