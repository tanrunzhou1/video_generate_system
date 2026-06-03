from datetime import datetime, timedelta
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


def _build_test_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def test_list_projects_returns_paginated_items_in_created_at_desc_order():
    test_session = _build_test_session()
    now = datetime(2026, 6, 3, 10, 0, 0)

    with test_session() as db:
        project_1 = Project(
            name="project-oldest",
            description="oldest",
            target_duration_sec=30,
            style_preset="simple",
            status=ProjectStatus.CREATED,
            created_at=now - timedelta(minutes=10),
            updated_at=now - timedelta(minutes=9),
        )
        project_2 = Project(
            name="project-middle",
            description="middle",
            target_duration_sec=45,
            style_preset="cinematic",
            status=ProjectStatus.RUNNING,
            created_at=now - timedelta(minutes=5),
            updated_at=now - timedelta(minutes=4),
        )
        project_3 = Project(
            name="project-latest",
            description="latest",
            target_duration_sec=60,
            style_preset="anime",
            status=ProjectStatus.SUCCEEDED,
            created_at=now,
            updated_at=now + timedelta(minutes=1),
        )
        db.add_all([project_1, project_2, project_3])
        db.commit()

    def override_get_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.get("/api/v1/projects?page=1&page_size=2")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["page"] == 1
    assert payload["data"]["page_size"] == 2
    assert payload["data"]["total"] == 3
    assert len(payload["data"]["items"]) == 2
    assert payload["data"]["items"][0]["name"] == "project-latest"
    assert payload["data"]["items"][1]["name"] == "project-middle"
    assert payload["data"]["items"][0]["created_at"] == "2026-06-03T18:00:00+08:00"
    assert payload["data"]["items"][0]["updated_at"] == "2026-06-03T18:01:00+08:00"


def test_list_projects_rejects_invalid_pagination_arguments():
    test_session = _build_test_session()

    def override_get_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.get("/api/v1/projects?page=0&page_size=10")
    app.dependency_overrides.clear()

    assert response.status_code == 422
