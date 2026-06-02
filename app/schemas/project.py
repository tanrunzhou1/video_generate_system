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
