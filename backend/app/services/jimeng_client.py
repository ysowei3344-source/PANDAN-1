import os
import urllib.request
from pathlib import Path

# 即梦（火山引擎）多图参考生视频 API 的凭证，等文档/Key 到位后核对真实变量名。
JIMENG_API_KEY = os.environ.get("JIMENG_API_KEY", "")


class JimengNotConfigured(Exception):
    """Raised for every call until JIMENG_API_KEY (and the real request
    logic below) is wired up. Callers turn this into a shot status of
    "failed" with this message as error_message, rather than a 500 —
    the rest of the pipeline is fully exercisable while this adapter is
    still a stub."""


def submit_shot_job(person_photo_url: str, product_photo_url: str, visual_desc: str) -> str:
    if not JIMENG_API_KEY:
        raise JimengNotConfigured("即梦 API 尚未接入（缺少 JIMENG_API_KEY）")
    raise JimengNotConfigured("即梦 API 尚未接入")


def check_shot_job(task_id: str) -> dict:
    if not JIMENG_API_KEY:
        raise JimengNotConfigured("即梦 API 尚未接入（缺少 JIMENG_API_KEY）")
    raise JimengNotConfigured("即梦 API 尚未接入")


def download_video(url: str, dest_path: Path) -> None:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as resp:
        dest_path.write_bytes(resp.read())
