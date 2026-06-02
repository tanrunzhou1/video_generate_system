# UC005 查询项目详情 API

## 1. 基本信息

- 用例 ID：UC005
- 类型：HTTP API
- 方法/路径：`GET /api/v1/projects/{project_id}`
- 目标：返回项目基础信息、素材摘要、最近任务摘要和核心产物摘要，供详情页直接展示。

## 2. 请求定义

### Path

- `project_id`：项目 ID（必填，自增整数）

## 3. 响应定义

### 200

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "project_id": 1001,
    "name": "我的毕业设计短片",
    "description": "项目描述",
    "target_duration_sec": 60,
    "style_preset": "cinematic",
    "status": "running",
    "created_at": "2026-06-02T12:00:00Z",
    "updated_at": "2026-06-02T12:10:00Z",
    "asset_summary": {
      "script_file_count": 1,
      "persona_doc_count": 1,
      "character_image_count": 2,
      "style_reference_count": 1
    },
    "latest_task": {
      "task_id": 37,
      "stage": "script_parse",
      "status": "running",
      "retry_count": 0,
      "error_code": null,
      "error_message": null,
      "log_file_path": "logs/tasks/project_1001/task_37.log"
    },
    "final_video": null
  }
}
```

### 404

- 项目不存在

## 4. 数据读取

- 主表：`project`
- 关联表：`project_asset`
- 关联表：`render_task`（按最近一次任务返回摘要）
- 关联表：`final_video`（如存在则返回最新成片信息）

## 5. 业务规则

1. `asset_summary` 返回按素材类型聚合后的数量，不直接返回全部素材明细。
2. `latest_task` 仅返回最近一次任务的摘要，不返回完整日志正文。
3. `final_video` 在尚未出片时允许为 `null`。
4. 详情接口面向页面展示，优先返回高频信息，低频明细可后续拆分独立接口。

## 6. 与 PRD 对齐

- 对齐模块：2.1 项目管理模块（查询项目状态、查看任务日志与失败原因）
- 对齐模块：2.7 视频合成与导出模块（展示成片摘要）
- 对齐验收：用户可查看任务进展、中间输入摘要和失败定位信息。

## 7. Postman 测试步骤

### 前置条件

1. 服务已启动（`make dev`）。
2. 已通过 `UC002` 创建项目。
3. 如需观察素材摘要，建议先调用 `UC003` 上传素材。

### 请求配置

- Method: `GET`
- URL: `http://127.0.0.1:8000/api/v1/projects/{{project_id}}`

### 成功判定

1. HTTP 状态码为 `200`。
2. 返回体 `code=0`。
3. `data.project_id` 等于 `{{project_id}}`。
4. `data.asset_summary` 存在，且字段为整数。
5. 未接入实际任务执行时，`latest_task` 与 `final_video` 可为 `null`。
