from pathlib import Path
import sys

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.base import Base
from app.db.models import AudioMixAsset, FinalVideo, Project, ProjectStatus, RenderTask, ScriptScene, ShotPlan, SubtitleSegment, VisualAsset
from app.db.session import get_db
from app.main import app


def _build_test_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def test_export_final_video_and_query_results(monkeypatch, tmp_path):
    test_session = _build_test_session()
    monkeypatch.setattr("app.services.final_video.settings.storage_dir", str(tmp_path / "storage"))
    monkeypatch.setattr("app.services.task_log.settings.logs_dir", str(tmp_path / "logs"))

    with test_session() as db:
        project = Project(
            name="uc022-project",
            description="",
            target_duration_sec=60,
            style_preset="cinematic",
            status=ProjectStatus.CREATED,
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        scene = ScriptScene(
            project_id=project.id,
            scene_index=1,
            scene_text="主角走向远方",
            mood="hopeful",
            estimated_duration_sec=6,
        )
        db.add(scene)
        db.commit()
        db.refresh(scene)

        shot = ShotPlan(
            project_id=project.id,
            scene_id=scene.id,
            shot_index=1,
            duration_sec=6.0,
            characters=["主角"],
            camera_instruction="远景",
            visual_prompt="主角走向夕阳",
        )
        db.add(shot)
        db.commit()
        db.refresh(shot)

        visual_asset = VisualAsset(
            project_id=project.id,
            shot_id=shot.id,
            asset_type="image",
            file_path=str(tmp_path / "storage" / "visual.png"),
            provider="qwen-image-2.0",
            resolution="720p",
            prompt_used="主角走向夕阳",
            seed=123,
            consistency_score=None,
            is_selected=True,
        )
        db.add(visual_asset)
        db.flush()
        Path(visual_asset.file_path).parent.mkdir(parents=True, exist_ok=True)
        Path(visual_asset.file_path).write_bytes(b"png")

        audio_mix_asset = AudioMixAsset(
            project_id=project.id,
            shot_id=shot.id,
            bgm_asset_id=1,
            mixed_audio_path=str(tmp_path / "storage" / "mix.wav"),
            ducking_gain_db=-10.0,
            fade_in_sec=0.3,
            fade_out_sec=0.5,
            is_selected=True,
        )
        db.add(audio_mix_asset)
        db.flush()
        Path(audio_mix_asset.mixed_audio_path).write_bytes(b"wav")

        subtitle_segment = SubtitleSegment(
            project_id=project.id,
            shot_id=shot.id,
            text="我们出发吧。",
            start_time_sec=0.0,
            end_time_sec=2.0,
        )
        db.add(subtitle_segment)
        db.commit()
        project_id = project.id

    def override_get_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    export_response = client.post(
        f"/api/v1/projects/{project_id}/final-videos",
        json={
            "resolution": "720p",
            "include_subtitles": True,
            "transition_mode": "none",
        },
    )
    assert export_response.status_code == 200
    export_payload = export_response.json()["data"]
    assert export_payload["project_id"] == project_id
    assert export_payload["resolution"] == "720p"
    assert export_payload["include_subtitles"] is True
    assert export_payload["transition_mode"] == "none"
    assert Path(export_payload["file_path"]).exists()

    list_response = client.get(f"/api/v1/projects/{project_id}/final-videos")
    assert list_response.status_code == 200
    list_payload = list_response.json()["data"]
    assert len(list_payload["items"]) == 1
    video_id = list_payload["items"][0]["video_id"]

    detail_response = client.get(f"/api/v1/projects/{project_id}/final-videos/{video_id}")
    app.dependency_overrides.clear()

    assert detail_response.status_code == 200
    detail_payload = detail_response.json()["data"]
    assert detail_payload["video_id"] == video_id
    assert detail_payload["project_id"] == project_id
    assert Path(detail_payload["file_path"]).exists()
    assert Path(detail_payload["cover_image_path"]).exists()

    with test_session() as db:
        assert db.query(FinalVideo).filter(FinalVideo.project_id == project_id).count() == 1
        task = db.query(RenderTask).filter(RenderTask.project_id == project_id, RenderTask.stage == "final_video_export").one()
        assert task.status.value == "succeeded"


def test_export_final_video_rejects_missing_audio_mix(monkeypatch, tmp_path):
    test_session = _build_test_session()
    monkeypatch.setattr("app.services.final_video.settings.storage_dir", str(tmp_path / "storage"))
    monkeypatch.setattr("app.services.task_log.settings.logs_dir", str(tmp_path / "logs"))

    with test_session() as db:
        project = Project(
            name="uc022-missing-audio",
            description="",
            target_duration_sec=60,
            style_preset="cinematic",
            status=ProjectStatus.CREATED,
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        scene = ScriptScene(
            project_id=project.id,
            scene_index=1,
            scene_text="测试镜头",
            mood=None,
            estimated_duration_sec=5,
        )
        db.add(scene)
        db.commit()
        db.refresh(scene)

        shot = ShotPlan(
            project_id=project.id,
            scene_id=scene.id,
            shot_index=1,
            duration_sec=5.0,
            characters=[],
            camera_instruction=None,
            visual_prompt="测试提示词",
        )
        db.add(shot)
        db.commit()
        db.refresh(shot)

        visual_asset = VisualAsset(
            project_id=project.id,
            shot_id=shot.id,
            asset_type="image",
            file_path=str(tmp_path / "storage" / "only_visual.png"),
            provider="qwen-image-2.0",
            resolution="720p",
            prompt_used="测试提示词",
            seed=None,
            consistency_score=None,
            is_selected=True,
        )
        db.add(visual_asset)
        db.flush()
        Path(visual_asset.file_path).parent.mkdir(parents=True, exist_ok=True)
        Path(visual_asset.file_path).write_bytes(b"png")
        db.commit()
        project_id = project.id

    def override_get_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    response = client.post(
        f"/api/v1/projects/{project_id}/final-videos",
        json={
            "resolution": "720p",
            "include_subtitles": False,
            "transition_mode": "none",
        },
    )
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json()["detail"] == "audio_mix_asset not found"
