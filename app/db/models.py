from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProjectStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ShotStatus(str, Enum):
    PLANNED = "planned"
    GENERATED = "generated"
    SELECTED = "selected"
    FAILED = "failed"


class AssetType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"


class RenderTaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ProjectAssetType(str, Enum):
    SCRIPT_FILE = "script_file"
    PERSONA_DOC = "persona_doc"
    CHARACTER_IMAGE = "character_image"
    STYLE_REFERENCE = "style_reference"


class Project(Base):
    __tablename__ = "project"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    target_duration_sec: Mapped[int] = mapped_column(Integer, nullable=False)
    style_preset: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[ProjectStatus] = mapped_column(
        SqlEnum(ProjectStatus, name="project_status"),
        nullable=False,
        default=ProjectStatus.CREATED,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class CharacterProfile(Base):
    __tablename__ = "character_profile"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    persona_text: Mapped[str] = mapped_column(Text, nullable=False)
    voice_style: Mapped[str] = mapped_column(String(128), nullable=False)
    reference_image_paths: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    prompt_constraints: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    seed_policy: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)


class ScriptScene(Base):
    __tablename__ = "script_scene"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False, index=True)
    scene_index: Mapped[int] = mapped_column(Integer, nullable=False)
    scene_text: Mapped[str] = mapped_column(Text, nullable=False)
    mood: Mapped[str | None] = mapped_column(String(64))
    estimated_duration_sec: Mapped[int] = mapped_column(Integer, nullable=False)


class ShotPlan(Base):
    __tablename__ = "shot_plan"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False, index=True)
    scene_id: Mapped[int] = mapped_column(ForeignKey("script_scene.id"), nullable=False, index=True)
    shot_index: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_sec: Mapped[float] = mapped_column(Float, nullable=False)
    characters: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    camera_instruction: Mapped[str | None] = mapped_column(String(512))
    visual_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ShotStatus] = mapped_column(
        SqlEnum(ShotStatus, name="shot_status"), nullable=False, default=ShotStatus.PLANNED
    )


class VisualAsset(Base):
    __tablename__ = "visual_asset"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False, index=True)
    shot_id: Mapped[int] = mapped_column(ForeignKey("shot_plan.id"), nullable=False, index=True)
    asset_type: Mapped[AssetType] = mapped_column(SqlEnum(AssetType, name="asset_type"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    provider: Mapped[str] = mapped_column(String(128), nullable=False)
    prompt_used: Mapped[str] = mapped_column(Text, nullable=False)
    seed: Mapped[int | None] = mapped_column(Integer)
    consistency_score: Mapped[float | None] = mapped_column(Float)
    is_selected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class VoiceAsset(Base):
    __tablename__ = "voice_asset"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False, index=True)
    shot_id: Mapped[int] = mapped_column(ForeignKey("shot_plan.id"), nullable=False, index=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("character_profile.id"), nullable=False, index=True)
    line_text: Mapped[str] = mapped_column(Text, nullable=False)
    voice_provider: Mapped[str] = mapped_column(String(128), nullable=False)
    audio_path: Mapped[str] = mapped_column(String(512), nullable=False)
    start_time_sec: Mapped[float] = mapped_column(Float, nullable=False)
    end_time_sec: Mapped[float] = mapped_column(Float, nullable=False)


class SubtitleSegment(Base):
    __tablename__ = "subtitle_segment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False, index=True)
    shot_id: Mapped[int] = mapped_column(ForeignKey("shot_plan.id"), nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    start_time_sec: Mapped[float] = mapped_column(Float, nullable=False)
    end_time_sec: Mapped[float] = mapped_column(Float, nullable=False)


class BgmAsset(Base):
    __tablename__ = "bgm_asset"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False, index=True)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    mood_tag: Mapped[str | None] = mapped_column(String(64))
    start_time_sec: Mapped[float] = mapped_column(Float, nullable=False)
    end_time_sec: Mapped[float] = mapped_column(Float, nullable=False)
    gain_db: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)


class RenderTask(Base):
    __tablename__ = "render_task"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False, index=True)
    stage: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[RenderTaskStatus] = mapped_column(
        SqlEnum(RenderTaskStatus, name="render_task_status"),
        nullable=False,
        default=RenderTaskStatus.PENDING,
    )
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_code: Mapped[str | None] = mapped_column(String(128))
    error_message: Mapped[str | None] = mapped_column(Text)
    log_file_path: Mapped[str | None] = mapped_column(String(512))
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)


class FinalVideo(Base):
    __tablename__ = "final_video"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False, index=True)
    resolution: Mapped[str] = mapped_column(String(32), nullable=False)
    duration_sec: Mapped[float] = mapped_column(Float, nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    cover_image_path: Mapped[str | None] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class ProjectAsset(Base):
    __tablename__ = "project_asset"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False)
    asset_type: Mapped[ProjectAssetType] = mapped_column(
        SqlEnum(ProjectAssetType, name="project_asset_type"), nullable=False
    )
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
