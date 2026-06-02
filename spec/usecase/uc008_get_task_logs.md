# UC008 查询任务日志 API

## 1. 基本信息

- 用例 ID：UC008
- 类型：HTTP API
- 方法/路径：`GET /api/v1/tasks/{task_id}/logs`
- 目标：根据任务 ID 返回任务摘要和日志文本内容，供前端查看执行过程与失败原因。

## 2. 请求定义

### Path

- `task_id`：任务 ID（必填，自增整数）

## 3. 响应定义

### 200

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "task_id": 37,
    "project_id": 12,
    "stage": "script_parse",
    "status": "failed",
    "retry_count": 1,
    "error_code": "SCRIPT_PARSE_FAILED",
    "error_message": "Qwen response does not contain valid shots",
    "log_file_path": "logs/tasks/project_12/task_37.log",
    "log_content": "[2026-06-02T08:00:00] task created: stage=script_parse, status=pending\n[2026-06-02T08:00:02] task running\n[2026-06-02T08:00:05] task failed: error_code=SCRIPT_PARSE_FAILED, error_message=Qwen response does not contain valid shots\n"
  }
}
```

### 404

- 任务不存在
- 任务存在但日志文件不存在

## 4. 数据读取

- 主表：`render_task`
- 依赖字段：`id`、`project_id`、`stage`、`status`、`retry_count`、`error_code`、`error_message`、`log_file_path`
- 外部资源：本地日志文件（`log_file_path`）

## 5. 业务规则

1. 接口通过 `task_id` 精确查询单个任务，不使用 query 参数做筛选。
2. 若数据库中存在任务但 `log_file_path` 为空，应返回可识别错误信息。
3. 若日志文件不存在，应返回 `404`，避免前端误以为任务无日志。
4. 日志内容按原始文本返回，不在 MVP 阶段做高亮、分页或结构化切分。
5. `log_content` 仅用于查看，不提供日志文件修改能力。

## 6. 与 UC007 的关系

- `UC007` 负责创建任务 ID 与日志路径的关联
- `UC008` 负责读取该关联结果并返回日志内容
- 两者共同构成“任务可追踪、失败可定位”的最小闭环

## 7. 与 PRD 对齐

- 对齐模块：2.1 项目管理模块（查看任务日志与失败原因）
- 对齐模块：2.8 工作流调度与监控模块（任务日志、错误追踪）
- 对齐验收：失败时可返回明确错误信息，并查看对应任务日志

## 8. Postman 测试步骤

### 前置条件

1. 服务已启动（`make dev`）
2. 已通过 `POST /api/v1/projects/{project_id}/tasks` 创建过任务
3. 已拿到有效 `task_id`

### 请求配置

- Method: `GET`
- URL: `http://127.0.0.1:8000/api/v1/tasks/{{task_id}}/logs`

### 成功判定

1. HTTP 状态码为 `200`
2. 返回体 `code=0`
3. `data.task_id` 等于 `{{task_id}}`
4. `data.log_file_path` 非空
5. `data.log_content` 非空，且至少包含一条任务创建日志

### 异常判定

- `task_id` 不存在：返回 `404`
- 日志文件缺失：返回 `404`

## 9. 后续演进

1. 支持日志分页读取或按行数截断
2. 支持返回结构化日志事件数组
3. 支持下载原始日志文件
