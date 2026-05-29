from typing import TypedDict
from langgraph.graph import StateGraph, END

class WorkflowState(TypedDict, total=False):
    project_id: int
    script_text: str
    shots: list
    status: str

def parse_script(state: WorkflowState) -> WorkflowState:
    # TODO: 接 LLM 做 scene/shot 拆解
    state["status"] = "script_parsed"
    state["shots"] = []
    return state

def build_graph():
    graph = StateGraph(WorkflowState)
    graph.add_node("parse_script", parse_script)
    graph.set_entry_point("parse_script")
    graph.add_edge("parse_script", END)
    return graph.compile()

workflow = build_graph()
