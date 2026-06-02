from pathlib import Path
import sys

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.base import Base
from app.db.models import Project, ProjectStatus
from app.db.session import get_db
from app.main import app
from app.services.task_log import create_task_with_log


def _build_test_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def test_get_task_logs_success(monkeypatch, tmp_path):
    test_session = _build_test_session()
    monkeypatch.setattr("app.services.task_log.settings.logs_dir", str(tmp_path))

    with test_session() as db:
        project = Project(
            name="uc008-success",
            description="",
            target_duration_sec=60,
            style_preset="cinematic",
            status=ProjectStatus.CREATED,
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        task = create_task_with_log(db, project_id=project.id, stage="script_parse")
        db.commit()
        db.refresh(task)
        task_id = task.id

    def override_get_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    response = client.get(f"/api/v1/tasks/{task_id}/logs")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["task_id"] == task_id
    assert payload["data"]["stage"] == "script_parse"
    assert "task created" in payload["data"]["log_content"]


def test_get_task_logs_returns_404_when_file_missing(monkeypatch, tmp_path):
    test_session = _build_test_session()
    monkeypatch.setattr("app.services.task_log.settings.logs_dir", str(tmp_path))

    with test_session() as db:
        project = Project(
            name="uc008-missing-log",
            description="",
            target_duration_sec=60,
            style_preset="cinematic",
            status=ProjectStatus.CREATED,
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        task = create_task_with_log(db, project_id=project.id, stage="script_parse")
        db.commit()
        db.refresh(task)
        task_id = task.id
        log_path = Path(task.log_file_path or "")
        if log_path.exists():
            log_path.unlink()

    def override_get_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    response = client.get(f"/api/v1/tasks/{task_id}/logs")
    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "task log file not found"
