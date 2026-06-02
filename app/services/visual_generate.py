import base64
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.db.models import AssetType, CharacterProfile, Project, RenderTask, ShotPlan, VisualAsset
from app.services.task_log import create_task_with_log, mark_task_failed, mark_task_running, mark_task_succeeded

settings = get_settings()

SUPPORTED_RESOLUTIONS = {"360p", "480p", "720p", "1080p"}
RESOLUTION_TO_SIZE = {
    "360p": "640*360",
    "480p": "854*480",
    "720p": "1280*720",
    "1080p": "1920*1080",
}
QWEN_IMAGE_PROVIDER = "qwen-image-2.0"
_MOCK_PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wn3Fo4AAAAASUVORK5CYII="
)


def _load_project_and_shot(db: Session, project_id: int, shot_id: int) -> tuple[Project, ShotPlan]:
    project = db.get(Project, project_id)
    if project is None:
        raise ValueError("project not found")

    shot = db.get(ShotPlan, shot_id)
    if shot is None or shot.project_id != project.id:
        raise ValueError("shot not found")

    return project, shot


def _normalize_resolution(resolution: str | None) -> str:
    normalized = (resolution or settings.default_image_resolution).strip()
    if normalized not in SUPPORTED_RESOLUTIONS:
        raise ValueError("unsupported resolution")
    return normalized


def _load_matching_characters(db: Session, project_id: int, character_names: list[str]) -> list[CharacterProfile]:
    normalized_names = [name.strip() for name in character_names if isinstance(name, str) and name.strip()]
    if not normalized_names:
        return []

    return (
        db.execute(
            select(CharacterProfile).where(
                CharacterProfile.project_id == project_id,
                CharacterProfile.name.in_(normalized_names),
            )
        )
        .scalars()
        .all()
    )


def _build_prompt_with_constraints(
    db: Session,
    project_id: int,
    shot: ShotPlan,
    override_prompt: str | None,
) -> tuple[str, int | None]:
    base_prompt = (override_prompt or shot.visual_prompt or "").strip()
    if not base_prompt:
        raise ValueError("shot visual prompt is empty")

    characters = _load_matching_characters(db, project_id, list(shot.characters or []))
    if not characters:
        return base_prompt, None

    parts = [base_prompt, "", "角色约束："]
    seed: int | None = None
    for character in characters:
        parts.append(f"- {character.name}：{character.persona_text}")
        positive = character.prompt_constraints.get("positive", [])
        negative = character.prompt_constraints.get("negative", [])
        if positive:
            parts.append(f"  正向约束：{'，'.join(str(item) for item in positive)}")
        if negative:
            parts.append(f"  负向约束：{'，'.join(str(item) for item in negative)}")
        if seed is None:
            seed_candidate = character.seed_policy.get("seed")
            if isinstance(seed_candidate, int):
                seed = seed_candidate

    return "\n".join(parts).strip(), seed


def _call_qwen_image(prompt: str, resolution: str, seed: int | None) -> bytes:
    if not settings.qwen_api_key:
        raise ValueError("QWEN_API_KEY is not configured")

    payload = {
        "model": settings.qwen_image_model,
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}],
                }
            ]
        },
        "parameters": {
            "size": RESOLUTION_TO_SIZE[resolution],
        },
    }
    if seed is not None:
        payload["parameters"]["seed"] = seed

    request = Request(
        settings.qwen_image_api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.qwen_api_key}",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=120) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise ValueError(f"Qwen-Image request failed: {exc.code} {body}") from exc
    except URLError as exc:
        raise ValueError(f"Qwen-Image request failed: {exc.reason}") from exc

    image_url = _extract_image_url(response_payload)
    if not image_url:
        raise ValueError("Qwen-Image response does not contain image url")
    return _download_binary(image_url)


def _extract_image_url(payload: dict) -> str | None:
    output = payload.get("output", {})
    if isinstance(output, dict):
        for key in ("url", "image_url", "image"):
            value = output.get(key)
            if isinstance(value, str) and value:
                return value

        for list_key in ("results", "images"):
            values = output.get(list_key)
            if not isinstance(values, list):
                continue
            for item in values:
                if not isinstance(item, dict):
                    continue
                for key in ("url", "image_url", "image"):
                    value = item.get(key)
                    if isinstance(value, str) and value:
                        return value
    return None


def _download_binary(url: str) -> bytes:
    try:
        with urlopen(url, timeout=120) as response:
            return response.read()
    except HTTPError as exc:
        raise ValueError(f"failed to download generated image: {exc.code}") from exc
    except URLError as exc:
        raise ValueError(f"failed to download generated image: {exc.reason}") from exc


def _save_image_bytes(project_id: int, shot_id: int, asset_id: int, content: bytes) -> str:
    base_dir = Path(settings.storage_dir) / "projects" / str(project_id) / "visual"
    base_dir.mkdir(parents=True, exist_ok=True)
    file_path = base_dir / f"shot_{shot_id}_asset_{asset_id}.png"
    file_path.write_bytes(content)
    return str(file_path)


def _generate_mock_image() -> bytes:
    return _MOCK_PNG_BYTES


def generate_visual_asset(
    db: Session,
    *,
    project_id: int,
    shot_id: int,
    provider: str,
    resolution: str | None,
    override_prompt: str | None,
) -> VisualAsset:
    normalized_provider = provider.strip()
    if normalized_provider not in {QWEN_IMAGE_PROVIDER, "mock-qwen-image-2.0"}:
        raise ValueError("unsupported provider")

    normalized_resolution = _normalize_resolution(resolution)
    _, shot = _load_project_and_shot(db, project_id, shot_id)
    prompt_used, seed = _build_prompt_with_constraints(db, project_id, shot, override_prompt)

    task: RenderTask | None = None
    try:
        task = create_task_with_log(db, project_id=project_id, stage="visual_generate")
        db.commit()
        db.refresh(task)

        mark_task_running(db, task)
        db.commit()

        if normalized_provider == QWEN_IMAGE_PROVIDER:
            image_bytes = _call_qwen_image(prompt_used, normalized_resolution, seed)
        else:
            image_bytes = _generate_mock_image()

        asset = VisualAsset(
            project_id=project_id,
            shot_id=shot.id,
            asset_type=AssetType.IMAGE,
            file_path="",
            provider=normalized_provider,
            resolution=normalized_resolution,
            prompt_used=prompt_used,
            seed=seed,
            consistency_score=None,
            is_selected=False,
        )
        db.add(asset)
        db.flush()
        asset.file_path = _save_image_bytes(project_id, shot.id, asset.id, image_bytes)
        db.flush()

        if task is not None:
            mark_task_succeeded(db, task, f"visual asset generated: asset_id={asset.id}")
        db.commit()
        db.refresh(asset)
        return asset
    except Exception as exc:
        db.rollback()
        if task is not None:
            db.add(task)
            mark_task_failed(db, task, "VISUAL_GENERATE_FAILED", str(exc))
            db.commit()
        raise
