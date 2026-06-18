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


class ProjectListItem(BaseModel):
    project_id: int
    name: str
    description: str | None
    target_duration_sec: int
    style_preset: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class ProjectListData(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[ProjectListItem]


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


class ShotListItem(BaseModel):
    shot_id: int
    scene_id: int
    scene_index: int
    shot_index: int
    duration_sec: float
    characters: list[str]
    camera_instruction: str | None
    visual_prompt: str
    status: str
    dialogue_count: int


class ShotListData(BaseModel):
    project_id: int
    items: list[ShotListItem]


class CreateVoiceAssetsRequest(BaseModel):
    provider: str = Field(min_length=1, max_length=128)
    source: str = Field(min_length=1, max_length=64)


class VoiceAssetItem(BaseModel):
    voice_asset_id: int
    character_id: int
    dialogue_id: int
    line_text: str
    voice_provider: str
    audio_path: str
    start_time_sec: float
    end_time_sec: float


class VoiceAssetListData(BaseModel):
    project_id: int
    shot_id: int
    provider: str | None = None
    source: str | None = None
    items: list[VoiceAssetItem]


class CreateSubtitleSegmentsRequest(BaseModel):
    source: str = Field(min_length=1, max_length=64)


class SubtitleSegmentItem(BaseModel):
    subtitle_segment_id: int
    text: str
    start_time_sec: float
    end_time_sec: float


class SubtitleSegmentListData(BaseModel):
    project_id: int
    shot_id: int
    source: str | None = None
    items: list[SubtitleSegmentItem]


class CreateBgmAssetRequest(BaseModel):
    file_path: str = Field(min_length=1, max_length=512)
    mood_tag: str | None = Field(default=None, max_length=64)
    start_time_sec: float = Field(ge=0)
    end_time_sec: float = Field(gt=0)
    gain_db: float = 0.0


class BgmAssetItem(BaseModel):
    bgm_asset_id: int
    file_path: str
    mood_tag: str | None
    start_time_sec: float
    end_time_sec: float
    gain_db: float


class BgmAssetListData(BaseModel):
    project_id: int
    items: list[BgmAssetItem]


class CreateAudioMixRequest(BaseModel):
    bgm_asset_id: int
    ducking_gain_db: float = 0.0
    fade_in_sec: float = Field(default=0.0, ge=0)
    fade_out_sec: float = Field(default=0.0, ge=0)


class AudioMixData(BaseModel):
    audio_mix_asset_id: int
    project_id: int
    shot_id: int
    bgm_asset_id: int
    voice_asset_ids: list[int]
    mixed_audio_path: str
    ducking_gain_db: float
    fade_in_sec: float
    fade_out_sec: float
    is_selected: bool
    created_at: datetime


class CreateFinalVideoRequest(BaseModel):
    resolution: str = Field(min_length=1, max_length=32)
    include_subtitles: bool = True
    transition_mode: str = Field(default="none", min_length=1, max_length=32)


class FinalVideoExportData(BaseModel):
    project_id: int
    task_id: int
    status: str
    resolution: str
    include_subtitles: bool
    transition_mode: str
    log_file_path: str
    video_id: int
    file_path: str


class FinalVideoItem(BaseModel):
    video_id: int
    resolution: str
    duration_sec: float
    file_path: str
    cover_image_path: str | None
    created_at: datetime


class FinalVideoListData(BaseModel):
    project_id: int
    items: list[FinalVideoItem]


class FinalVideoDetailData(BaseModel):
    video_id: int
    project_id: int
    resolution: str
    duration_sec: float
    file_path: str
    cover_image_path: str | None
    created_at: datetime
