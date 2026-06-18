# 用例总览（Usecases）

## 范围

本文档描述当前服务的外部入口与主要用例映射。

## 已识别入口

### UC001 - 健康检查

- 类型：HTTP GET
- 路径：`/health`
- 代码位置：`app/api/health.py`
- 目标：返回服务存活状态和基础运行环境标识。
- 当前状态：已实现

## 来自 PRD 的核心入口

### UC002 - 创建项目

- 类型：HTTP POST
- 路径：`/api/v1/projects`
- 目标：创建短片生成项目并写入元数据。
- 当前状态：已实现
- 详细文档：`spec/usecase/uc002_create_project.md`

### UC003 - 上传项目素材

- 类型：HTTP POST（multipart）
- 路径：`/api/v1/projects/{project_id}/assets`
- 目标：上传剧本、人设图、人设文档等输入素材。
- 当前状态：已实现
- 详细文档：`spec/usecase/uc003_upload_project_assets.md`

### UC004 - 查询项目状态

- 类型：HTTP GET
- 路径：`/api/v1/projects/{project_id}/status`
- 目标：返回项目生命周期状态与处理进度。
- 当前状态：已实现
- 详细文档：`spec/usecase/uc004_query_project_status.md`

### UC005 - 查询项目详情

- 类型：HTTP GET
- 路径：`/api/v1/projects/{project_id}`
- 目标：返回项目详情与关联产物摘要。
- 当前状态：已实现
- 详细文档：`spec/usecase/uc005_query_project_detail.md`

### UC014 - 分页查询项目列表

- 类型：HTTP GET
- 路径：`/api/v1/projects`
- 目标：分页返回已创建项目列表，默认按创建时间倒序展示。
- 当前状态：已实现
- 详细文档：`spec/usecase/uc014_list_projects.md`

## 内部工作流入口

### UC006 - 工作流剧本解析

- 类型：内部工作流节点
- 节点：`parse_script`
- 辅助触发接口：`POST /api/v1/projects/{project_id}/parse-script`
- 代码位置：`app/workflow/graph.py`
- 目标：将原始剧本转换为可用于分镜的数据结构。
- 当前状态：IMPLEMENTED_MVP
- 详细文档：`spec/usecase/uc006_workflow_parse_script.md`

### UC007 - 任务日志关联

- 类型：内部任务生命周期能力 + 辅助 HTTP API
- 关联对象：`render_task.id`、`render_task.log_file_path`
- 目标：为每个任务生成稳定的任务 ID，并可通过任务记录定位本地日志文件。
- 当前状态：IMPLEMENTED_MVP
- 详细文档：`spec/usecase/uc007_task_log_linking.md`

### UC008 - 查询任务日志

- 类型：HTTP GET
- 路径：`/api/v1/tasks/{task_id}/logs`
- 目标：按任务 ID 返回任务基础信息与日志文本内容，支持前端直接查看任务执行过程。
- 当前状态：IMPLEMENTED_MVP
- 详细文档：`spec/usecase/uc008_get_task_logs.md`

### UC009 - 创建角色档案

- 类型：HTTP POST
- 路径：`/api/v1/projects/{project_id}/characters`
- 目标：为项目创建角色档案，沉淀角色参考图、提示词约束与 seed 策略。
- 当前状态：已实现
- 详细文档：`spec/usecase/uc009_create_character_profile.md`

### UC010 - 查询角色列表

- 类型：HTTP GET
- 路径：`/api/v1/projects/{project_id}/characters`
- 目标：返回项目下全部角色档案摘要。
- 当前状态：已实现
- 详细文档：`spec/usecase/uc010_list_character_profiles.md`

### UC011 - 查询角色详情

- 类型：HTTP GET
- 路径：`/api/v1/projects/{project_id}/characters/{character_id}`
- 目标：返回单个角色档案完整详情，供后续视觉生成与人工校验使用。
- 当前状态：已实现
- 详细文档：`spec/usecase/uc011_get_character_profile_detail.md`

### UC012 - 生成视觉素材

- 类型：HTTP POST
- 路径：`/api/v1/projects/{project_id}/shots/{shot_id}/visual-assets`
- 目标：基于镜头分镜与角色约束，调用 `qwen-image-2.0` 生成 1 份图片素材并落库。
- 当前状态：已实现
- 详细文档：`spec/usecase/uc012_generate_visual_asset.md`

