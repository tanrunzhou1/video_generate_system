from pathlib import Path
import sys

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.base import Base
from app.db.models import CharacterProfile, Project, ProjectAsset, ProjectAssetType, ProjectStatus
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


def test_create_character_profile_and_query_it():
    test_session = _build_test_session()

    with test_session() as db:
        project = Project(
            name="uc009-project",
            description="",
            target_duration_sec=60,
            style_preset="cinematic",
            status=ProjectStatus.CREATED,
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        asset_1 = ProjectAsset(
            project_id=project.id,
            asset_type=ProjectAssetType.CHARACTER_IMAGE,
            file_path="storage/projects/1/character_image/hero_1.jpg",
            original_name="hero_1.jpg",
            mime_type="image/jpeg",
            size_bytes=1024,
            is_active=True,
        )
        asset_2 = ProjectAsset(
            project_id=project.id,
            asset_type=ProjectAssetType.CHARACTER_IMAGE,
            file_path="storage/projects/1/character_image/hero_2.jpg",
            original_name="hero_2.jpg",
            mime_type="image/jpeg",
            size_bytes=2048,
            is_active=True,
        )
        db.add_all([asset_1, asset_2])
        db.commit()
        db.refresh(asset_1)
        db.refresh(asset_2)
        project_id = project.id
        asset_ids = [asset_1.id, asset_2.id]

    def override_get_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    create_response = client.post(
        f"/api/v1/projects/{project_id}/characters",
        json={
            "name": "主角",
            "persona_text": "17 岁女高中生，冷静但有行动力。",
            "voice_style": "young_female_calm",
            "reference_image_asset_ids": asset_ids,
            "prompt_constraints": {
                "positive": ["黑色短发", "校服"],
                "negative": ["多余手指"],
            },
            "seed_policy": {"mode": "fixed", "seed": 123456},
        },
    )
    assert create_response.status_code == 200
    create_payload = create_response.json()
    assert create_payload["data"]["project_id"] == project_id
    assert len(create_payload["data"]["reference_image_paths"]) == 2
    character_id = create_payload["data"]["character_id"]

    list_response = client.get(f"/api/v1/projects/{project_id}/characters")
    assert list_response.status_code == 200
    list_payload = list_response.json()
    assert list_payload["data"]["project_id"] == project_id
    assert len(list_payload["data"]["items"]) == 1
    assert list_payload["data"]["items"][0]["character_id"] == character_id
    assert list_payload["data"]["items"][0]["reference_image_count"] == 2

    detail_response = client.get(f"/api/v1/projects/{project_id}/characters/{character_id}")
    app.dependency_overrides.clear()

    assert detail_response.status_code == 200
    detail_payload = detail_response.json()
    assert detail_payload["data"]["character_id"] == character_id
    assert detail_payload["data"]["name"] == "主角"
    assert detail_payload["data"]["seed_policy"]["seed"] == 123456

    with test_session() as db:
        saved = db.get(CharacterProfile, character_id)
        assert saved is not None
        assert saved.project_id == project_id
        assert len(saved.reference_image_paths) == 2


def test_create_character_profile_rejects_invalid_asset_type():
    test_session = _build_test_session()

    with test_session() as db:
        project = Project(
            name="uc009-invalid-asset",
            description="",
            target_duration_sec=60,
            style_preset="cinematic",
            status=ProjectStatus.CREATED,
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        invalid_asset = ProjectAsset(
            project_id=project.id,
            asset_type=ProjectAssetType.SCRIPT_FILE,
            file_path="storage/projects/2/script/script.md",
            original_name="script.md",
            mime_type="text/markdown",
            size_bytes=512,
            is_active=True,
        )
        db.add(invalid_asset)
        db.commit()
        db.refresh(invalid_asset)
        project_id = project.id
        asset_id = invalid_asset.id

    def override_get_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    response = client.post(
        f"/api/v1/projects/{project_id}/characters",
        json={
            "name": "主角",
            "persona_text": "角色设定",
            "voice_style": "young_female_calm",
            "reference_image_asset_ids": [asset_id],
            "prompt_constraints": {},
            "seed_policy": {},
        },
    )
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json()["detail"] == "invalid character_image asset reference"
