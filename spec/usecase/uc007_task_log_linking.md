# UC007 任务日志关联（MVP）

## 1. 基本信息

- 用例 ID：UC007
- 类型：内部任务生命周期能力
- 目标：打通任务 ID 与日志文件的关联，支持根据任务记录快速定位日志与错误原因。
- 实现策略：轻量方案

## 2. MVP 设计范围

1. 日志正文仍写本地文件，不做数据库全文存储。
2. 数据库仅保存任务元信息与日志文件路径。
3. 使用 `render_task.id` 作为唯一任务 ID（task_id）。
4. 提供最小辅助接口 `POST /api/v1/projects/{project_id}/tasks` 用于创建任务记录并初始化日志链路。

## 3. 数据模型约定

基于现有 `render_task` 表扩展以下语义：

- `id`：任务 ID（task_id）
- `project_id`：所属项目 ID
- `stage`：当前任务阶段，如 `script_parse`、`visual_generate`
- `status`：任务状态，取值 `pending/running/succeeded/failed`
- `retry_count`：阶段重试次数
- `error_code`：最近一次失败错误码
- `error_message`：最近一次失败错误摘要
- `log_file_path`：本地日志文件路径
- `started_at` / `finished_at`：任务开始与结束时间

## 4. 日志路径规范

- 根目录：`LOGS_DIR/tasks/`
- 建议格式：`logs/tasks/project_{project_id}/task_{task_id}.log`
- 示例：`logs/tasks/project_12/task_37.log`

## 5. 任务与日志关联流程

1. 创建任务记录时，数据库生成 `render_task.id`。
2. 系统根据 `project_id` 和 `task_id` 生成日志文件路径。
3. 任务执行过程中的结构化文本日志写入该文件。
4. 如任务失败，数据库同步更新 `status`、`error_code`、`error_message`。
5. 后续通过任务 ID 或项目维度可反查日志文件位置。

## 6. 查询与使用方式

MVP 阶段至少支持以下两类使用场景：

1. 通过项目状态页展示最近任务的 `task_id`、`status`、`error_message`
2. 通过任务记录中的 `log_file_path` 打开或下载日志文件

## 6.1 辅助接口定义

- Method/Path：`POST /api/v1/projects/{project_id}/tasks`
- 目标：创建任务记录、生成 `task_id`、写入 `log_file_path`、初始化首条日志

### 请求体

```json
{
  "stage": "script_parse"
}
```

### 响应体

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "task_id": 37,
    "project_id": 12,
    "stage": "script_parse",
    "status": "pending",
    "log_file_path": "logs/tasks/project_12/task_37.log"
  }
}
```

## 7. 验收标准

1. 每个任务均有唯一 `task_id`
2. 每个任务均可定位到唯一日志文件路径
3. 任务失败时，数据库中可看到失败摘要，日志文件中可看到详细过程
4. 项目维度可追踪最近一次任务和对应日志
5. 创建任务后，本地应立即生成日志文件并写入首条创建日志

## 8. 非目标

1. 不做日志全文检索
2. 不做集中式日志平台接入
3. 不做日志切分、归档、告警系统

## 9. 后续演进

1. `GET /api/v1/tasks/{task_id}/logs` 已拆分为独立用例 `UC008`
2. 可接入结构化日志或外部日志平台
3. 可增加任务事件表，用于记录关键节点时间线

## 10. 当前实现状态

1. 已实现 `render_task.log_file_path`
2. 已实现任务日志路径生成与本地文件写盘
3. 已实现 `POST /api/v1/projects/{project_id}/tasks` 最小任务创建接口
4. 已由项目状态接口与项目详情接口返回最近任务摘要中的 `task_id` 和 `log_file_path`
