# 数据库增量设计：project_asset

## 1. 设计背景

PRD 要求“上传输入素材（剧本、人设图、人设文档、可选风格参考）”，当前核心表未显式记录上传元数据，故新增 `project_asset` 表。

## 2. 表定义

- 表名：`project_asset`
- 主键：`id`（int，自增）
- 外键：`project_id -> project.id`

### 字段

- `id`：素材记录 ID
- `project_id`：所属项目 ID
- `asset_type`：素材类型（`script_file/persona_doc/character_image/style_reference`）
- `file_path`：存储路径
- `original_name`：原始文件名
- `mime_type`：MIME 类型
- `size_bytes`：文件大小（字节）
- `is_active`：是否当前生效版本（默认 true）
- `created_at`：上传时间

## 3. 约束与规则

1. `project_id` 必须存在。
2. `asset_type` 必须在白名单内。
3. 允许同 `project_id + asset_type` 多条记录，使用 `is_active` 标识当前版本。

## 4. 与现有表关系

- `project` 1:N `project_asset`
- 后续可由 workflow 消费 `project_asset` 推进分镜、视觉、语音阶段。
