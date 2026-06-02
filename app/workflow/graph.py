from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.db.session import SessionLocal
from app.services.script_parse import run_script_parse
from app.services.task_log import create_task_with_log


class WorkflowShot(TypedDict, total=False):
    scene_index: int
    shot_index: int
    duration_sec: float
    characters: list[str]
    visual_prompt: str
    dialogue: str


class WorkflowState(TypedDict, total=False):
    project_id: int
    script_text: str
    shots: list[WorkflowShot]
    status: str


def parse_script(state: WorkflowState) -> WorkflowState:
    project_id = state.get("project_id")
    script_text = state.get("script_text", "")
    if project_id is None:
        raise ValueError("project_id is required")

    with SessionLocal() as db:
        task = create_task_with_log(db, project_id=project_id, stage="script_parse")
        db.commit()
        db.refresh(task)
        shots = run_script_parse(db, project_id=project_id, script_text=script_text, task=task)

    state["status"] = "script_parsed"
    state["shots"] = shots
    return state


def build_graph():
    graph = StateGraph(WorkflowState)
    graph.add_node("parse_script", parse_script)
    graph.set_entry_point("parse_script")
    graph.add_edge("parse_script", END)
    return graph.compile()


workflow = build_graph()
