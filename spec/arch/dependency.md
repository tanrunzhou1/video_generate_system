# 依赖说明（Dependency Spec）

## 1. 已识别运行时依赖

### 框架与核心

- `fastapi`
- `uvicorn`
- `pydantic`
- `pydantic-settings`

### 工作流与模型编排

- `langgraph`
- `langchain`
- `openai`

### 数据与基础设施

- `sqlalchemy`
- `alembic`
- `redis`
- `celery`

### 媒体与 AI 支撑

- `opencv-python`
- `pillow`
- `numpy`
- `faiss-cpu`

## 2. 规划中的外部依赖

- Qwen API（已配置，尚未接入 workflow 业务节点）
- OpenAI-compatible API（已配置，尚未接入 workflow 业务节点）
- FFmpeg 可执行文件（用于音视频合成）

## 3. 当前耦合关系

- API 层依赖 settings 加载。
- 迁移运行时依赖 settings + ORM metadata。
- 当前 workflow 为骨架实现，无外部副作用。

## 4. TODO / NEED_VERIFY

- TODO：定义模型服务适配器边界（`llm_client`、`tts_client`、`vision_client`）。
- NEED_VERIFY：确认 Celery/Redis 在 MVP 阶段是强依赖还是可选开关。
