# UC004 查询项目状态 API

## 1. 基本信息

- 用例 ID：UC004
- 类型：HTTP API
- 方法/路径：`GET /api/v1/projects/{project_id}/status`
- 目标：返回项目当前状态、阶段与错误信息摘要。

## 2. 请求定义

### Path

- `project_id`：项目 ID（必填）

## 3. 响应定义

### 200

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "project_id": 1001,
    "status": "running",
    "current_stage": "script_parse",
    "progress": 35,
    "retry_count": 1,
    "last_error_code": null,
    "last_error_message": null,
    "updated_at": "2026-05-29T12:30:00Z"
  }
}
```

### 404

- 项目不存在

## 4. 数据读取

- 主表：`project`
- 辅助表：`render_task`（取最近任务阶段、重试次数、错误信息）

## 5. 业务规则

1. `status` 取值：`created/running/succeeded/failed`。
2. `current_stage`、`progress` 在工作流未接入时允许为默认值或 `null`。
3. 若最近任务失败，返回最近 `error_code/error_message`。

## 6. 与 PRD 对齐

- 对齐模块：2.1 项目管理模块（查询项目状态、失败原因）
- 对齐验收：状态可实时查询，失败信息明确。

## 7. Postman 测试步骤

### 前置条件

1. 服务已启动（`make dev`）。
2. 已有有效 `project_id`（可通过 `UC002` 创建获得）。

### 请求配置

- Method: `GET`
- URL: `http://127.0.0.1:8000/api/v1/projects/{{project_id}}/status`

### 成功判定

1. HTTP 状态码为 `200`。
2. 返回体 `code=0`。
3. `data.project_id` 等于 `{{project_id}}`，且为整数。
4. `data.status` 在 `created/running/succeeded/failed` 集合内。
5. 当前工作流未接入时，`current_stage` 与 `progress` 可为 `null`（属预期）。

### 异常判定

- 当 `project_id` 不存在时，返回 `404`。
