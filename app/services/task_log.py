from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.db.models import RenderTask, RenderTaskStatus

settings = get_settings()


def _task_log_path(project_id: int, task_id: int) -> str:
    return str(Path(settings.logs_dir) / "tasks" / f"project_{project_id}" / f"task_{task_id}.log")


def _write_task_log(log_file_path: str, message: str) -> None:
    path = Path(log_file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().isoformat(timespec="seconds")
    with path.open("a", encoding="utf-8") as file_obj:
        file_obj.write(f"[{timestamp}] {message}\n")


def create_task_with_log(db: Session, project_id: int, stage: str) -> RenderTask:
    task = RenderTask(
        project_id=project_id,
        stage=stage,
        status=RenderTaskStatus.PENDING,
        retry_count=0,
    )
    db.add(task)
    db.flush()
    task.log_file_path = _task_log_path(project_id, task.id)
    _write_task_log(task.log_file_path, f"task created: stage={stage}, status={task.status.value}")
    db.flush()
    return task


def mark_task_running(db: Session, task: RenderTask) -> RenderTask:
    task.status = RenderTaskStatus.RUNNING
    task.started_at = datetime.utcnow()
    _write_task_log(task.log_file_path or _task_log_path(task.project_id, task.id), "task running")
    db.flush()
    return task


def mark_task_succeeded(db: Session, task: RenderTask, message: str | None = None) -> RenderTask:
    task.status = RenderTaskStatus.SUCCEEDED
    task.finished_at = datetime.utcnow()
    _write_task_log(task.log_file_path or _task_log_path(task.project_id, task.id), message or "task succeeded")
    db.flush()
    return task


def mark_task_failed(
    db: Session,
    task: RenderTask,
    error_code: str,
    error_message: str,
) -> RenderTask:
    task.status = RenderTaskStatus.FAILED
    task.error_code = error_code
    task.error_message = error_message
    task.finished_at = datetime.utcnow()
    _write_task_log(
        task.log_file_path or _task_log_path(task.project_id, task.id),
        f"task failed: error_code={error_code}, error_message={error_message}",
    )
    db.flush()
    return task
