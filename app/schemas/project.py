from datetime import datetime

from pydantic import BaseModel, Field


class CreateProjectRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    target_duration_sec: int = Field(ge=10, le=600)
    style_preset: str | None = Field(default=None, max_length=128)


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "ok"
    data: dict


class ProjectCreatedData(BaseModel):
    project_id: int
    name: str
    status: str
    target_duration_sec: int
    created_at: datetime


class UploadedAssetItem(BaseModel):
    asset_id: int
    asset_type: str
    file_path: str


class UploadAssetsData(BaseModel):
    project_id: int
    uploaded: list[UploadedAssetItem]
    failed: list[dict]


class ProjectStatusData(BaseModel):
    project_id: int
    status: str
    current_stage: str | None
    progress: int | None
    retry_count: int
    last_error_code: str | None
    last_error_message: str | None
    updated_at: datetime


class CreateTaskRequest(BaseModel):
    stage: str = Field(min_length=1, max_length=128)


class TaskCreatedData(BaseModel):
    task_id: int
    project_id: int
    stage: str
    status: str
    log_file_path: str


class TaskLogData(BaseModel):
    task_id: int
    project_id: int
    stage: str
    status: str
    retry_count: int
    error_code: str | None
    error_message: str | None
    log_file_path: str
    log_content: str


class ParseScriptTriggeredData(BaseModel):
    project_id: int
    task_id: int
    status: str
    workflow_status: str
    shot_count: int
    log_file_path: str


class CreateCharacterProfileRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    persona_text: str = Field(min_length=1, max_length=5000)
    voice_style: str = Field(min_length=1, max_length=128)
    reference_image_asset_ids: list[int] = Field(min_length=1)
    prompt_constraints: dict = Field(default_factory=dict)
    seed_policy: dict = Field(default_factory=dict)


class CharacterProfileCreatedData(BaseModel):
    character_id: int
    project_id: int
    name: str
    voice_style: str
    reference_image_paths: list[str]
    created_at: datetime


class CharacterProfileListItem(BaseModel):
    character_id: int
    name: str
    voice_style: str
    reference_image_count: int
    created_at: datetime


class CharacterProfileListData(BaseModel):
    project_id: int
    items: list[CharacterProfileListItem]


class CharacterProfileDetailData(BaseModel):
    character_id: int
    project_id: int
    name: str
    persona_text: str
    voice_style: str
    reference_image_paths: list[str]
    prompt_constraints: dict
    seed_policy: dict


class CreateVisualAssetRequest(BaseModel):
    provider: str = Field(min_length=1, max_length=128)
    resolution: str | None = Field(default=None, max_length=32)
    override_prompt: str | None = Field(default=None, max_length=4000)


class VisualAssetData(BaseModel):
    asset_id: int
    project_id: int
    shot_id: int
    asset_type: str
    provider: str
    resolution: str
    file_path: str
    prompt_used: str
    seed: int | None
    is_selected: bool


class VisualAssetListData(BaseModel):
    project_id: int
    shot_id: int
    items: list[VisualAssetData]
