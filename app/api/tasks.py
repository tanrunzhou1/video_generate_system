from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models import RenderTask
from app.db.session import get_db
from app.schemas.project import ApiResponse, TaskLogData

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.get("/{task_id}/logs", response_model=ApiResponse)
def get_task_logs(task_id: int, db: Session = Depends(get_db)) -> ApiResponse:
    task = db.get(RenderTask, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")

    if not task.log_file_path:
        raise HTTPException(status_code=404, detail="task log file path not found")

    log_path = Path(task.log_file_path)
    if not log_path.exists():
        raise HTTPException(status_code=404, detail="task log file not found")

    data = TaskLogData(
        task_id=task.id,
        project_id=task.project_id,
        stage=task.stage,
        status=task.status.value,
        retry_count=task.retry_count,
        error_code=task.error_code,
        error_message=task.error_message,
        log_file_path=task.log_file_path,
        log_content=log_path.read_text(encoding="utf-8"),
    )
    return ApiResponse(data=data.model_dump())
