# 前端设计文档（基于当前已实现后端）

## 1. 文档范围

本文档只覆盖当前后端已经实现的能力，目标是让前端可以直接进入开发，不提前设计还没有接口支撑的模块。

当前已纳入范围：

- 项目创建
- 项目素材上传
- 项目详情与状态查看
- 剧本解析触发
- 任务日志查看
- 角色档案创建、列表、详情
- 镜头视觉素材生成与查询

当前暂不纳入范围：

- 语音生成
- 字幕生成
- 背景音乐混合
- 最终视频合成与导出
- 角色编辑
- 批量视觉生成
- 视觉素材人工选中

## 2. 前端目标

当前前端 MVP 的主链路是：

1. 创建项目
2. 上传剧本与角色素材
3. 查看项目准备状态
4. 触发剧本解析
5. 创建角色档案
6. 为单个镜头生成视觉素材
7. 查看任务日志与结果

前端重点不是“功能看起来很多”，而是让用户能顺畅完成这条最小生产链路，并且在失败时能快速定位问题。

## 3. 技术建议

- 框架：React 18
- 工程框架：`@umijs/max`
- UI：Ant Design 5 + ProComponents
- 请求层：`umi-request` 或 `axios`
- 服务端状态管理：`@tanstack/react-query`
- 表单：Ant Design `Form`
- 上传：Ant Design `Upload`
- 代码高亮日志：`react-syntax-highlighter` 或原生 `pre/code`

## 4. 页面结构建议

建议采用以下页面路由：

1. `/projects/new`
- 项目创建页

2. `/projects/:projectId/setup`
- 项目准备页
- 上传剧本、人物图、人设文档、风格参考图

3. `/projects/:projectId`
- 项目工作台
- 查看项目详情、项目状态、最近任务
- 触发剧本解析

4. `/projects/:projectId/characters`
- 角色管理页
- 角色列表 + 创建角色

5. `/projects/:projectId/characters/:characterId`
- 角色详情页

6. `/projects/:projectId/shots/:shotId/visual-assets`
- 单镜头视觉素材页

7. `/tasks/:taskId/logs`
- 任务日志页

说明：

- 当前后端还没有“镜头列表接口”，所以前端先不要单独开发完整的镜头列表页。
- `shot_id` 当前主要来自剧本解析后的数据库结果，前端短期内可以通过后续补充接口或调试数据接入。

## 5. 通用接口约定

### 5.1 基础返回结构

除 `GET /health` 外，当前业务接口统一返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

前端判断建议：

- `HTTP 2xx` 且 `code === 0`：业务成功
- `HTTP 4xx/5xx`：业务失败
- 出现 `detail` 时，优先展示后端返回的 `detail`

### 5.2 错误处理建议

- `400`：参数错误、前置条件不满足
- `404`：项目、角色、任务、镜头、文件不存在
- `409`：命名冲突，例如项目重名、角色重名
- `500`：后端内部错误

### 5.3 前端基础 TypeScript 类型建议

```ts
export type ApiResponse<T> = {
  code: number;
  message: string;
  data: T;
};
```

## 6. 页面与接口映射

### 6.1 项目创建页 `/projects/new`

页面目标：

- 创建项目
- 创建成功后跳转到项目准备页

接口：

- `POST /api/v1/projects`

请求体：

```json
{
  "name": "校园短片A",
  "description": "第一版演示项目",
  "target_duration_sec": 60,
  "style_preset": "cinematic"
}
```

字段说明：

- `name`: 必填，项目名，不能与已有项目重名
- `description`: 选填，项目描述
- `target_duration_sec`: 必填，目标时长，范围 `10-600`
- `style_preset`: 选填，风格预设

