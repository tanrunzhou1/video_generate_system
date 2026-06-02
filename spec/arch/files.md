# 文件结构说明（Files Spec）

## 1. 项目概览

- 服务名：`Video_generate_system_be`
- 识别框架：`FastAPI`、`LangGraph`、`SQLAlchemy`、`Alembic`
- 生成模式：Lite（允许 TODO/NEED_VERIFY，支持迭代）

## 2. 目录结构

- `app/`：应用源码目录
- `app/main.py`：FastAPI 入口
- `app/api/`：HTTP 路由层
- `app/core/`：配置与通用运行时能力
- `app/db/`：SQLAlchemy Base 与 ORM 模型
- `app/workflow/`：LangGraph 工作流骨架
- `alembic/`：数据库迁移脚本
- `docs/`：PRD 与设计文档
- `assets/`：输入素材目录（MVP 本地文件）
- `storage/`：运行时存储（SQLite、产物）
- `logs/`：日志目录
- `tests/`：测试目录（当前较少）

## 3. 模块职责

- API 模块（`app/api`）：当前仅提供健康检查接口；项目创建/上传/状态接口待实现。
- Workflow 模块（`app/workflow`）：当前包含 `parse_script` 初始节点，完整 DAG 待实现。
- DB 模块（`app/db`）：已包含与 PRD 对齐的核心实体与枚举。
- Settings 模块（`app/core/settings.py`）：负责加载 `.env` 并提供类型化配置。
- Migration 模块（`alembic`）：负责 schema 版本管理与升级。

## 4. 关键运行路径

- 数据库文件（默认）：`./storage/app.db`
- 素材目录：`./assets`
- 存储目录：`./storage`
- 日志目录：`./logs`
- 任务日志建议目录：`./logs/tasks/project_{project_id}/task_{task_id}.log`

## 5. 差距与待办

- TODO：增加 `app/services`、`app/repositories` 分层以支持项目生命周期 API。
- TODO：新增 `/api/v1/projects` 路由族。
- TODO：为 `render_task` 建立日志文件路径写入与查询能力，打通任务 ID 与日志关联。
- NEED_VERIFY：后续实体增多时，是否按领域拆分 `models.py`。
