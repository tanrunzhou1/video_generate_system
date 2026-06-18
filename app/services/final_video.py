import base64
from pathlib import Path

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.db.models import AudioMixAsset, FinalVideo, Project, RenderTask, ShotPlan, SubtitleSegment, VisualAsset
from app.services.task_log import create_task_with_log, mark_task_failed, mark_task_running, mark_task_succeeded

settings = get_settings()

SUPPORTED_EXPORT_RESOLUTIONS = {"720p", "1080p"}
SUPPORTED_TRANSITION_MODES = {"none"}
_MOCK_PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wn3Fo4AAAAASUVORK5CYII="
)


def _write_mock_video(path: Path, project_id: int, resolution: str, duration_sec: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(f"mock-final-video project={project_id} resolution={resolution} duration={duration_sec}".encode("utf-8"))


def _write_cover_image(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_MOCK_PNG_BYTES)


def _select_latest_or_selected_asset(items: list[VisualAsset] | list[AudioMixAsset]):
    selected = [item for item in items if getattr(item, "is_selected", False)]
    if selected:
        return max(selected, key=lambda item: item.id)
    return max(items, key=lambda item: item.id) if items else None


def export_final_video(
    db: Session,
    *,
    project_id: int,
    resolution: str,
    include_subtitles: bool,
    transition_mode: str,
) -> tuple[RenderTask, FinalVideo]:
    normalized_resolution = resolution.strip()
    if normalized_resolution not in SUPPORTED_EXPORT_RESOLUTIONS:
        raise ValueError("unsupported resolution")

    normalized_transition_mode = transition_mode.strip()
    if normalized_transition_mode not in SUPPORTED_TRANSITION_MODES:
        raise ValueError("unsupported transition_mode")

    project = db.get(Project, project_id)
    if project is None:
        raise ValueError("project not found")

    shots = (
        db.execute(
            select(ShotPlan)
            .where(ShotPlan.project_id == project_id)
            .order_by(ShotPlan.scene_id.asc(), ShotPlan.shot_index.asc(), ShotPlan.id.asc())
        )
        .scalars()
        .all()
    )
    if not shots:
        raise ValueError("shot not found")

    task: RenderTask | None = None
    try:
        task = create_task_with_log(db, project_id=project_id, stage="final_video_export")
        db.commit()
        db.refresh(task)

        mark_task_running(db, task)
        db.commit()

        selected_visual_assets: list[VisualAsset] = []
        selected_audio_mix_assets: list[AudioMixAsset] = []
        total_duration_sec = 0.0

        for shot in shots:
            visual_assets = (
                db.execute(
                    select(VisualAsset)
                    .where(VisualAsset.project_id == project_id, VisualAsset.shot_id == shot.id)
                    .order_by(desc(VisualAsset.id))
                )
                .scalars()
                .all()
            )
            visual_asset = _select_latest_or_selected_asset(visual_assets)
            if visual_asset is None:
                raise ValueError("visual_asset not found")

            audio_mix_assets = (
                db.execute(
                    select(AudioMixAsset)
                    .where(AudioMixAsset.project_id == project_id, AudioMixAsset.shot_id == shot.id)
                    .order_by(desc(AudioMixAsset.id))
                )
                .scalars()
                .all()
            )
            audio_mix_asset = _select_latest_or_selected_asset(audio_mix_assets)
            if audio_mix_asset is None:
                raise ValueError("audio_mix_asset not found")

            if include_subtitles:
                subtitle_exists = db.execute(
                    select(SubtitleSegment.id)
                    .where(SubtitleSegment.project_id == project_id, SubtitleSegment.shot_id == shot.id)
                    .limit(1)
                ).scalar_one_or_none()
                if subtitle_exists is None:
                    raise ValueError("subtitle_segment not found")

            selected_visual_assets.append(visual_asset)
            selected_audio_mix_assets.append(audio_mix_asset)
            total_duration_sec += shot.duration_sec

        video = FinalVideo(
            project_id=project_id,
            resolution=normalized_resolution,
            duration_sec=round(total_duration_sec, 2),
            file_path="",
            cover_image_path="",
        )
        db.add(video)
        db.flush()

        base_dir = Path(settings.storage_dir) / "projects" / str(project_id) / "final_video"
        video_path = base_dir / f"final_{normalized_resolution}_{video.id}.mp4"
        cover_path = base_dir / f"final_{normalized_resolution}_{video.id}_cover.png"
        _write_mock_video(video_path, project_id, normalized_resolution, video.duration_sec)
        _write_cover_image(cover_path)
        video.file_path = str(video_path)
        video.cover_image_path = str(cover_path)
        db.flush()

        if task is not None:
            mark_task_succeeded(
                db,
                task,
                (
                    "final video exported: "
                    f"video_id={video.id}, resolution={normalized_resolution}, "
                    f"include_subtitles={include_subtitles}, transition_mode={normalized_transition_mode}, "
                    f"shot_count={len(shots)}"
                ),
            )
        db.commit()
        db.refresh(task)
        db.refresh(video)
        return task, video
    except Exception as exc:
        db.rollback()
        if task is not None:
            db.add(task)
            mark_task_failed(db, task, "FINAL_VIDEO_EXPORT_FAILED", str(exc))
            db.commit()
        raise


def list_final_videos(db: Session, project_id: int) -> list[FinalVideo]:
    return (
        db.execute(
            select(FinalVideo)
            .where(FinalVideo.project_id == project_id)
            .order_by(desc(FinalVideo.created_at), desc(FinalVideo.id))
        )
        .scalars()
        .all()
    )
