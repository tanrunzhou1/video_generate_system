from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.db.models import (
    Project,
    ProjectAsset,
    ProjectAssetType,
    ProjectStatus,
    RenderTask,
)
from app.db.session import get_db
from app.schemas.project import (
    ApiResponse,
    CreateProjectRequest,
    ProjectStatusData,
    UploadedAssetItem,
)

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])
settings = get_settings()


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:16]}"


def _save_upload_file(project_id: str, asset_type: str, file: UploadFile) -> tuple[str, int]:
    base = Path(settings.storage_dir) / "projects" / project_id / asset_type
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
        id=_new_id("prj"),
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


@router.post("/{project_id}/assets", response_model=ApiResponse)
def upload_project_assets(
    project_id: str,
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
            id=_new_id("ast"),
            project_id=project_id,
            asset_type=asset_type,
            file_path=file_path,
            original_name=file.filename or "",
            mime_type=file.content_type or "application/octet-stream",
            size_bytes=size_bytes,
            is_active=True,
        )
        db.add(asset)
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
def get_project_status(project_id: str, db: Session = Depends(get_db)) -> ApiResponse:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")

    latest_task = db.execute(
        select(RenderTask).where(RenderTask.project_id == project_id).order_by(desc(RenderTask.started_at))
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