### UC013 - 查询镜头视觉素材列表

- 类型：HTTP GET
- 路径：`/api/v1/projects/{project_id}/shots/{shot_id}/visual-assets`
- 目标：按镜头返回已生成的图片素材列表。
- 当前状态：已实现
- 详细文档：`spec/usecase/uc013_list_visual_assets_by_shot.md`

### UC015 - 生成镜头配音素材

- 类型：HTTP POST
- 路径：`/api/v1/projects/{project_id}/shots/{shot_id}/voice-assets`
- 目标：基于镜头台词与角色音色配置生成多角色配音音频。
- 当前状态：SPEC_READY
- 详细文档：`spec/usecase/uc015_generate_voice_assets.md`

### UC016 - 查询镜头配音素材列表

- 类型：HTTP GET
- 路径：`/api/v1/projects/{project_id}/shots/{shot_id}/voice-assets`
- 目标：按镜头返回已生成配音素材列表。
- 当前状态：SPEC_READY
- 详细文档：`spec/usecase/uc016_list_voice_assets_by_shot.md`

### UC017 - 生成镜头字幕片段

- 类型：HTTP POST
- 路径：`/api/v1/projects/{project_id}/shots/{shot_id}/subtitle-segments`
- 目标：基于镜头配音素材生成字幕时间轴片段。
- 当前状态：SPEC_READY
- 详细文档：`spec/usecase/uc017_generate_subtitle_segments.md`

### UC018 - 查询镜头字幕片段列表

- 类型：HTTP GET
- 路径：`/api/v1/projects/{project_id}/shots/{shot_id}/subtitle-segments`
- 目标：按镜头返回已生成字幕片段列表。
- 当前状态：SPEC_READY
- 详细文档：`spec/usecase/uc018_list_subtitle_segments_by_shot.md`

### UC019 - 创建背景音乐素材

- 类型：HTTP POST
- 路径：`/api/v1/projects/{project_id}/bgm-assets`
- 目标：登记项目背景音乐素材，供后续镜头混音选择使用。
- 当前状态：SPEC_READY
- 详细文档：`spec/usecase/uc019_create_bgm_asset.md`

### UC020 - 查询项目背景音乐素材列表

- 类型：HTTP GET
- 路径：`/api/v1/projects/{project_id}/bgm-assets`
- 目标：返回项目下已登记的背景音乐素材列表。
- 当前状态：SPEC_READY
- 详细文档：`spec/usecase/uc020_list_bgm_assets.md`

### UC021 - 生成镜头混音结果

- 类型：HTTP POST
- 路径：`/api/v1/projects/{project_id}/shots/{shot_id}/audio-mix`
- 目标：基于镜头配音与背景音乐生成镜头级混音结果。
- 当前状态：SPEC_READY
- 详细文档：`spec/usecase/uc021_mix_shot_audio.md`

### UC022 - 导出项目成片

- 类型：HTTP POST
- 路径：`/api/v1/projects/{project_id}/final-videos`
- 目标：触发项目成片合成与导出任务。
- 当前状态：SPEC_READY
- 详细文档：`spec/usecase/uc022_export_final_video.md`

### UC023 - 查询项目成片列表

- 类型：HTTP GET
- 路径：`/api/v1/projects/{project_id}/final-videos`
- 目标：返回项目下已导出的成片列表。
- 当前状态：SPEC_READY
- 详细文档：`spec/usecase/uc023_list_final_videos.md`

### UC024 - 查询成片详情

- 类型：HTTP GET
- 路径：`/api/v1/projects/{project_id}/final-videos/{video_id}`
- 目标：返回单个成片的完整元数据。
- 当前状态：SPEC_READY
- 详细文档：`spec/usecase/uc024_get_final_video_detail.md`

### UC025 - 查询项目镜头列表

- 类型：HTTP GET
- 路径：`/api/v1/projects/{project_id}/shots`
- 目标：返回项目下全部镜头列表，作为视觉、语音、字幕、混音与导出的统一镜头入口。
- 当前状态：SPEC_READY
- 详细文档：`spec/usecase/uc025_list_shots_by_project.md`

## 说明

- PRD 已定义完整端到端能力，当前代码仍处于初始化阶段。
- 详细用例见 `spec/usecase/uc*_*.md`。