成功返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "project_id": 1,
    "name": "校园短片A",
    "status": "created",
    "target_duration_sec": 60,
    "created_at": "2026-06-03T12:00:00"
  }
}
```

常见失败：

- `400 project name cannot be blank`
- `409 project name already exists`

前端交互建议：

- 项目名输入框要做必填校验
- 命中 `409` 时，直接在项目名输入框下方提示“项目名称已存在”
- 成功后跳转到 `/projects/{project_id}/setup`

### 6.2 项目准备页 `/projects/:projectId/setup`

页面目标：

- 上传剧本、人物设定图、人设文档、风格参考图
- 展示当前项目素材摘要

接口：

- `POST /api/v1/projects/{project_id}/assets`
- `GET /api/v1/projects/{project_id}`
- `GET /api/v1/projects/{project_id}/status`

#### 6.2.1 上传素材

接口：

- `POST /api/v1/projects/{project_id}/assets`

请求类型：

- `multipart/form-data`

表单字段：

- `script_file`: 必填，单文件
- `persona_doc`: 必填，单文件
- `character_images`: 必填，多文件
- `style_reference`: 选填，单文件

前端上传示例：

```ts
const formData = new FormData();
formData.append("script_file", scriptFile);
formData.append("persona_doc", personaDoc);
characterImages.forEach((file) => formData.append("character_images", file));
if (styleReference) {
  formData.append("style_reference", styleReference);
}
```

成功返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "project_id": 1,
    "uploaded": [
      {
        "asset_id": 1,
        "asset_type": "script_file",
        "file_path": "storage/projects/1/script_file/demo.md"
      },
      {
        "asset_id": 2,
        "asset_type": "persona_doc",
        "file_path": "storage/projects/1/persona_doc/persona.md"
      },
      {
        "asset_id": 3,
        "asset_type": "character_image",
        "file_path": "storage/projects/1/character_image/a.jpg"
      }
    ],
    "failed": []
  }
}
```

常见失败：

- `404 project not found`
- 文件缺失时，FastAPI 会直接返回 `422`

前端交互建议：

- 使用 `Upload` 组件分别维护：
  - 剧本文件
  - 人设文档
  - 角色参考图列表
  - 风格参考图
- 提交成功后刷新项目详情和状态
- `uploaded` 结果建议直接在页面显示，帮助用户确认哪些文件已经入库

#### 6.2.2 查询项目详情

接口：

- `GET /api/v1/projects/{project_id}`

成功返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "project_id": 1,
    "name": "校园短片A",
    "description": "第一版演示项目",
    "target_duration_sec": 60,
    "style_preset": "cinematic",
    "status": "created",
    "created_at": "2026-06-03T12:00:00",
    "updated_at": "2026-06-03T12:10:00",
    "asset_summary": {
      "script_file_count": 1,
      "persona_doc_count": 1,
      "character_image_count": 2,
      "style_reference_count": 1
    },
    "latest_task": null,
    "final_video": null
  }
}
```

字段说明：

- `asset_summary`: 当前最适合前端展示“准备度”的摘要信息
- `latest_task`: 最近一次任务摘要，可能为空
- `final_video`: 当前通常为空，因为后端还没有完成视频合成模块

`latest_task` 非空示例：

```json
{
  "task_id": 7,
  "stage": "script_parse",
  "status": "succeeded",
  "retry_count": 0,
  "error_code": null,
  "error_message": null,
  "log_file_path": "logs/tasks/project_1/task_7.log"
}
```

#### 6.2.3 查询项目状态

接口：

- `GET /api/v1/projects/{project_id}/status`

成功返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "project_id": 1,
    "status": "created",
    "current_stage": "script_parse",
    "progress": null,
    "retry_count": 0,
    "last_error_code": null,
    "last_error_message": null,
    "updated_at": "2026-06-03T12:10:00"
  }
}
```

前端交互建议：

- 项目准备页顶部可以放一个“准备状态卡片”
- 当 `script_file_count >= 1`、`persona_doc_count >= 1`、`character_image_count >= 1` 时，可以提示用户进入下一步

### 6.3 项目工作台 `/projects/:projectId`

页面目标：

- 查看项目基础信息
- 查看项目最新任务状态
- 手动触发剧本解析

接口：

- `GET /api/v1/projects/{project_id}`
- `GET /api/v1/projects/{project_id}/status`
- `POST /api/v1/projects/{project_id}/parse-script`

#### 6.3.1 触发剧本解析

接口：

- `POST /api/v1/projects/{project_id}/parse-script`

请求体：

- 无

