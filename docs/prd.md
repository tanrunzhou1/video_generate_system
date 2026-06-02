# PRD：剧本驱动的多模态短片生成系统

## 1. 项目简介与技术栈

### 1.1 项目简介

本项目旨在构建一个“剧本驱动的多模态短片生成系统”。用户输入剧本、人物设定图与人物设定文档后，系统自动完成分镜拆解、画面生成、角色配音、字幕对齐、背景音乐匹配与视频合成，最终输出 1 分钟短片。

项目定位为课程/毕业设计可落地系统，强调：

- 端到端流程可运行
- 生成链路可追踪、可重试
- 中间产物可人工编辑
- 结果可用于演示与答辩

### 1.2 技术栈（建议）

- 架构策略：Workflow 主干（80%）+ Agent 增强（20%）
- 后端框架：FastAPI
- 工作流编排：LangGraph（后续可升级 Temporal）
- 异步任务：Celery + Redis（可选）
- 文本/规划模型：Qwen
- 图像生成：SDXL
- 语音合成：XTTS
- 检索与一致性：CLIP + FAISS
- 媒体处理：FFmpeg
- 前端框架：React 18
- 工程框架：@umijs/max（Umi/Max）
- UI 体系：Ant Design 5 + @ant-design/pro-components
- 媒体播放：原生 `<video>`（MVP），可选 video.js
- 数据请求与状态：umi-request + @tanstack/react-query
- 存储：本地文件系统（MVP），后续可扩展对象存储

### 1.3 Python 工程约定（使用 uv）

- Python 环境管理：使用 `uv`（不使用 `venv/conda/poetry`）
- 依赖管理：使用 `uv add` / `uv remove`
- 锁定文件：提交 `uv.lock`，保障团队与部署环境一致
- 启动方式：使用 `uv run` 执行后端与脚本命令

**推荐初始化命令（示例）**：

```bash
uv init
uv python install 3.12
uv venv --python 3.12
source .venv/bin/activate
uv add fastapi uvicorn langgraph pydantic python-multipart
```

---

## 2. 功能需求（按模块拆解）

### 2.1 项目管理模块

**目标**：管理一次短片生成任务的全生命周期。

**功能点**：

- 创建项目（名称、描述、风格、目标时长）
- 上传输入素材（剧本、人设图、人设文档、可选风格参考）
- 查询项目状态（待处理/处理中/完成/失败）
- 查看任务日志与失败原因

**验收标准**：

- 用户可在 1 分钟内完成任务创建与素材上传
- 任务状态可实时更新，失败时返回明确错误信息

### 2.2 剧本解析与分镜规划模块

**目标**：将剧本转化为可执行的镜头序列。

**功能点**：

- 场景切分（Scene）
- 镜头拆解（Shot）
- 台词归属（角色-台词映射）
- 每个镜头生成提示词草案（画面、角色、情绪、机位）

**验收标准**：

- 输出结构化分镜（JSON）
- 每个镜头包含：时长、角色、画面描述、台词片段

### 2.3 角色一致性与素材检索模块

**目标**：保证角色在跨镜头生成时外观一致。

**功能点**：

- 建立角色资产库（参考图、关键词、禁用词、seed）
- CLIP 特征提取与相似度校验
- 风格约束模板注入（prompt 模板）
- 失败镜头一致性检测与重试

**验收标准**：

- 同一角色跨镜头相似性分数达到设定阈值（可配置）

### 2.4 视觉生成模块

**目标**：基于分镜结果与角色约束生成可用的视觉素材。

**功能点**：

- 基于分镜与角色约束生成视觉素材
- 接入 `qwen-image-2.0` 生成图片素材
- 保存生成结果（图片路径、使用的提示词、分辨率、生成参数）
- 支持手动指定常见分辨率：`360p`、`480p`、`720p`、`1080p`
- 支持按镜头查看已生成素材

**验收标准**：

- 每个镜头可生成至少 1 份可用图片素材
- 可按镜头查询已生成结果及对应提示词、分辨率和文件路径

### 2.5 语音与字幕模块

**目标**：完成多角色配音与字幕时间轴。

**功能点**：

- 角色音色映射与多角色 TTS
- 台词音频合成（按镜头/按句）
- 字幕文件（SRT）生成
- 音频-字幕时间对齐

**验收标准**：

- 字幕与语音时间偏差在可接受范围（如 <300ms）

### 2.6 音乐与音频混合模块

**目标**：提升成片表现力与听感完整度。

**功能点**：

- 按情绪/节奏选择背景音乐
- 自动裁剪与淡入淡出
- 配音与 BGM 音量平衡（ducking）

**验收标准**：

- 无明显爆音/削波，台词清晰可辨

### 2.7 视频合成与导出模块

**目标**：将全量素材合成为可播放短片。

**功能点**：

- 镜头拼接、转场（可选）
- 配音轨道合入
- 字幕叠加
- 多规格导出（如 720p/1080p）

**验收标准**：

- 可稳定导出 MP4，时长与目标时长偏差可控

### 2.8 工作流调度与监控模块

**目标**：保障流程可执行、可恢复、可追踪。

**功能点**：

- 阶段编排（workflow DAG）
- 阶段级重试/超时/回退
- 任务日志、耗时统计、错误追踪

**验收标准**：

