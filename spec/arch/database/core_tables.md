# 数据库表说明（Core Tables）

## 数据库信息

- 引擎：SQLite（MVP 默认）
- 连接：`sqlite:///./storage/app.db`
- 迁移工具：Alembic
- 当前版本：`455512264750`

## 表清单

### project
- 主键：`id`（int，自增）
- 字段：`name`、`description`、`target_duration_sec`、`style_preset`、`status`、`created_at`、`updated_at`

### character_profile
- 主键：`id`（int，自增）
- 外键：`project_id -> project.id`
- 字段：`name`、`persona_text`、`voice_style`、`reference_image_paths(JSON)`、`prompt_constraints(JSON)`、`seed_policy(JSON)`

### script_scene
- 主键：`id`（int，自增）
- 外键：`project_id -> project.id`
- 字段：`scene_index`、`scene_text`、`mood`、`estimated_duration_sec`

### shot_plan
- 主键：`id`（int，自增）
- 外键：`project_id -> project.id`、`scene_id -> script_scene.id`
- 字段：`shot_index`、`duration_sec`、`characters(JSON)`、`camera_instruction`、`visual_prompt`、`status`

### shot_dialogue
- 主键：`id`（int，自增）
- 外键：`project_id -> project.id`、`shot_id -> shot_plan.id`
- 字段：`character_name`、`text`、`sequence_no`

### visual_asset
- 主键：`id`（int，自增）
- 外键：`project_id -> project.id`、`shot_id -> shot_plan.id`
- 字段：`asset_type`、`file_path`、`provider`、`prompt_used`、`seed`、`consistency_score`、`is_selected`

### voice_asset
- 主键：`id`（int，自增）
- 外键：`project_id -> project.id`、`shot_id -> shot_plan.id`、`character_id -> character_profile.id`
- 字段：`line_text`、`voice_provider`、`audio_path`、`start_time_sec`、`end_time_sec`

### subtitle_segment
- 主键：`id`（int，自增）
- 外键：`project_id -> project.id`、`shot_id -> shot_plan.id`
- 字段：`text`、`start_time_sec`、`end_time_sec`

### bgm_asset
- 主键：`id`（int，自增）
- 外键：`project_id -> project.id`
- 字段：`file_path`、`mood_tag`、`start_time_sec`、`end_time_sec`、`gain_db`

### audio_mix_asset
- 主键：`id`（int，自增）
- 外键：`project_id -> project.id`、`shot_id -> shot_plan.id`、`bgm_asset_id -> bgm_asset.id`
- 字段：`mixed_audio_path`、`ducking_gain_db`、`fade_in_sec`、`fade_out_sec`、`is_selected`、`created_at`

### render_task
- 主键：`id`（int，自增）
- 外键：`project_id -> project.id`
- 字段：`stage`、`status`、`retry_count`、`error_code`、`error_message`、`log_file_path`、`started_at`、`finished_at`
- 说明：`render_task.id` 即任务 ID（task_id），MVP 阶段用于与本地日志文件建立一对一关联

### final_video
- 主键：`id`（int，自增）
- 外键：`project_id -> project.id`
- 字段：`resolution`、`duration_sec`、`file_path`、`cover_image_path`、`created_at`

## 备注

- 枚举值通过 ORM 定义，并已体现在迁移脚本中。
- NEED_VERIFY：若切换到 MySQL/PostgreSQL，需复核 JSON/枚举字段的方言兼容性。