成功返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "project_id": 1,
    "task_id": 7,
    "status": "succeeded",
    "workflow_status": "script_parsed",
    "shot_count": 6,
    "log_file_path": "logs/tasks/project_1/task_7.log"
  }
}
```

常见失败：

- `400 script_file asset not found`
- `404 script file not found`
- `400 script file is empty`
- `404 project not found`

前端交互建议：

- 触发按钮建议加 loading
- 成功后刷新：
  - 项目详情
  - 项目状态
- 页面上显示：
  - `task_id`
  - `workflow_status`
  - `shot_count`
- 若返回了 `task_id`，提供“查看任务日志”按钮，跳转 `/tasks/{taskId}/logs`

### 6.4 任务日志页 `/tasks/:taskId/logs`

页面目标：

- 查看任务执行日志
- 查看任务错误摘要

接口：

- `GET /api/v1/tasks/{task_id}/logs`

成功返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "task_id": 7,
    "project_id": 1,
    "stage": "script_parse",
    "status": "succeeded",
    "retry_count": 0,
    "error_code": null,
    "error_message": null,
    "log_file_path": "logs/tasks/project_1/task_7.log",
    "log_content": "[2026-06-03 12:20:00] task created\n[2026-06-03 12:20:03] task succeeded\n"
  }
}
```

常见失败：

- `404 task not found`
- `404 task log file path not found`
- `404 task log file not found`

前端交互建议：

- `log_content` 用等宽字体、滚动容器展示
- 页面头部同时展示：
  - `stage`
  - `status`
  - `retry_count`
  - `error_message`

### 6.5 角色管理页 `/projects/:projectId/characters`

页面目标：

- 查看角色列表
- 创建角色档案

接口：

- `GET /api/v1/projects/{project_id}/characters`
- `POST /api/v1/projects/{project_id}/characters`

#### 6.5.1 创建角色

请求体：

```json
{
  "name": "主角",
  "persona_text": "17岁女高中生，冷静，行动力强。",
  "voice_style": "young_female_calm",
  "reference_image_asset_ids": [3, 4],
  "prompt_constraints": {
    "positive": ["黑色短发", "校服", "干净构图"],
    "negative": ["多余手指", "面部崩坏"]
  },
  "seed_policy": {
    "mode": "fixed",
    "seed": 123456
  }
}
```

字段说明：

- `reference_image_asset_ids` 必须引用当前项目内已上传的 `character_image` 素材
- `prompt_constraints` 和 `seed_policy` 当前后端不做强结构校验，前端可以按 JSON 编辑器或结构化表单实现

成功返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "character_id": 1,
    "project_id": 1,
    "name": "主角",
    "voice_style": "young_female_calm",
    "reference_image_paths": [
      "storage/projects/1/character_image/a.jpg",
      "storage/projects/1/character_image/b.jpg"
    ],
    "created_at": "2026-06-03T13:00:00"
  }
}
```

常见失败：

- `404 project not found`
- `400 character name cannot be blank`
- `400 persona_text cannot be blank`
- `400 voice_style cannot be blank`
- `400 reference_image_asset_ids cannot be empty`
- `400 invalid character_image asset reference`
- `409 character name already exists in project`

前端交互建议：

- 角色创建表单建议拆成四块：
  - 基础信息
  - 参考图选择
  - 提示词约束
  - Seed 策略
- 参考图选择最好从项目已上传素材中选，不建议手填 asset id

#### 6.5.2 查询角色列表

成功返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "project_id": 1,
    "items": [
      {
        "character_id": 1,
        "name": "主角",
        "voice_style": "young_female_calm",
        "reference_image_count": 2,
        "created_at": "2026-06-03T13:00:00"
      }
    ]
  }
}
```

前端交互建议：

- 列表页展示：
  - 角色名
  - 音色风格
  - 参考图数量
  - 创建时间
- 点击行跳转到详情页

### 6.6 角色详情页 `/projects/:projectId/characters/:characterId`

页面目标：

- 展示单个角色完整信息

接口：

- `GET /api/v1/projects/{project_id}/characters/{character_id}`

