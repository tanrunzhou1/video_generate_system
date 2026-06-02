# 用例总览（Usecases）

## 范围

本文档描述当前服务的外部入口与主要用例映射。

## 已识别入口

### UC001 - 健康检查

- 类型：HTTP GET
- 路径：`/health`
- 代码位置：`app/api/health.py`
- 目标：返回服务存活状态和基础运行环境标识。
- 当前状态：已实现

## 来自 PRD 的核心入口

### UC002 - 创建项目

- 类型：HTTP POST
- 路径：`/api/v1/projects`
- 目标：创建短片生成项目并写入元数据。
- 当前状态：已实现
- 详细文档：`spec/usecase/uc002_create_project.md`

### UC003 - 上传项目素材

- 类型：HTTP POST（multipart）
- 路径：`/api/v1/projects/{project_id}/assets`
- 目标：上传剧本、人设图、人设文档等输入素材。
- 当前状态：已实现
- 详细文档：`spec/usecase/uc003_upload_project_assets.md`

### UC004 - 查询项目状态

- 类型：HTTP GET
- 路径：`/api/v1/projects/{project_id}/status`
- 目标：返回项目生命周期状态与处理进度。
- 当前状态：已实现
- 详细文档：`spec/usecase/uc004_query_project_status.md`

### UC005 - 查询项目详情

- 类型：HTTP GET
- 路径：`/api/v1/projects/{project_id}`
- 目标：返回项目详情与关联产物摘要。
- 当前状态：已实现
- 详细文档：`spec/usecase/uc005_query_project_detail.md`

## 内部工作流入口

### UC006 - 工作流剧本解析

- 类型：内部工作流节点
- 节点：`parse_script`
- 代码位置：`app/workflow/graph.py`
- 目标：将原始剧本转换为可用于分镜的数据结构。
- 当前状态：IMPLEMENTED_MVP
- 详细文档：`spec/usecase/uc006_workflow_parse_script.md`

### UC007 - 任务日志关联

- 类型：内部任务生命周期能力 + 辅助 HTTP API
- 关联对象：`render_task.id`、`render_task.log_file_path`
- 目标：为每个任务生成稳定的任务 ID，并可通过任务记录定位本地日志文件。
- 当前状态：IMPLEMENTED_MVP
- 详细文档：`spec/usecase/uc007_task_log_linking.md`

### UC008 - 查询任务日志

- 类型：HTTP GET
- 路径：`/api/v1/tasks/{task_id}/logs`
- 目标：按任务 ID 返回任务基础信息与日志文本内容，支持前端直接查看任务执行过程。
- 当前状态：IMPLEMENTED_MVP
- 详细文档：`spec/usecase/uc008_get_task_logs.md`

## 说明

- PRD 已定义完整端到端能力，当前代码仍处于初始化阶段。
- 详细用例见 `spec/usecase/uc*_*.md`。
