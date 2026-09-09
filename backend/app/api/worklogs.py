from fastapi import APIRouter, Depends, HTTPException

from .. import storage
from ..auth import get_current_user
from ..schemas import WorkLog, WorkLogInput

router = APIRouter(prefix="/api/admin/worklogs", tags=["worklogs"])

# 权限模型跟 orders 一样：谁都能读全部日志（列表接口不过滤），前端按
# username 分组显示，看别人的要先过 orders 那套 verify-sales-passcode
# （同一个口令，本模块不重复定义）。写权限收在这里：只能改自己的。


@router.get("", response_model=list[WorkLog], dependencies=[Depends(get_current_user)])
def list_work_logs() -> list[WorkLog]:
    return storage.list_work_logs()


@router.post("", response_model=WorkLog)
def create_work_log(payload: WorkLogInput, current: dict = Depends(get_current_user)) -> WorkLog:
    log = storage.create_work_log({**payload.model_dump(), "username": current["username"]})
    storage.log_activity(current["id"], current["username"], "新增工作日志", log.today_work[:30])
    return log


@router.put("/{log_id}", response_model=WorkLog)
def update_work_log(log_id: str, payload: WorkLogInput, current: dict = Depends(get_current_user)) -> WorkLog:
    existing = storage.get_work_log(log_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="log not found")
    if current["role"] != "super_admin" and existing.username != current["username"]:
        raise HTTPException(status_code=403, detail="只能编辑自己的日志")
    updated = storage.update_work_log(log_id, payload.model_dump())
    storage.log_activity(current["id"], current["username"], "编辑工作日志", log_id)
    return updated


@router.delete("/{log_id}")
def delete_work_log(log_id: str, current: dict = Depends(get_current_user)) -> dict:
    existing = storage.get_work_log(log_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="log not found")
    if current["role"] != "super_admin" and existing.username != current["username"]:
        raise HTTPException(status_code=403, detail="只能删除自己的日志")
    storage.delete_work_log(log_id)
    storage.log_activity(current["id"], current["username"], "删除工作日志", log_id)
    return {"ok": True}
