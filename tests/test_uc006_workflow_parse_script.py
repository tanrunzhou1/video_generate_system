from pathlib import Path
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.base import Base
from app.db.models import Project, ProjectStatus, RenderTask, ScriptScene, ShotPlan
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


def test_parse_script_success(monkeypatch, tmp_path):
    test_session = _build_test_session()
    monkeypatch.setattr(workflow_graph, "SessionLocal", test_session)
    monkeypatch.setattr("app.services.task_log.settings.logs_dir", str(tmp_path))
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

    with test_session() as db:
        project = Project(
            name="uc006-success",
            description="",
            target_duration_sec=60,
            style_preset="cinematic",
            status=ProjectStatus.CREATED,
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        project_id = project.id

    result = workflow_graph.workflow.invoke(
        {
            "project_id": project_id,
            "script_text": "主角在夜景街道行走，随后与朋友汇合。",
            "shots": [],
            "status": "created",
        }
    )

    assert result["status"] == "script_parsed"
    assert len(result["shots"]) == 2

    with test_session() as db:
        assert db.query(ScriptScene).filter(ScriptScene.project_id == project_id).count() == 1
        assert db.query(ShotPlan).filter(ShotPlan.project_id == project_id).count() == 2
        task = db.query(RenderTask).filter(RenderTask.project_id == project_id).one()
        assert task.status.value == "succeeded"
        assert task.log_file_path is not None
        assert Path(task.log_file_path).exists()


def test_parse_script_blank_text_marks_task_failed(monkeypatch, tmp_path):
    test_session = _build_test_session()
    monkeypatch.setattr(workflow_graph, "SessionLocal", test_session)
    monkeypatch.setattr("app.services.task_log.settings.logs_dir", str(tmp_path))

    with test_session() as db:
        project = Project(
            name="uc006-blank",
            description="",
            target_duration_sec=60,
            style_preset="cinematic",
            status=ProjectStatus.CREATED,
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        project_id = project.id

    try:
        workflow_graph.workflow.invoke(
            {
                "project_id": project_id,
                "script_text": "   ",
                "shots": [],
                "status": "created",
            }
        )
        raised = False
    except ValueError:
        raised = True

    assert raised is True

    with test_session() as db:
        project = db.get(Project, project_id)
        task = db.query(RenderTask).filter(RenderTask.project_id == project_id).one()
        assert project.status.value == "failed"
        assert task.status.value == "failed"
        assert task.error_code == "SCRIPT_PARSE_FAILED"