成功返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "character_id": 1,
    "project_id": 1,
    "name": "主角",
    "persona_text": "17岁女高中生，冷静，行动力强。",
    "voice_style": "young_female_calm",
    "reference_image_paths": [
      "storage/projects/1/character_image/a.jpg",
      "storage/projects/1/character_image/b.jpg"
    ],
    "prompt_constraints": {
      "positive": ["黑色短发", "校服", "干净构图"],
      "negative": ["多余手指", "面部崩坏"]
    },
    "seed_policy": {
      "mode": "fixed",
      "seed": 123456
    }
  }
}
```

常见失败：

- `404 project not found`
- `404 character not found`

前端交互建议：

- `prompt_constraints` 与 `seed_policy` 适合用 JSON Viewer 展示
- `reference_image_paths` 当前是本地路径，前端暂时只能作为文本展示，等后端补静态资源访问后再接图片预览

### 6.7 镜头视觉素材页 `/projects/:projectId/shots/:shotId/visual-assets`

页面目标：

- 为单个镜头生成视觉素材
- 查看该镜头已生成的视觉素材列表

接口：

- `POST /api/v1/projects/{project_id}/shots/{shot_id}/visual-assets`
- `GET /api/v1/projects/{project_id}/shots/{shot_id}/visual-assets`

#### 6.7.1 生成视觉素材

请求体：

```json
{
  "provider": "qwen-image-2.0",
  "resolution": "720p",
  "override_prompt": "黄昏校园操场，电影感，主角站在跑道边，逆光。"
}
```

字段说明：

- `provider`: 当前建议固定传 `qwen-image-2.0`
- `resolution`: 选填，可选值：
  - `360p`
  - `480p`
  - `720p`
  - `1080p`
- `override_prompt`: 选填，用于手动覆盖镜头默认提示词

成功返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "asset_id": 11,
    "project_id": 1,
    "shot_id": 5,
    "asset_type": "image",
    "provider": "qwen-image-2.0",
    "resolution": "720p",
    "file_path": "storage/projects/1/visual/shot_5_asset_11.png",
    "prompt_used": "黄昏校园操场，电影感，主角站在跑道边，逆光。",
    "seed": 123456,
    "is_selected": false
  }
}
```

常见失败：

- `404 project not found`
- `404 shot not found`
- `400 unsupported provider`
- `400 unsupported resolution`
- `400 shot visual_prompt is empty`
- 其他 Qwen-Image 调用失败信息

前端交互建议：

- `provider` 在 MVP 阶段可以不做下拉，直接写死
- `resolution` 用单选按钮组或 Select
- `override_prompt` 用多行输入框
- 成功后立即刷新素材列表

#### 6.7.2 查询镜头视觉素材列表

