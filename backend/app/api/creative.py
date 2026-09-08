import subprocess
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from .. import storage
from ..auth import get_current_user
from ..schemas import CreativeProject, CreativeProjectInput, CreativeScriptEditInput
from ..services import jimeng_client, script_template

router = APIRouter(prefix="/api/admin/creative", tags=["creative"])

STATIC_DIR = Path(__file__).parent.parent / "static"


def _get_shot(project: CreativeProject, index: int) -> dict:
    for shot in project.shots:
        if shot.index == index:
            return shot.model_dump()
    raise HTTPException(status_code=404, detail="shot not found")


def _save_shot(project_id: str, project: CreativeProject, shot: dict) -> CreativeProject:
    shots = [shot if s.index == shot["index"] else s.model_dump() for s in project.shots]
    updated = storage.update_creative_project(project_id, {"shots": shots})
    if updated is None:
        raise HTTPException(status_code=404, detail="project not found")
    return updated


@router.get("", response_model=list[CreativeProject], dependencies=[Depends(get_current_user)])
def list_creative_projects() -> list[CreativeProject]:
    return storage.list_creative_projects()


@router.post("", response_model=CreativeProject)
def create_creative_project(payload: CreativeProjectInput, current: dict = Depends(get_current_user)) -> CreativeProject:
    if payload.product_id and storage.get_product(payload.product_id) is None:
        raise HTTPException(status_code=404, detail="product not found")
    project = storage.create_creative_project({**payload.model_dump(), "created_by": current["username"]})
    storage.log_activity(current["id"], current["username"], "新建AI创作项目", project.name)
    return project


@router.get("/{project_id}", response_model=CreativeProject, dependencies=[Depends(get_current_user)])
def get_creative_project(project_id: str) -> CreativeProject:
    project = storage.get_creative_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    return project


@router.put("/{project_id}", response_model=CreativeProject)
def update_creative_project(project_id: str, payload: CreativeProjectInput, current: dict = Depends(get_current_user)) -> CreativeProject:
    if payload.product_id and storage.get_product(payload.product_id) is None:
        raise HTTPException(status_code=404, detail="product not found")
    project = storage.update_creative_project(project_id, payload.model_dump())
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    storage.log_activity(current["id"], current["username"], "编辑AI创作项目", project.name)
    return project


@router.delete("/{project_id}")
def delete_creative_project(project_id: str, current: dict = Depends(get_current_user)) -> dict:
    project = storage.get_creative_project(project_id)
    if project is None or not storage.delete_creative_project(project_id):
        raise HTTPException(status_code=404, detail="project not found")
    storage.log_activity(current["id"], current["username"], "删除AI创作项目", project.name)
    return {"ok": True}


@router.post("/{project_id}/generate-script", response_model=CreativeProject)
def generate_script(project_id: str, current: dict = Depends(get_current_user)) -> CreativeProject:
    project = storage.get_creative_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    product = storage.get_product(project.product_id) if project.product_id else None
    script_text, shots = script_template.generate_script(product, project.duration_seconds)
    updated = storage.update_creative_project(project_id, {"script_text": script_text, "shots": shots})
    storage.log_activity(current["id"], current["username"], "生成AI创作脚本", project.name)
    return updated


@router.put("/{project_id}/script", response_model=CreativeProject)
def edit_script(project_id: str, payload: CreativeScriptEditInput, current: dict = Depends(get_current_user)) -> CreativeProject:
    project = storage.get_creative_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    updated = storage.update_creative_project(
        project_id,
        {"script_text": payload.script_text, "shots": [s.model_dump() for s in payload.shots]},
    )
    storage.log_activity(current["id"], current["username"], "编辑AI创作脚本", project.name)
    return updated


def _trigger_shot_generation(project_id: str, index: int, current: dict) -> dict:
    project = storage.get_creative_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    shot = _get_shot(project, index)

    if not project.person_photo_url:
        raise HTTPException(status_code=400, detail="请先上传人物照片")
    product = storage.get_product(project.product_id) if project.product_id else None
    if product is None or not product.main_image_urls:
        raise HTTPException(status_code=400, detail="请先选择带主图的商品")

    try:
        task_id = jimeng_client.submit_shot_job(project.person_photo_url, product.main_image_urls[0], shot["visual_desc"])
    except jimeng_client.JimengNotConfigured as e:
        shot.update(status="failed", error_message=str(e), jimeng_task_id=None)
        _save_shot(project_id, project, shot)
        storage.log_activity(current["id"], current["username"], "触发分镜生成失败", f"{project.name} #{index}: {e}")
        return shot

    shot.update(status="generating", jimeng_task_id=task_id, error_message=None)
    _save_shot(project_id, project, shot)
    storage.log_activity(current["id"], current["username"], "触发分镜生成", f"{project.name} #{index}")
    return shot


@router.post("/{project_id}/shots/{index}/generate")
def generate_shot(project_id: str, index: int, current: dict = Depends(get_current_user)) -> dict:
    return _trigger_shot_generation(project_id, index, current)


@router.post("/{project_id}/shots/{index}/regenerate")
def regenerate_shot(project_id: str, index: int, current: dict = Depends(get_current_user)) -> dict:
    return _trigger_shot_generation(project_id, index, current)


@router.get("/{project_id}/shots/{index}/status", dependencies=[Depends(get_current_user)])
def get_shot_status(project_id: str, index: int) -> dict:
    project = storage.get_creative_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    shot = _get_shot(project, index)

    if shot["status"] != "generating" or not shot["jimeng_task_id"]:
        return shot

    try:
        result = jimeng_client.check_shot_job(shot["jimeng_task_id"])
    except jimeng_client.JimengNotConfigured as e:
        shot.update(status="failed", error_message=str(e))
        return _get_shot(_save_shot(project_id, project, shot), index)

    shot.update(status=result["status"], video_url=result.get("video_url"))
    return _get_shot(_save_shot(project_id, project, shot), index)


@router.post("/{project_id}/compose", response_model=CreativeProject)
def compose_final_video(project_id: str, current: dict = Depends(get_current_user)) -> CreativeProject:
    project = storage.get_creative_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    if not project.shots or any(s.status != "done" for s in project.shots):
        raise HTTPException(status_code=400, detail="还有分镜没有生成完成")

    project_dir = STATIC_DIR / "creative" / project_id
    shot_paths = []
    for shot in sorted(project.shots, key=lambda s: s.index):
        shot_path = project_dir / f"shot-{shot.index}.mp4"
        jimeng_client.download_video(shot.video_url, shot_path)
        shot_paths.append(shot_path)

    list_path = project_dir / "concat_list.txt"
    list_path.write_text("".join(f"file '{p.name}'\n" for p in shot_paths), encoding="utf-8")
    out_path = project_dir / "final.mp4"
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path), "-c", "copy", str(out_path)],
            check=True, capture_output=True, cwd=project_dir,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise HTTPException(status_code=502, detail=f"视频合成失败：{e}")

    final_url = f"/static/creative/{project_id}/final.mp4"
    updated = storage.update_creative_project(project_id, {"final_video_url": final_url, "status": "done"})
    storage.log_activity(current["id"], current["username"], "合成AI创作视频", project.name)
    return updated
