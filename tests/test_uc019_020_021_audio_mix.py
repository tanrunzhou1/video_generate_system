from pathlib import Path
import sys

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.base import Base
from app.db.models import AudioMixAsset, BgmAsset, CharacterProfile, Project, ProjectStatus, ScriptScene, ShotDialogue, ShotPlan, VoiceAsset
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


def test_create_and_list_bgm_assets_and_mix_audio(monkeypatch, tmp_path):
    test_session = _build_test_session()
    monkeypatch.setattr("app.services.voice_subtitle.settings.storage_dir", str(tmp_path / "storage"))
    monkeypatch.setattr("app.services.audio_mix.settings.storage_dir", str(tmp_path / "storage"))

    with test_session() as db:
        project = Project(
            name="uc019-project",
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
            scene_text="角色在天台说话",
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
            characters=["主角"],
            camera_instruction="近景",
            visual_prompt="主角站在傍晚天台",
        )
        db.add(shot)
        db.commit()
        db.refresh(shot)

        db.add(
            CharacterProfile(
                project_id=project.id,
                name="主角",
                persona_text="冷静的高中生",
                voice_style="young_female_calm",
                reference_image_paths=["/tmp/hero.jpg"],
                prompt_constraints={},
                seed_policy={},
            )
        )
        db.add(
            ShotDialogue(
                project_id=project.id,
                shot_id=shot.id,
                character_name="主角",
                text="我们开始吧。",
                sequence_no=1,
            )
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

    voice_response = client.post(
        f"/api/v1/projects/{project_id}/shots/{shot_id}/voice-assets",
        json={"provider": "xtts-v2", "source": "shot_dialogues"},
    )
    assert voice_response.status_code == 200
    assert len(voice_response.json()["data"]["items"]) == 1

    create_bgm_response = client.post(
        f"/api/v1/projects/{project_id}/bgm-assets",
        json={
            "file_path": "storage/projects/1/bgm/calm_theme.mp3",
            "mood_tag": "calm",
            "start_time_sec": 0.0,
            "end_time_sec": 18.0,
            "gain_db": -6.0,
        },
    )
    assert create_bgm_response.status_code == 200
    bgm_asset_id = create_bgm_response.json()["data"]["bgm_asset_id"]

    list_bgm_response = client.get(f"/api/v1/projects/{project_id}/bgm-assets")
    assert list_bgm_response.status_code == 200
    assert len(list_bgm_response.json()["data"]["items"]) == 1

    mix_response = client.post(
        f"/api/v1/projects/{project_id}/shots/{shot_id}/audio-mix",
        json={
            "bgm_asset_id": bgm_asset_id,
            "ducking_gain_db": -10.0,
            "fade_in_sec": 0.3,
            "fade_out_sec": 0.5,
        },
    )
    app.dependency_overrides.clear()

    assert mix_response.status_code == 200
    mix_payload = mix_response.json()["data"]
    assert mix_payload["project_id"] == project_id
    assert mix_payload["shot_id"] == shot_id
    assert mix_payload["bgm_asset_id"] == bgm_asset_id
    assert len(mix_payload["voice_asset_ids"]) == 1
    assert Path(mix_payload["mixed_audio_path"]).exists()

    with test_session() as db:
        assert db.query(BgmAsset).filter(BgmAsset.project_id == project_id).count() == 1
        assert db.query(VoiceAsset).filter(VoiceAsset.project_id == project_id, VoiceAsset.shot_id == shot_id).count() == 1
        assert db.query(AudioMixAsset).filter(AudioMixAsset.project_id == project_id, AudioMixAsset.shot_id == shot_id).count() == 1


def test_create_audio_mix_rejects_missing_voice_assets(monkeypatch):
    test_session = _build_test_session()
    monkeypatch.setattr("app.services.audio_mix.settings.storage_dir", "/tmp/storage")

    with test_session() as db:
        project = Project(
            name="uc021-no-voice",
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
            scene_text="空镜头",
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

        bgm = BgmAsset(
            project_id=project.id,
            file_path="storage/projects/1/bgm/empty.mp3",
            mood_tag="calm",
            start_time_sec=0.0,
            end_time_sec=6.0,
            gain_db=-6.0,
        )
        db.add(bgm)
        db.commit()
        db.refresh(bgm)
        project_id = project.id
        shot_id = shot.id
        bgm_asset_id = bgm.id

    def override_get_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    response = client.post(
        f"/api/v1/projects/{project_id}/shots/{shot_id}/audio-mix",
        json={
            "bgm_asset_id": bgm_asset_id,
            "ducking_gain_db": -8.0,
            "fade_in_sec": 0.2,
            "fade_out_sec": 0.2,
        },
    )
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json()["detail"] == "voice_asset not found"
