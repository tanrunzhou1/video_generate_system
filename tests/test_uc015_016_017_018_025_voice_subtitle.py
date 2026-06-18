from pathlib import Path
import sys

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.base import Base
from app.db.models import CharacterProfile, Project, ProjectStatus, ScriptScene, ShotDialogue, ShotPlan, SubtitleSegment, VoiceAsset
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


def test_list_shots_and_generate_voice_and_subtitles(monkeypatch, tmp_path):
    test_session = _build_test_session()
    monkeypatch.setattr("app.services.voice_subtitle.settings.storage_dir", str(tmp_path / "storage"))

    with test_session() as db:
        project = Project(
            name="uc015-project",
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
            scene_text="主角与朋友对话",
            mood="calm",
            estimated_duration_sec=8,
        )
        db.add(scene)
        db.commit()
        db.refresh(scene)

        shot = ShotPlan(
            project_id=project.id,
            scene_id=scene.id,
            shot_index=1,
            duration_sec=8.0,
            characters=["主角", "朋友"],
            camera_instruction="中景",
            visual_prompt="两人站在路灯下交谈",
        )
        db.add(shot)
        db.commit()
        db.refresh(shot)

        db.add_all(
            [
                ShotDialogue(
                    project_id=project.id,
                    shot_id=shot.id,
                    character_name="主角",
                    text="今天开始行动。",
                    sequence_no=1,
                ),
                ShotDialogue(
                    project_id=project.id,
                    shot_id=shot.id,
                    character_name="朋友",
                    text="我会配合你。",
                    sequence_no=2,
                ),
            ]
        )
        db.add_all(
            [
                CharacterProfile(
                    project_id=project.id,
                    name="主角",
                    persona_text="冷静的女高中生",
                    voice_style="young_female_calm",
                    reference_image_paths=["/tmp/hero.jpg"],
                    prompt_constraints={},
                    seed_policy={},
                ),
                CharacterProfile(
                    project_id=project.id,
                    name="朋友",
                    persona_text="外向的男生",
                    voice_style="young_male_bright",
                    reference_image_paths=["/tmp/friend.jpg"],
                    prompt_constraints={},
                    seed_policy={},
                ),
            ]
        )
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

    shots_response = client.get(f"/api/v1/projects/{project_id}/shots")
    assert shots_response.status_code == 200
    shots_payload = shots_response.json()
    assert shots_payload["data"]["items"][0]["shot_id"] == shot_id
    assert shots_payload["data"]["items"][0]["dialogue_count"] == 2

    voice_response = client.post(
        f"/api/v1/projects/{project_id}/shots/{shot_id}/voice-assets",
        json={"provider": "xtts-v2", "source": "shot_dialogues"},
    )
    assert voice_response.status_code == 200
    voice_payload = voice_response.json()
    assert voice_payload["data"]["project_id"] == project_id
    assert voice_payload["data"]["shot_id"] == shot_id
    assert len(voice_payload["data"]["items"]) == 2
    assert voice_payload["data"]["items"][0]["dialogue_id"] > 0
    assert Path(voice_payload["data"]["items"][0]["audio_path"]).exists()

    voice_list_response = client.get(f"/api/v1/projects/{project_id}/shots/{shot_id}/voice-assets")
    assert voice_list_response.status_code == 200
    assert len(voice_list_response.json()["data"]["items"]) == 2

    subtitle_response = client.post(
        f"/api/v1/projects/{project_id}/shots/{shot_id}/subtitle-segments",
        json={"source": "voice_assets"},
    )
    assert subtitle_response.status_code == 200
    subtitle_payload = subtitle_response.json()
    assert len(subtitle_payload["data"]["items"]) == 2
    assert subtitle_payload["data"]["items"][0]["text"] == "今天开始行动。"

    subtitle_list_response = client.get(f"/api/v1/projects/{project_id}/shots/{shot_id}/subtitle-segments")
    app.dependency_overrides.clear()

    assert subtitle_list_response.status_code == 200
    assert len(subtitle_list_response.json()["data"]["items"]) == 2

    with test_session() as db:
        assert db.query(VoiceAsset).filter(VoiceAsset.project_id == project_id, VoiceAsset.shot_id == shot_id).count() == 2
        assert db.query(SubtitleSegment).filter(SubtitleSegment.project_id == project_id, SubtitleSegment.shot_id == shot_id).count() == 2


def test_generate_voice_assets_rejects_missing_dialogue(monkeypatch):
    test_session = _build_test_session()
    monkeypatch.setattr("app.services.voice_subtitle.settings.storage_dir", "/tmp/storage")

    with test_session() as db:
        project = Project(
            name="uc015-missing-dialogue",
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
            scene_text="空对白镜头",
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
            visual_prompt="空镜头",
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
        f"/api/v1/projects/{project_id}/shots/{shot_id}/voice-assets",
        json={"provider": "xtts-v2", "source": "shot_dialogues"},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json()["detail"] == "shot_dialogue not found"
