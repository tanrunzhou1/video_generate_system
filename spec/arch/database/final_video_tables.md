# 成片导出表说明

## 范围

本文档补充说明 2.7 视频合成与导出模块在当前数据库中的核心表结构与使用语义。

## 1. final_video

- 主键：`id`（int，自增）
- 外键：
  - `project_id -> project.id`

字段说明：

- `resolution`：导出分辨率，例如 `720p`、`1080p`
- `duration_sec`：导出成片时长
- `file_path`：成片文件路径
- `cover_image_path`：封面图路径
- `created_at`：成片生成时间

当前使用约定：

1. 每次导出成功后新增 1 条 `final_video` 记录。
2. 一个项目允许存在多个成片版本，例如不同分辨率或重复导出。
3. 当前阶段 `final_video` 只保存结果元数据，不单独回存完整导出参数。

## 2. NEED_VERIFY

1. 是否为 `final_video` 增加 `task_id` 字段，便于回溯导出任务与日志。
2. 是否增加 `include_subtitles`、`transition_mode` 等导出参数字段。
3. 若后续接入对象存储，`file_path` / `cover_image_path` 是否改为 URL 字段。
