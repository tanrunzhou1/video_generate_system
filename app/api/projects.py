from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.db.models import (
    FinalVideo,
    Project,
    ProjectAsset,
    ProjectAssetType,
    ProjectStatus,
    RenderTask,
)
from app.db.session import get_db
from app.services.task_log import create_task_with_log
from app.schemas.project import (
    ApiResponse,
    CreateTaskRequest,
    CreateProjectRequest,
    ProjectStatusData,
    TaskCreatedData,
    UploadedAssetItem,
)

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])
settings = get_settings()


def _build_latest_task_summary(latest_task: RenderTask | None) -> dict | None:
    if latest_task is None:
        return None

    return {
        "task_id": latest_task.id,
        "stage": latest_task.stage,
        "status": latest_task.status.value,
        "retry_count": latest_task.retry_count,
        "error_code": latest_task.error_code,
        "error_message": latest_task.error_message,
        "log_file_path": getattr(latest_task, "log_file_path", None),
    }


def _build_final_video_summary(final_video: FinalVideo | None) -> dict | None:
    if final_video is None:
        return None

    return {
        "video_id": final_video.id,
        "resolution": final_video.resolution,
        "duration_sec": final_video.duration_sec,
        "file_path": final_video.file_path,
        "cover_image_path": final_video.cover_image_path,
        "created_at": final_video.created_at,
    }

def _save_upload_file(project_id: int, asset_type: str, file: UploadFile) -> tuple[str, int]:
    base = Path(settings.storage_dir) / "projects" / str(project_id) / asset_type
    base.mkdir(parents=True, exist_ok=True)
    filename = file.filename or f"{asset_type}.bin"
    dst = base / filename
    content = file.file.read()
    dst.write_bytes(content)
    return str(dst), len(content)


@router.post("", response_model=ApiResponse)
def create_project(payload: CreateProjectRequest, db: Session = Depends(get_db)) -> ApiResponse:
    normalized_name = payload.name.strip()
    if not normalized_name:
        raise HTTPException(status_code=400, detail="project name cannot be blank")

    existing = db.execute(select(Project.id).where(Project.name == normalized_name)).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=409, detail="project name already exists")

    project = Project(
        name=normalized_name,
        description=payload.description,
        target_duration_sec=payload.target_duration_sec,
        style_preset=payload.style_preset,
        status=ProjectStatus.CREATED,
    )
    db.add(project)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="project name already exists")
    db.refresh(project)
    return ApiResponse(
        data={
            "project_id": project.id,
            "name": project.name,
            "status": project.status.value,
            "target_duration_sec": project.target_duration_sec,
            "created_at": project.created_at,
        }
    )


@router.post("/{project_id}/tasks", response_model=ApiResponse)
def create_project_task(
    project_id: int,
    payload: CreateTaskRequest,
    db: Session = Depends(get_db),
) -> ApiResponse:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")

    task = create_task_with_log(db, project_id=project.id, stage=payload.stage.strip())
    db.commit()
    db.refresh(task)

    data = TaskCreatedData(
        task_id=task.id,
        project_id=project.id,
        stage=task.stage,
        status=task.status.value,
        log_file_path=task.log_file_path or "",
    )
    return ApiResponse(data=data.model_dump())


@router.post("/{project_id}/assets", response_model=ApiResponse)
def upload_project_assets(
    project_id: int,
    script_file: UploadFile = File(...),
    persona_doc: UploadFile = File(...),
    character_images: list[UploadFile] = File(...),
    style_reference: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
) -> ApiResponse:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")

    uploads: list[tuple[ProjectAssetType, UploadFile]] = [
        (ProjectAssetType.SCRIPT_FILE, script_file),
        (ProjectAssetType.PERSONA_DOC, persona_doc),
    ]
    uploads.extend((ProjectAssetType.CHARACTER_IMAGE, f) for f in character_images)
    if style_reference is not None:
        uploads.append((ProjectAssetType.STYLE_REFERENCE, style_reference))

    uploaded_items: list[UploadedAssetItem] = []
    for asset_type, file in uploads:
        file_path, size_bytes = _save_upload_file(project_id, asset_type.value, file)
        asset = ProjectAsset(
            project_id=project.id,
            asset_type=asset_type,
            file_path=file_path,
            original_name=file.filename or "",
            mime_type=file.content_type or "application/octet-stream",
            size_bytes=size_bytes,
            is_active=True,
        )
        db.add(asset)
        db.flush()
        uploaded_items.append(
            UploadedAssetItem(asset_id=asset.id, asset_type=asset_type.value, file_path=file_path)
        )

    db.commit()
    return ApiResponse(
        data={
            "project_id": project_id,
            "uploaded": [x.model_dump() for x in uploaded_items],
            "failed": [],
        }
    )


@router.get("/{project_id}/status", response_model=ApiResponse)
def get_project_status(project_id: int, db: Session = Depends(get_db)) -> ApiResponse:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")

    latest_task = db.execute(
        select(RenderTask).where(RenderTask.project_id == project.id).order_by(desc(RenderTask.started_at))
    ).scalars().first()

    data = ProjectStatusData(
        project_id=project.id,
        status=project.status.value,
        current_stage=latest_task.stage if latest_task else None,
        progress=None,
        retry_count=latest_task.retry_count if latest_task else 0,
        last_error_code=latest_task.error_code if latest_task else None,
        last_error_message=latest_task.error_message if latest_task else None,
        updated_at=project.updated_at,
    )
    return ApiResponse(data=data.model_dump())


@router.get("/{project_id}", response_model=ApiResponse)
def get_project_detail(project_id: int, db: Session = Depends(get_db)) -> ApiResponse:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")

    assets = db.execute(
        select(ProjectAsset).where(ProjectAsset.project_id == project.id, ProjectAsset.is_active.is_(True))
    ).scalars().all()

    asset_summary = {
        "script_file_count": 0,
        "persona_doc_count": 0,
        "character_image_count": 0,
        "style_reference_count": 0,
    }
    for asset in assets:
        key = f"{asset.asset_type.value}_count"
        if key in asset_summary:
            asset_summary[key] += 1

    latest_task = db.execute(
        select(RenderTask).where(RenderTask.project_id == project.id).order_by(desc(RenderTask.started_at))
    ).scalars().first()
    final_video = db.execute(
        select(FinalVideo).where(FinalVideo.project_id == project.id).order_by(desc(FinalVideo.created_at))
    ).scalars().first()

    return ApiResponse(
        data={
            "project_id": project.id,
            "name": project.name,
            "description": project.description,
            "target_duration_sec": project.target_duration_sec,
            "style_preset": project.style_preset,
            "status": project.status.value,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "asset_summary": asset_summary,
            "latest_task": _build_latest_task_summary(latest_task),
            "final_video": _build_final_video_summary(final_video),
        }
    )
