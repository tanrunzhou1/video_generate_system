from pathlib import Path
import sys

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.base import Base
from app.db.models import Project, ProjectAsset, ProjectAssetType, ProjectStatus, RenderTask, ScriptScene, ShotDialogue, ShotPlan
from app.db.session import get_db
from app.main import app
from app.workflow import graph as workflow_graph


def _build_test_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def test_trigger_parse_script_success(monkeypatch, tmp_path):
    test_session = _build_test_session()
    monkeypatch.setattr(workflow_graph, "SessionLocal", test_session)
    monkeypatch.setattr("app.services.task_log.settings.logs_dir", str(tmp_path / "logs"))
    monkeypatch.setattr(
        "app.services.script_parse._call_qwen",
        lambda script_text: (
            '{"shots":['
            '{"scene_index":1,"shot_index":1,"duration_sec":5.0,"characters":["主角"],'
            '"visual_prompt":"夜景街道，主角独自行走","dialogue":"我要出发了"},'
            '{"scene_index":1,"shot_index":2,"duration_sec":4.0,"characters":["主角","朋友"],'
            '"visual_prompt":"两人汇合，准备出发","dialogue":"我们走吧"}'
            "]}"
        ),
    )

    script_path = tmp_path / "script.md"
    script_path.write_text("主角在夜景街道行走，随后与朋友汇合。", encoding="utf-8")

    with test_session() as db:
        project = Project(
            name="uc006-api-success",
            description="",
            target_duration_sec=60,
            style_preset="cinematic",
            status=ProjectStatus.CREATED,
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        db.add(
            ProjectAsset(
                project_id=project.id,
                asset_type=ProjectAssetType.SCRIPT_FILE,
                file_path=str(script_path),
                original_name="script.md",
                mime_type="text/markdown",
                size_bytes=script_path.stat().st_size,
                is_active=True,
            )
        )
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
    response = client.post(f"/api/v1/projects/{project_id}/parse-script")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["project_id"] == project_id
    assert payload["data"]["status"] == "succeeded"
    assert payload["data"]["workflow_status"] == "script_parsed"
    assert payload["data"]["shot_count"] == 2

    with test_session() as db:
        assert db.query(RenderTask).filter(RenderTask.project_id == project_id).count() == 1
        assert db.query(ScriptScene).filter(ScriptScene.project_id == project_id).count() == 1
        assert db.query(ShotPlan).filter(ShotPlan.project_id == project_id).count() == 2
        assert db.query(ShotDialogue).filter(ShotDialogue.project_id == project_id).count() == 2


def test_trigger_parse_script_returns_400_without_script_asset(monkeypatch):
    test_session = _build_test_session()
    monkeypatch.setattr(workflow_graph, "SessionLocal", test_session)

    with test_session() as db:
        project = Project(
            name="uc006-api-no-script",
            description="",
            target_duration_sec=60,
            style_preset="cinematic",
            status=ProjectStatus.CREATED,
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        project_id = project.id

    def override_get_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    response = client.post(f"/api/v1/projects/{project_id}/parse-script")
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json()["detail"] == "script_file asset not found"
