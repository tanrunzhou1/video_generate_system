import json
from collections.abc import Iterable

from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.db.models import Project, ProjectStatus, ScriptScene, ShotDialogue, ShotPlan
from app.services.task_log import mark_task_failed, mark_task_running, mark_task_succeeded

settings = get_settings()


class ShotDraft(BaseModel):
    scene_index: int = Field(ge=1)
    shot_index: int = Field(ge=1)
    duration_sec: float = Field(gt=0)
    characters: list[str] = Field(default_factory=list)
    visual_prompt: str = Field(min_length=1)
    dialogue: str | None = None


def _clean_llm_json(content: str) -> str:
    stripped = content.strip()
    if stripped.startswith("```"):
        parts = stripped.split("```")
        for part in parts:
            candidate = part.strip()
            if candidate and not candidate.lower().startswith("json"):
                return candidate
        return stripped.replace("```", "").replace("json", "", 1).strip()
    return stripped


def _call_qwen(script_text: str) -> str:
    if not settings.qwen_api_key:
        raise ValueError("QWEN_API_KEY is not configured")

    client = OpenAI(api_key=settings.qwen_api_key, base_url=settings.qwen_base_url)
    prompt = (
        "你是短片分镜规划助手。"
        "请把输入剧本拆解为镜头列表，并严格返回 JSON 对象，格式为"
        '{"shots":[{"scene_index":1,"shot_index":1,"duration_sec":5.0,"characters":["主角"],'
        '"visual_prompt":"画面提示词","dialogue":"台词"}]}。'
        "不要输出任何解释、Markdown 或代码块。"
    )
    response = client.chat.completions.create(
        model=settings.qwen_model,
        temperature=0.2,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": script_text},
        ],
    )
    content = response.choices[0].message.content
    if not content:
        raise ValueError("Qwen returned empty content")
    return content


def generate_shot_drafts(script_text: str) -> list[ShotDraft]:
    if not script_text or not script_text.strip():
        raise ValueError("script_text cannot be blank")

    raw_content = _call_qwen(script_text.strip())
    payload = json.loads(_clean_llm_json(raw_content))
    shots_data = payload.get("shots")
    if not isinstance(shots_data, list) or not shots_data:
        raise ValueError("Qwen response does not contain valid shots")

    try:
        return [ShotDraft.model_validate(item) for item in shots_data]
    except ValidationError as exc:
        raise ValueError(f"Invalid shot draft structure: {exc}") from exc


def _upsert_script_breakdown(db: Session, project_id: int, shots: Iterable[ShotDraft]) -> None:
    shots = list(shots)
    db.execute(delete(ShotDialogue).where(ShotDialogue.project_id == project_id))
    db.execute(delete(ShotPlan).where(ShotPlan.project_id == project_id))
    db.execute(delete(ScriptScene).where(ScriptScene.project_id == project_id))

    scene_map: dict[int, ScriptScene] = {}
    for shot in shots:
        scene = scene_map.get(shot.scene_index)
        if scene is None:
            scene = ScriptScene(
                project_id=project_id,
                scene_index=shot.scene_index,
                scene_text=shot.dialogue or shot.visual_prompt,
                mood=None,
                estimated_duration_sec=max(int(round(shot.duration_sec)), 1),
            )
            db.add(scene)
            db.flush()
            scene_map[shot.scene_index] = scene
        else:
            scene.estimated_duration_sec += max(int(round(shot.duration_sec)), 1)

        shot_record = ShotPlan(
            project_id=project_id,
            scene_id=scene.id,
            shot_index=shot.shot_index,
            duration_sec=shot.duration_sec,
            characters=shot.characters,
            camera_instruction=None,
            visual_prompt=shot.visual_prompt,
        )
        db.add(shot_record)
        db.flush()

        if shot.dialogue and shot.dialogue.strip():
            character_name = shot.characters[0] if shot.characters else "旁白"
            db.add(
                ShotDialogue(
                    project_id=project_id,
                    shot_id=shot_record.id,
                    character_name=character_name,
                    text=shot.dialogue.strip(),
                    sequence_no=1,
                )
            )


def run_script_parse(db: Session, project_id: int, script_text: str, task) -> list[dict]:
    project = db.get(Project, project_id)
    if project is None:
        raise ValueError(f"project {project_id} not found")

    try:
        mark_task_running(db, task)
        project.status = ProjectStatus.RUNNING
        shot_drafts = generate_shot_drafts(script_text)
        _upsert_script_breakdown(db, project_id, shot_drafts)
        mark_task_succeeded(db, task, f"script parsed successfully: {len(shot_drafts)} shots")
        project.status = ProjectStatus.RUNNING
        db.commit()
        return [shot.model_dump() for shot in shot_drafts]
    except Exception as exc:
        db.rollback()
        db.add(task)
        db.add(project)
        mark_task_failed(db, task, "SCRIPT_PARSE_FAILED", str(exc))
        project.status = ProjectStatus.FAILED
        db.commit()
        raise