- 任一阶段失败不导致系统崩溃，可重试或回退

---

## 3. Data Model Definition（数据模型建议）

以下为建议的核心实体与字段（可用关系型数据库 + 对象存储实现）。

### 3.1 Project

- `id` (string)
- `name` (string)
- `description` (string)
- `target_duration_sec` (int)
- `style_preset` (string, optional)
- `status` (enum: created/running/succeeded/failed)
- `created_at` / `updated_at` (datetime)

### 3.2 CharacterProfile

- `id` (string)
- `project_id` (string)
- `name` (string)
- `persona_text` (text)
- `voice_style` (string)
- `reference_image_paths` (array<string>)
- `prompt_constraints` (json)
- `seed_policy` (json)

### 3.3 ScriptScene

- `id` (string)
- `project_id` (string)
- `scene_index` (int)
- `scene_text` (text)
- `mood` (string)
- `estimated_duration_sec` (int)

### 3.4 ShotPlan

- `id` (string)
- `project_id` (string)
- `scene_id` (string)
- `shot_index` (int)
- `duration_sec` (float)
- `characters` (array<string>)
- `camera_instruction` (string)
- `visual_prompt` (text)
- `status` (enum: planned/generated/selected/failed)

### 3.5 VisualAsset

- `id` (string)
- `project_id` (string)
- `shot_id` (string)
- `asset_type` (enum: image/video)
- `file_path` (string)
- `provider` (string)
- `prompt_used` (text)
- `seed` (int)
- `consistency_score` (float)
- `is_selected` (bool)

### 3.6 VoiceAsset

- `id` (string)
- `project_id` (string)
- `shot_id` (string)
- `character_id` (string)
- `line_text` (text)
- `voice_provider` (string)
- `audio_path` (string)
- `start_time_sec` (float)
- `end_time_sec` (float)

### 3.7 SubtitleSegment

- `id` (string)
- `project_id` (string)
- `shot_id` (string)
- `text` (text)
- `start_time_sec` (float)
- `end_time_sec` (float)

### 3.8 BgmAsset

- `id` (string)
- `project_id` (string)
- `file_path` (string)
- `mood_tag` (string)
- `start_time_sec` (float)
- `end_time_sec` (float)
- `gain_db` (float)

### 3.9 RenderTask

- `id` (string)
- `project_id` (string)
- `stage` (enum)
- `status` (enum: pending/running/succeeded/failed)
- `retry_count` (int)
- `error_code` (string, optional)
- `error_message` (text, optional)
- `started_at` / `finished_at` (datetime)

### 3.10 FinalVideo

- `id` (string)
- `project_id` (string)
- `resolution` (string)
- `duration_sec` (float)
- `file_path` (string)
- `cover_image_path` (string)
- `created_at` (datetime)

---

## 4. 分步开发指令

### 第 0 步：项目初始化

1. 使用 `uv` 初始化后端工程与虚拟环境（FastAPI）
2. 初始化工作流骨架（LangGraph）
3. 建立 `docs/`、`assets/`、`storage/`、`logs/` 目录
4. 配置 `.env`（模型 API Key、路径、默认参数）
5. 安装基础依赖并生成/提交 `uv.lock`

### 第 1 步：数据层与项目管理

1. 建立核心数据表/模型（Project、CharacterProfile、ShotPlan 等）
2. 实现项目创建、素材上传、状态查询 API
3. 打通任务 ID 与日志关联

### 第 2 步：剧本解析与分镜模块

1. 接入 LLM，完成剧本切 scene 与 shot
2. 输出结构化 `ShotPlan`
3. 增加人工编辑接口（可改 shot 文本与时长）

### 第 3 步：角色一致性与视觉生成模块

1. 接入图像生成模型（SDXL/FLUX）
2. 实现角色约束 prompt 模板
3. 实现每镜头 Top-K 候选生成
4. 接入 CLIP 相似度打分并支持自动重试

### 第 4 步：语音与字幕模块

1. 接入 TTS，完成多角色配音
2. 生成 SRT 字幕
3. 完成语音与字幕时间轴对齐

### 第 5 步：BGM 与合成导出模块

1. 接入 BGM 选择策略（标签/情绪）
2. 使用 FFmpeg 完成音视频合成
3. 导出标准 MP4，生成封面图

### 第 6 步：工作流编排与容错

1. 将各模块串成完整 workflow
2. 增加阶段级超时、重试、回退
3. 完成任务级状态流转与错误码定义

### 第 7 步：最小可用前端（可选）

1. 实现创建任务页
2. 实现中间结果预览与编辑
3. 实现成片播放与下载
4. 基于 ProComponents 实现任务列表、详情页与状态轮询

### 第 8 步：测试与答辩准备

1. 准备 3 套测试剧本（短/中/复杂）
2. 统计指标：成功率、平均耗时、角色一致性评分
3. 固化一条稳定演示链路（Demo Script）
4. 输出答辩材料：架构图、流程图、指标表

---

## 附：MVP 验收标准（建议）

- 输入完整素材后可在可接受时间内自动生成短片
- 至少一条端到端流程稳定跑通（含失败重试）
- 中间结果可查看、可局部修正
- 最终输出含画面、配音、字幕、BGM 四要素
- 有量化指标可展示（成功率、耗时、质量评分）
