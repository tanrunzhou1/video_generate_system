# 语音与字幕表说明

## 范围

本文档补充说明 2.5 语音与字幕模块在当前数据库中的核心表结构与使用语义。

## 1. voice_asset

- 主键：`id`（int，自增）
- 外键：
  - `project_id -> project.id`
  - `shot_id -> shot_plan.id`
  - `character_id -> character_profile.id`

字段说明：

- `line_text`：当前语音素材对应的台词文本
- `voice_provider`：TTS 提供方，例如 `xtts-v2`
- `audio_path`：生成音频文件路径
- `start_time_sec`：语音在镜头内开始时间
- `end_time_sec`：语音在镜头内结束时间

当前使用约定：

1. 每条镜头台词生成 1 条 `voice_asset` 记录。
2. `start_time_sec/end_time_sec` 作为字幕对齐的直接输入。
3. `character_id` 用于回溯角色音色与角色身份。

## 2. subtitle_segment

- 主键：`id`（int，自增）
- 外键：
  - `project_id -> project.id`
  - `shot_id -> shot_plan.id`

字段说明：

- `text`：字幕文本
- `start_time_sec`：字幕开始时间
- `end_time_sec`：字幕结束时间

当前使用约定：

1. MVP 阶段字幕片段由 `voice_asset` 派生生成。
2. 每条 `voice_asset` 默认映射为 1 条 `subtitle_segment`。
3. 当前只存结构化片段，不单独持久化 `.srt` 文件路径。

## 3. NEED_VERIFY

1. 若后续要支持项目级 `.srt` 文件导出，是否新增 `subtitle_file` 或 `final_video` 关联字段。
2. 若后续要支持句内断句字幕，是否需要在 `subtitle_segment` 中增加 `sequence_no` 或 `speaker_name`。
3. 若后续要支持多语言字幕，是否需要增加 `language_code` 字段。
