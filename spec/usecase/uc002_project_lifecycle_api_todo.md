# UC002 项目生命周期 API（待实现）

## 1. 基本信息

- 用例 ID：UC002
- 用例名称：项目生命周期接口
- 类型：HTTP API
- 状态：TODO

## 2. 规划接口

- `POST /api/v1/projects`：创建项目
- `POST /api/v1/projects/{project_id}/assets`：上传素材
- `GET /api/v1/projects/{project_id}`：查询详情
- `GET /api/v1/projects/{project_id}/status`：查询状态

## 3. 数据依赖

- 表：`project`
- 表：`character_profile`
- 表：`script_scene`
- 表：`shot_plan`
- 表：`render_task`
- NEED_VERIFY：是否新增 `project_asset` 表用于上传元数据归一化。

## 4. 对应 PRD 验收

- 用户在 1 分钟内完成创建与素材上传（前后端联动目标）
- 状态可查询，失败原因明确

## 5. 建议实现切片

1. 先补 Pydantic 请求/响应模型。
2. 增加 SQLAlchemy Session 管理与 repository 层。
3. MVP 先交付创建项目 + 状态查询。
4. 再补 multipart 上传与素材元数据持久化。
