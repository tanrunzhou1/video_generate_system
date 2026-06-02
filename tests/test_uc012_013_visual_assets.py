from pathlib import Path
import sys

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.base import Base
from app.db.models import CharacterProfile, Project, ProjectStatus, RenderTask, ScriptScene, ShotPlan, VisualAsset
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


def test_generate_visual_asset_and_list(monkeypatch, tmp_path):
    test_session = _build_test_session()
    monkeypatch.setattr("app.services.task_log.settings.logs_dir", str(tmp_path / "logs"))
    monkeypatch.setattr("app.services.visual_generate.settings.storage_dir", str(tmp_path / "storage"))
    monkeypatch.setattr("app.services.visual_generate._call_qwen_image", lambda prompt, resolution, seed: b"fake-png-binary")

    with test_session() as db:
        project = Project(
            name="uc012-project",
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
            scene_text="主角走在夜景街道",
            mood="calm",
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
            characters=["主角"],
            camera_instruction=None,
            visual_prompt="夜景街道，主角独自行走",
        )
        db.add(shot)
        db.commit()
        db.refresh(shot)

        character = CharacterProfile(
            project_id=project.id,
            name="主角",
            persona_text="17 岁女高中生，冷静但有行动力。",
            voice_style="young_female_calm",
            reference_image_paths=["storage/projects/1/character_image/hero_1.jpg"],
            prompt_constraints={"positive": ["黑色短发", "校服"], "negative": ["多余手指"]},
            seed_policy={"mode": "fixed", "seed": 123456},
        )
        db.add(character)
        db.commit()
        project_id = project.id
        shot_id = shot.id

    def override_get_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    create_response = client.post(
        f"/api/v1/projects/{project_id}/shots/{shot_id}/visual-assets",
        json={
            "provider": "qwen-image-2.0",
            "resolution": "720p",
            "override_prompt": None,
        },
    )
    assert create_response.status_code == 200
    create_payload = create_response.json()
    assert create_payload["data"]["project_id"] == project_id
    assert create_payload["data"]["shot_id"] == shot_id
    assert create_payload["data"]["provider"] == "qwen-image-2.0"
    assert create_payload["data"]["resolution"] == "720p"
    assert "角色约束" in create_payload["data"]["prompt_used"]
    assert Path(create_payload["data"]["file_path"]).exists()

    list_response = client.get(f"/api/v1/projects/{project_id}/shots/{shot_id}/visual-assets")
    app.dependency_overrides.clear()

    assert list_response.status_code == 200
    list_payload = list_response.json()
    assert list_payload["data"]["project_id"] == project_id
    assert list_payload["data"]["shot_id"] == shot_id
    assert len(list_payload["data"]["items"]) == 1
    assert list_payload["data"]["items"][0]["provider"] == "qwen-image-2.0"
    assert list_payload["data"]["items"][0]["resolution"] == "720p"

    with test_session() as db:
        assert db.query(VisualAsset).filter(VisualAsset.project_id == project_id, VisualAsset.shot_id == shot_id).count() == 1
        task = db.query(RenderTask).filter(RenderTask.project_id == project_id, RenderTask.stage == "visual_generate").one()
        assert task.status.value == "succeeded"


def test_generate_visual_asset_rejects_invalid_resolution(monkeypatch):
    test_session = _build_test_session()
    monkeypatch.setattr("app.services.task_log.settings.logs_dir", "/tmp/logs")

    with test_session() as db:
        project = Project(
            name="uc012-invalid-resolution",
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
        project_id = project.id
        shot_id = shot.id

    def override_get_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    response = client.post(
        f"/api/v1/projects/{project_id}/shots/{shot_id}/visual-assets",
        json={
            "provider": "qwen-image-2.0",
            "resolution": "2k",
        },
    )
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json()["detail"] == "unsupported resolution"
