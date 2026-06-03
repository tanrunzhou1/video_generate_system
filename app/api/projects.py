from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.db.models import (
    AssetType,
    CharacterProfile,
    FinalVideo,
    Project,
    ProjectAsset,
    ProjectAssetType,
    ProjectStatus,
    RenderTask,
    ShotPlan,
    VisualAsset,
)
from app.db.session import get_db
from app.workflow import graph as workflow_graph
from app.services.task_log import create_task_with_log
from app.services.visual_generate import generate_visual_asset
from app.schemas.project import (
    ApiResponse,
    CharacterProfileCreatedData,
    CharacterProfileDetailData,
    CharacterProfileListData,
    CharacterProfileListItem,
    CreateCharacterProfileRequest,
    CreateTaskRequest,
    CreateProjectRequest,
    CreateVisualAssetRequest,
    ParseScriptTriggeredData,
    ProjectListData,
    ProjectListItem,
    ProjectStatusData,
    TaskCreatedData,
    UploadedAssetItem,
    VisualAssetData,
    VisualAssetListData,
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


def _build_visual_asset_data(asset: VisualAsset) -> VisualAssetData:
    return VisualAssetData(
        asset_id=asset.id,
        project_id=asset.project_id,
        shot_id=asset.shot_id,
        asset_type=asset.asset_type.value,
        provider=asset.provider,
        resolution=asset.resolution or settings.default_image_resolution,
        file_path=asset.file_path,
        prompt_used=asset.prompt_used,
        seed=asset.seed,
        is_selected=asset.is_selected,
    )

def _save_upload_file(project_id: int, asset_type: str, file: UploadFile) -> tuple[str, int]:
    base = Path(settings.storage_dir) / "projects" / str(project_id) / asset_type
    base.mkdir(parents=True, exist_ok=True)
    filename = file.filename or f"{asset_type}.bin"
    dst = base / filename
    content = file.file.read()
    dst.write_bytes(content)
    return str(dst), len(content)


def _get_latest_script_asset(db: Session, project_id: int) -> ProjectAsset | None:
    return (
        db.execute(
            select(ProjectAsset)
            .where(
                ProjectAsset.project_id == project_id,
                ProjectAsset.asset_type == ProjectAssetType.SCRIPT_FILE,
                ProjectAsset.is_active.is_(True),
            )
            .order_by(desc(ProjectAsset.created_at), desc(ProjectAsset.id))
        )
        .scalars()
        .first()
    )


def _require_project(db: Session, project_id: int) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    return project


def _require_shot(db: Session, project_id: int, shot_id: int) -> ShotPlan:
    shot = db.get(ShotPlan, shot_id)
    if shot is None or shot.project_id != project_id:
        raise HTTPException(status_code=404, detail="shot not found")
    return shot


def _load_character_reference_assets(
    db: Session,
    project_id: int,
    asset_ids: list[int],
) -> list[ProjectAsset]:
    if not asset_ids:
        raise HTTPException(status_code=400, detail="reference_image_asset_ids cannot be empty")

    assets = (
        db.execute(
            select(ProjectAsset).where(
                ProjectAsset.project_id == project_id,
                ProjectAsset.id.in_(asset_ids),
                ProjectAsset.is_active.is_(True),
            )
        )
        .scalars()
        .all()
    )
    assets_by_id = {asset.id: asset for asset in assets}

    resolved_assets: list[ProjectAsset] = []
    for asset_id in asset_ids:
        asset = assets_by_id.get(asset_id)
        if asset is None or asset.asset_type != ProjectAssetType.CHARACTER_IMAGE:
            raise HTTPException(status_code=400, detail="invalid character_image asset reference")
        resolved_assets.append(asset)
    return resolved_assets


def _build_character_profile_detail(character: CharacterProfile) -> CharacterProfileDetailData:
    return CharacterProfileDetailData(
        character_id=character.id,
        project_id=character.project_id,
        name=character.name,
        persona_text=character.persona_text,
        voice_style=character.voice_style,
        reference_image_paths=list(character.reference_image_paths or []),
        prompt_constraints=dict(character.prompt_constraints or {}),
        seed_policy=dict(character.seed_policy or {}),
    )


@router.get("", response_model=ApiResponse)
def list_projects(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ApiResponse:
    total = db.execute(select(func.count()).select_from(Project)).scalar_one()
    offset = (page - 1) * page_size

    items = (
        db.execute(
            select(Project)
            .order_by(desc(Project.created_at), desc(Project.id))
            .offset(offset)
            .limit(page_size)
        )
        .scalars()
        .all()
    )

    data = ProjectListData(
        page=page,
        page_size=page_size,
        total=total,
        items=[
            ProjectListItem(
                project_id=item.id,
                name=item.name,
                description=item.description,
                target_duration_sec=item.target_duration_sec,
                style_preset=item.style_preset,
                status=item.status.value,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in items
        ],
    )
    return ApiResponse(data=data.model_dump())


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
    project = _require_project(db, project_id)

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


@router.post("/{project_id}/parse-script", response_model=ApiResponse)
def trigger_parse_script(project_id: int, db: Session = Depends(get_db)) -> ApiResponse:
    project = _require_project(db, project_id)

    script_asset = _get_latest_script_asset(db, project.id)
    if script_asset is None:
        raise HTTPException(status_code=400, detail="script_file asset not found")

    script_path = Path(script_asset.file_path)
    if not script_path.exists():
        raise HTTPException(status_code=404, detail="script file not found")

    script_text = script_path.read_text(encoding="utf-8").strip()
    if not script_text:
        raise HTTPException(status_code=400, detail="script file is empty")

    try:
        workflow_result = workflow_graph.workflow.invoke(
            {
                "project_id": project.id,
                "script_text": script_text,
                "shots": [],
                "status": project.status.value,
            }
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    db.expire_all()
    latest_task = (
        db.execute(
            select(RenderTask)
            .where(RenderTask.project_id == project.id, RenderTask.stage == "script_parse")
            .order_by(desc(RenderTask.id))
        )
        .scalars()
        .first()
    )
    if latest_task is None:
        raise HTTPException(status_code=500, detail="script parse task not created")

    data = ParseScriptTriggeredData(
        project_id=project.id,
        task_id=latest_task.id,
        status=latest_task.status.value,
        workflow_status=workflow_result.get("status", latest_task.status.value),
        shot_count=len(workflow_result.get("shots", [])),
        log_file_path=latest_task.log_file_path or "",
    )
    return ApiResponse(data=data.model_dump())


@router.post("/{project_id}/characters", response_model=ApiResponse)
def create_character_profile(
    project_id: int,
    payload: CreateCharacterProfileRequest,
    db: Session = Depends(get_db),
) -> ApiResponse:
    project = _require_project(db, project_id)
    normalized_name = payload.name.strip()
    persona_text = payload.persona_text.strip()
    voice_style = payload.voice_style.strip()

    if not normalized_name:
        raise HTTPException(status_code=400, detail="character name cannot be blank")
    if not persona_text:
        raise HTTPException(status_code=400, detail="persona_text cannot be blank")
    if not voice_style:
        raise HTTPException(status_code=400, detail="voice_style cannot be blank")

    existing = db.execute(
        select(CharacterProfile.id).where(
            CharacterProfile.project_id == project.id,
            CharacterProfile.name == normalized_name,
        )
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=409, detail="character name already exists in project")

    reference_assets = _load_character_reference_assets(db, project.id, payload.reference_image_asset_ids)
    character = CharacterProfile(
        project_id=project.id,
        name=normalized_name,
        persona_text=persona_text,
        voice_style=voice_style,
        reference_image_paths=[asset.file_path for asset in reference_assets],
        prompt_constraints=dict(payload.prompt_constraints or {}),
        seed_policy=dict(payload.seed_policy or {}),
    )
    db.add(character)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="character name already exists in project")
    db.refresh(character)

    data = CharacterProfileCreatedData(
        character_id=character.id,
        project_id=project.id,
        name=character.name,
        voice_style=character.voice_style,
        reference_image_paths=list(character.reference_image_paths or []),
        created_at=character.created_at,
    )
    return ApiResponse(data=data.model_dump())


@router.get("/{project_id}/characters", response_model=ApiResponse)
def list_character_profiles(project_id: int, db: Session = Depends(get_db)) -> ApiResponse:
    project = _require_project(db, project_id)
    items = (
        db.execute(
            select(CharacterProfile)
            .where(CharacterProfile.project_id == project.id)
            .order_by(CharacterProfile.created_at.asc(), CharacterProfile.id.asc())
        )
        .scalars()
        .all()
    )

    data = CharacterProfileListData(
        project_id=project.id,
        items=[
            CharacterProfileListItem(
                character_id=item.id,
                name=item.name,
                voice_style=item.voice_style,
                reference_image_count=len(item.reference_image_paths or []),
                created_at=item.created_at,
            )
            for item in items
        ],
    )
    return ApiResponse(data=data.model_dump())


@router.get("/{project_id}/characters/{character_id}", response_model=ApiResponse)
def get_character_profile_detail(project_id: int, character_id: int, db: Session = Depends(get_db)) -> ApiResponse:
    project = _require_project(db, project_id)
    character = db.get(CharacterProfile, character_id)
    if character is None or character.project_id != project.id:
        raise HTTPException(status_code=404, detail="character not found")

    data = _build_character_profile_detail(character)
    return ApiResponse(data=data.model_dump())


@router.post("/{project_id}/shots/{shot_id}/visual-assets", response_model=ApiResponse)
def create_visual_asset(
    project_id: int,
    shot_id: int,
    payload: CreateVisualAssetRequest,
    db: Session = Depends(get_db),
) -> ApiResponse:
    _require_project(db, project_id)
    _require_shot(db, project_id, shot_id)

    try:
        asset = generate_visual_asset(
            db,
            project_id=project_id,
            shot_id=shot_id,
            provider=payload.provider,
            resolution=payload.resolution,
            override_prompt=payload.override_prompt,
        )
    except ValueError as exc:
        detail = str(exc)
        if detail in {"project not found", "shot not found"}:
            raise HTTPException(status_code=404, detail=detail) from exc
        raise HTTPException(status_code=400, detail=detail) from exc

    data = _build_visual_asset_data(asset)
    return ApiResponse(data=data.model_dump())


@router.get("/{project_id}/shots/{shot_id}/visual-assets", response_model=ApiResponse)
def list_visual_assets(project_id: int, shot_id: int, db: Session = Depends(get_db)) -> ApiResponse:
    _require_project(db, project_id)
    _require_shot(db, project_id, shot_id)

    items = (
        db.execute(
            select(VisualAsset)
            .where(
                VisualAsset.project_id == project_id,
                VisualAsset.shot_id == shot_id,
                VisualAsset.asset_type == AssetType.IMAGE,
            )
            .order_by(VisualAsset.id.asc())
        )
        .scalars()
        .all()
    )

    data = VisualAssetListData(
        project_id=project_id,
        shot_id=shot_id,
        items=[_build_visual_asset_data(item) for item in items],
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
    project = _require_project(db, project_id)

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
    project = _require_project(db, project_id)

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
    project = _require_project(db, project_id)

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
