# 配置说明（Config Spec）

## 1. 配置来源

- 主配置文件：`.env`
- 类型化加载：`app/core/settings.py`（`pydantic-settings`）

## 2. 配置项

### 运行时

- `APP_NAME`（默认：`Video Generate System BE`）
- `APP_ENV`（默认：`dev`）
- `APP_HOST`（默认：`0.0.0.0`）
- `APP_PORT`（默认：`8000`）
- `LOG_LEVEL`（默认：`INFO`）

### 模型服务

- `QWEN_API_KEY`
- `QWEN_BASE_URL`
- `QWEN_MODEL`
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`

### 媒体工具

- `FFMPEG_BIN`（默认：`ffmpeg`）

### 存储路径

- `ASSETS_DIR`（默认：`./assets`）
- `STORAGE_DIR`（默认：`./storage`）
- `LOGS_DIR`（默认：`./logs`）

### 工作流默认参数

- `TARGET_DURATION_SEC`（默认：`60`）
- `MAX_RETRY_PER_STAGE`（默认：`2`）
- `WORKFLOW_TIMEOUT_SEC`（默认：`1800`）
- `TOP_K_CANDIDATES`（默认：`3`）
- `CONSISTENCY_THRESHOLD`（默认：`0.78`）

### 基础设施

- `REDIS_URL`（默认：`redis://localhost:6379/0`）
- `DATABASE_URL`（默认：`sqlite:///./storage/app.db`）

## 3. 当前使用状态

- 已使用：
  - `APP_NAME`：用于 FastAPI 应用初始化
  - `APP_ENV`、`STORAGE_DIR`：用于 `/health` 返回
  - `DATABASE_URL`：用于 Alembic 迁移连接
- TODO：
  - 将工作流超时/重试/Top-K 配置接入执行节点
  - 将模型服务配置接入 LLM/TTS/视觉生成适配器