成功返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "project_id": 1,
    "shot_id": 5,
    "items": [
      {
        "asset_id": 11,
        "project_id": 1,
        "shot_id": 5,
        "asset_type": "image",
        "provider": "qwen-image-2.0",
        "resolution": "720p",
        "file_path": "storage/projects/1/visual/shot_5_asset_11.png",
        "prompt_used": "黄昏校园操场，电影感，主角站在跑道边，逆光。",
        "seed": 123456,
        "is_selected": false
      }
    ]
  }
}
```

前端交互建议：

- 列表建议展示：
  - 缩略图占位
  - `provider`
  - `resolution`
  - `seed`
  - `prompt_used`
  - `file_path`
- 当前由于还没有图片静态访问接口，先把 `file_path` 和元信息展示出来即可

### 6.8 健康检查接口

接口：

- `GET /health`

成功返回：

```json
{
  "status": "ok",
  "env": "dev",
  "storage_dir": "storage"
}
```

用途：

- 前端本地联调时可用来判断服务是否启动成功
- 不建议作为业务页面主接口

## 7. 前端类型定义建议

建议在 `src/services/types.ts` 中定义以下核心类型。

### 7.1 ProjectDetail

```ts
export type ProjectDetail = {
  project_id: number;
  name: string;
  description: string | null;
  target_duration_sec: number;
  style_preset: string | null;
  status: "created" | "running" | "succeeded" | "failed";
  created_at: string;
  updated_at: string;
  asset_summary: {
    script_file_count: number;
    persona_doc_count: number;
    character_image_count: number;
    style_reference_count: number;
  };
  latest_task: {
    task_id: number;
    stage: string;
    status: string;
    retry_count: number;
    error_code: string | null;
    error_message: string | null;
    log_file_path: string | null;
  } | null;
  final_video: {
    video_id: number;
    resolution: string | null;
    duration_sec: number | null;
    file_path: string;
    cover_image_path: string | null;
    created_at: string;
  } | null;
};
```

### 7.2 ProjectStatus

```ts
export type ProjectStatus = {
  project_id: number;
  status: "created" | "running" | "succeeded" | "failed";
  current_stage: string | null;
  progress: number | null;
  retry_count: number;
  last_error_code: string | null;
  last_error_message: string | null;
  updated_at: string;
};
```

### 7.3 CharacterProfile

```ts
export type CharacterProfile = {
  character_id: number;
  project_id: number;
  name: string;
  persona_text: string;
  voice_style: string;
  reference_image_paths: string[];
  prompt_constraints: Record<string, unknown>;
  seed_policy: Record<string, unknown>;
};
```

### 7.4 VisualAsset

```ts
export type VisualAsset = {
  asset_id: number;
  project_id: number;
  shot_id: number;
  asset_type: string;
  provider: string;
  resolution: string;
  file_path: string;
  prompt_used: string;
  seed: number | null;
  is_selected: boolean;
};
```

### 7.5 TaskLog

```ts
export type TaskLog = {
  task_id: number;
  project_id: number;
  stage: string;
  status: string;
  retry_count: number;
  error_code: string | null;
  error_message: string | null;
  log_file_path: string;
  log_content: string;
};
```

## 8. 服务层组织建议

建议按资源维度拆分前端请求封装：

1. `src/services/project.ts`
- 创建项目
- 查询项目详情
- 查询项目状态
- 上传素材
- 触发剧本解析

2. `src/services/character.ts`
- 创建角色
- 查询角色列表
- 查询角色详情

3. `src/services/task.ts`
- 查询任务日志

4. `src/services/visual.ts`
- 生成视觉素材
- 查询视觉素材列表

## 9. React Query 建议

推荐 query key：

- `["project", projectId]`
- `["project-status", projectId]`
- `["characters", projectId]`
- `["character", projectId, characterId]`
- `["visual-assets", projectId, shotId]`
- `["task-log", taskId]`

推荐失效策略：

- 创建项目成功后：跳页，不需要失效
- 上传素材成功后：失效 `["project", projectId]` 和 `["project-status", projectId]`
- 触发剧本解析成功后：失效 `["project", projectId]` 和 `["project-status", projectId]`
- 创建角色成功后：失效 `["characters", projectId]`
- 生成视觉素材成功后：失效 `["visual-assets", projectId, shotId]`

## 10. 推荐组件拆分

页面级组件：

- `ProjectCreatePage`
- `ProjectSetupPage`
- `ProjectDashboardPage`
- `CharacterListPage`
- `CharacterDetailPage`
- `ShotVisualAssetPage`
- `TaskLogPage`

业务组件：

- `ProjectBasicForm`
- `ProjectAssetUploadPanel`
- `ProjectStatusCard`
- `LatestTaskCard`
- `CharacterFormDrawer`
- `CharacterConstraintEditor`
- `VisualGenerateForm`
- `VisualAssetGallery`
- `TaskLogViewer`

## 11. 当前已知限制

1. 后端还没有独立“镜头列表接口”
- 前端暂时不能完整做镜头管理页

2. 图片文件当前只保存为本地路径
- 还没有静态资源访问 URL
- 前端暂时无法稳定预览本地图片文件

3. 角色档案没有编辑接口
- 当前只能创建、列表、详情

4. 视觉素材目前只支持单镜头单次生成
- 还没有批量生成接口

5. `prompt_constraints` 和 `seed_policy` 目前是弱约束 JSON
- 前端可以先做宽松 JSON 结构

## 12. 推荐开发顺序

建议前端按下面顺序推进，这样每一步都能单独联调：

1. 项目创建页
2. 项目准备页
3. 项目工作台
4. 任务日志页
5. 角色管理页
6. 角色详情页
7. 单镜头视觉素材页

## 13. 后续扩展方向

等后端继续补接口后，前端可以自然扩展：

1. 镜头列表页
2. 分镜详情页
3. 角色编辑页
4. 视觉素材选中页
5. 语音字幕工作台
6. 最终视频预览与导出页
