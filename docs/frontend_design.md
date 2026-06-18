# 前端设计文档（基于当前已实现后端 + 已确认 Spec）

## 1. 文档范围

本文档分两层描述前端设计：

1. 已实现后端能力
- 前端现在就可以直接联调

2. 已确认 Spec 但后端待实现能力
- 前端可以先完成页面信息架构、类型定义、交互设计与接口封装草稿
- 等后端实现后直接联调

当前已纳入范围：

- 项目创建
- 项目列表分页查询
- 项目素材上传
- 项目详情与状态查看
- 剧本解析触发
- 镜头列表查询（已确认 Spec）
- 任务日志查看
- 角色档案创建、列表、详情
- 镜头视觉素材生成与查询
- 镜头语音生成与查询（已确认 Spec）
- 镜头字幕生成与查询（已确认 Spec）
- 项目 BGM 登记与查询（已确认 Spec）
- 镜头音频混音（已确认 Spec）
- 项目成片导出、列表与详情（已确认 Spec）

当前暂不纳入范围：

- 角色编辑
- 批量视觉生成
- 视觉素材人工选中
- 项目级自动工作流编排页

## 2. 前端目标

当前前端 MVP 的主链路是：

1. 分页查看项目列表 / 创建项目
2. 上传剧本与角色素材
3. 查看项目准备状态
4. 触发剧本解析
5. 查询镜头列表
6. 创建角色档案
7. 为单个镜头生成视觉素材
8. 为单个镜头生成语音与字幕
9. 为单个镜头选择 BGM 并混音
10. 触发项目成片导出
11. 查看任务日志、成片列表与成片详情

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

1. `/projects`
- 项目列表页
- 分页查看历史项目

2. `/projects/new`
- 项目创建页

3. `/projects/:projectId/setup`
- 项目准备页
- 上传剧本、人物图、人设文档、风格参考图

4. `/projects/:projectId`
- 项目工作台
- 查看项目详情、项目状态、最近任务
- 触发剧本解析

5. `/projects/:projectId/shots`
- 镜头列表页
- 统一进入视觉、语音、字幕、混音页面

6. `/projects/:projectId/characters`
- 角色管理页
- 角色列表 + 创建角色

7. `/projects/:projectId/characters/:characterId`
- 角色详情页

8. `/projects/:projectId/shots/:shotId/visual-assets`
- 单镜头视觉素材页

9. `/projects/:projectId/shots/:shotId/voice-assets`
- 单镜头语音素材页

10. `/projects/:projectId/shots/:shotId/subtitle-segments`
- 单镜头字幕页

11. `/projects/:projectId/shots/:shotId/audio-mix`
- 单镜头混音页

12. `/projects/:projectId/bgm-assets`
- 项目背景音乐管理页

13. `/projects/:projectId/final-videos`
- 项目成片列表页

14. `/projects/:projectId/final-videos/:videoId`
- 成片详情页

15. `/tasks/:taskId/logs`
- 任务日志页

说明：

- `UC025` 已定义项目镜头列表接口，前端应按该接口设计镜头工作台。
- 语音、字幕、BGM、混音、成片导出目前是 `SPEC_READY`，建议先完成页面骨架与类型定义。

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

### 6.1 项目列表页 `/projects`

页面目标：

- 分页查看已创建项目
- 进入项目详情或准备页
- 提供“创建项目”入口

接口：

- `GET /api/v1/projects?page=1&page_size=10`

请求参数：

- `page`：页码，默认 `1`
- `page_size`：每页条数，默认 `10`

成功返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "page": 1,
    "page_size": 10,
    "total": 23,
    "items": [
      {
        "project_id": 12,
        "name": "校园短片A",
        "description": "第一版演示项目",
        "target_duration_sec": 60,
        "style_preset": "cinematic",
        "status": "created",
        "created_at": "2026-06-18T18:00:00+08:00",
        "updated_at": "2026-06-18T18:05:00+08:00"
      }
    ]
  }
}
```

前端交互建议：

- 使用表格或卡片列表展示：
  - 项目名称
  - 项目状态
  - 目标时长
  - 风格
  - 创建时间
  - 更新时间
- 点击列表项进入 `/projects/:projectId`
- 右上角提供“新建项目”按钮

### 6.2 项目创建页 `/projects/new`

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

### 6.3 项目准备页 `/projects/:projectId/setup`

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

### 6.4 项目工作台 `/projects/:projectId`

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

### 6.5 任务日志页 `/tasks/:taskId/logs`

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

### 6.6 角色管理页 `/projects/:projectId/characters`

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

### 6.7 角色详情页 `/projects/:projectId/characters/:characterId`

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

### 6.8 镜头列表页 `/projects/:projectId/shots`

页面目标：

- 展示项目下全部镜头
- 作为视觉、语音、字幕、混音、导出的统一入口页

接口：

- `GET /api/v1/projects/{project_id}/shots`

成功返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "project_id": 12,
    "items": [
      {
        "shot_id": 33,
        "scene_id": 7,
        "scene_index": 1,
        "shot_index": 1,
        "duration_sec": 5.0,
        "characters": ["主角"],
        "camera_instruction": "中景，跟拍",
        "visual_prompt": "夜景街道，主角独自行走",
        "status": "planned",
        "dialogue_count": 2
      }
    ]
  }
}
```

前端交互建议：

- 使用时间线或分组表格展示：
  - `scene_index`
  - `shot_index`
  - `duration_sec`
  - `characters`
  - `status`
  - `dialogue_count`
- 每条镜头提供操作入口：
  - 生成视觉
  - 生成语音
  - 生成字幕
  - 混音
- `dialogue_count === 0` 时，禁用语音生成按钮并提示“当前镜头无台词”

### 6.9 镜头视觉素材页 `/projects/:projectId/shots/:shotId/visual-assets`

页面目标：

- 为单个镜头生成视觉素材
- 查看该镜头已生成的视觉素材列表

接口：

- `POST /api/v1/projects/{project_id}/shots/{shot_id}/visual-assets`
- `GET /api/v1/projects/{project_id}/shots/{shot_id}/visual-assets`

#### 6.9.1 生成视觉素材

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

#### 6.9.2 查询镜头视觉素材列表

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

### 6.10 镜头语音素材页 `/projects/:projectId/shots/:shotId/voice-assets`

页面目标：

- 基于已落库的 `shot_dialogue` 生成镜头语音
- 查看当前镜头已生成的语音素材列表

接口：

- `POST /api/v1/projects/{project_id}/shots/{shot_id}/voice-assets`
- `GET /api/v1/projects/{project_id}/shots/{shot_id}/voice-assets`

#### 6.10.1 生成镜头语音

请求体：

```json
{
  "provider": "xtts-v2",
  "source": "shot_dialogues"
}
```

说明：

- 前端不再手工录入台词
- 台词来源来自 `UC006` 落库后的 `shot_dialogue`

成功返回重点字段：

- `provider`
- `source`
- `items[].dialogue_id`
- `items[].character_id`
- `items[].line_text`
- `items[].audio_path`
- `items[].start_time_sec`
- `items[].end_time_sec`

前端交互建议：

- 页面顶部先展示镜头台词摘要
- 角色档案未准备完整时，禁用语音生成并提示“角色名尚未映射到角色档案”
- 生成成功后刷新语音列表

#### 6.10.2 查询镜头语音列表

列表建议展示：

- `character_id`
- `line_text`
- `voice_provider`
- `start_time_sec`
- `end_time_sec`
- `audio_path`

说明：

- 当前还没有稳定的音频访问 URL，可先展示路径和时间轴

### 6.11 镜头字幕页 `/projects/:projectId/shots/:shotId/subtitle-segments`

页面目标：

- 基于镜头语音结果生成字幕片段
- 查看字幕时间轴

接口：

- `POST /api/v1/projects/{project_id}/shots/{shot_id}/subtitle-segments`
- `GET /api/v1/projects/{project_id}/shots/{shot_id}/subtitle-segments`

#### 6.11.1 生成字幕

请求体：

```json
{
  "source": "voice_assets"
}
```

前端交互建议：

- 只有当语音列表非空时才允许点击“生成字幕”
- 生成成功后刷新字幕列表

#### 6.11.2 查询字幕列表

列表建议展示：

- `text`
- `start_time_sec`
- `end_time_sec`

说明：

- 当前返回结构化字幕片段，不直接返回 `.srt` 文本

### 6.12 项目背景音乐管理页 `/projects/:projectId/bgm-assets`

页面目标：

- 登记项目背景音乐素材
- 查看项目已登记的 BGM 列表

接口：

- `POST /api/v1/projects/{project_id}/bgm-assets`
- `GET /api/v1/projects/{project_id}/bgm-assets`

#### 6.12.1 创建 BGM 记录

请求体：

```json
{
  "file_path": "storage/projects/12/bgm/calm_theme.mp3",
  "mood_tag": "calm",
  "start_time_sec": 0.0,
  "end_time_sec": 18.0,
  "gain_db": -6.0
}
```

前端交互建议：

- MVP 阶段先做“登记路径”表单，不做文件上传组件耦合
- 表单建议字段：
  - 文件路径
  - 情绪标签
  - 开始时间
  - 结束时间
  - 默认增益

#### 6.12.2 查询 BGM 列表

列表建议展示：

- `mood_tag`
- `start_time_sec`
- `end_time_sec`
- `gain_db`
- `file_path`

### 6.13 镜头混音页 `/projects/:projectId/shots/:shotId/audio-mix`

页面目标：

- 选择 BGM 为单镜头生成混音结果
- 查看混音输出路径和版本信息

接口：

- `POST /api/v1/projects/{project_id}/shots/{shot_id}/audio-mix`

请求体：

```json
{
  "bgm_asset_id": 9,
  "ducking_gain_db": -10.0,
  "fade_in_sec": 0.3,
  "fade_out_sec": 0.5
}
```

前端交互建议：

- 从项目 BGM 列表中选择 `bgm_asset_id`
- 默认值建议：
  - `ducking_gain_db = -10`
  - `fade_in_sec = 0.3`
  - `fade_out_sec = 0.5`
- 混音成功后展示：
  - `mixed_audio_path`
  - `voice_asset_ids`
  - 本次混音参数

### 6.14 成片导出与结果页

#### 6.14.1 导出项目成片 `/projects/:projectId/final-videos`

接口：

- `POST /api/v1/projects/{project_id}/final-videos`
- `GET /api/v1/projects/{project_id}/final-videos`

导出请求体：

```json
{
  "resolution": "720p",
  "include_subtitles": true,
  "transition_mode": "none"
}
```

前端交互建议：

- 页面入口可以放在项目工作台，也可以放在单独“导出成片”Tab
- 表单先暴露最小字段：
  - 分辨率
  - 是否叠加字幕
- 提交成功后跳转任务日志页，或停留当前页轮询项目详情/成片列表

#### 6.14.2 查询项目成片列表 `/projects/:projectId/final-videos`

列表建议展示：

- `video_id`
- `resolution`
- `duration_sec`
- `created_at`
- `file_path`
- `cover_image_path`

#### 6.14.3 查询成片详情 `/projects/:projectId/final-videos/:videoId`

详情页建议展示：

- 成片基础信息
- 封面图路径
- 视频路径
- 导出时间

说明：

- 当前仍返回本地文件路径，不直接返回可播放 URL
- 前端详情页先按“结果元数据页”设计，不强依赖原生播放器

### 6.15 健康检查接口

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

### 7.3 ProjectListItem

```ts
export type ProjectListItem = {
  project_id: number;
  name: string;
  description: string | null;
  target_duration_sec: number;
  style_preset: string | null;
  status: "created" | "running" | "succeeded" | "failed";
  created_at: string;
  updated_at: string;
};
```

### 7.4 ShotListItem

```ts
export type ShotListItem = {
  shot_id: number;
  scene_id: number;
  scene_index: number;
  shot_index: number;
  duration_sec: number;
  characters: string[];
  camera_instruction: string | null;
  visual_prompt: string;
  status: string;
  dialogue_count: number;
};
```

### 7.5 CharacterProfile

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

### 7.6 VisualAsset

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

### 7.7 VoiceAsset

```ts
export type VoiceAsset = {
  voice_asset_id: number;
  character_id: number;
  dialogue_id?: number;
  line_text: string;
  voice_provider: string;
  audio_path: string;
  start_time_sec: number;
  end_time_sec: number;
};
```

### 7.8 SubtitleSegment

```ts
export type SubtitleSegment = {
  subtitle_segment_id: number;
  text: string;
  start_time_sec: number;
  end_time_sec: number;
};
```

### 7.9 BgmAsset

```ts
export type BgmAsset = {
  bgm_asset_id: number;
  file_path: string;
  mood_tag: string | null;
  start_time_sec: number;
  end_time_sec: number;
  gain_db: number;
};
```

### 7.10 AudioMixResult

```ts
export type AudioMixResult = {
  project_id: number;
  shot_id: number;
  bgm_asset_id: number;
  voice_asset_ids: number[];
  mixed_audio_path: string;
  ducking_gain_db: number;
  fade_in_sec: number;
  fade_out_sec: number;
};
```

### 7.11 FinalVideo

```ts
export type FinalVideo = {
  video_id: number;
  project_id?: number;
  resolution: string;
  duration_sec: number;
  file_path: string;
  cover_image_path: string | null;
  created_at: string;
};
```

### 7.12 TaskLog

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
- 查询项目列表
- 创建项目
- 查询项目详情
- 查询项目状态
- 上传素材
- 触发剧本解析
- 查询镜头列表
- 触发成片导出
- 查询成片列表
- 查询成片详情

2. `src/services/character.ts`
- 创建角色
- 查询角色列表
- 查询角色详情

3. `src/services/task.ts`
- 查询任务日志

4. `src/services/visual.ts`
- 生成视觉素材
- 查询视觉素材列表

5. `src/services/voice.ts`
- 生成镜头语音
- 查询镜头语音列表
- 生成字幕
- 查询字幕列表

6. `src/services/audio.ts`
- 创建 BGM 记录
- 查询 BGM 列表
- 生成镜头混音

## 9. React Query 建议

推荐 query key：

- `["projects", page, pageSize]`
- `["project", projectId]`
- `["project-status", projectId]`
- `["shots", projectId]`
- `["characters", projectId]`
- `["character", projectId, characterId]`
- `["visual-assets", projectId, shotId]`
- `["voice-assets", projectId, shotId]`
- `["subtitle-segments", projectId, shotId]`
- `["bgm-assets", projectId]`
- `["audio-mix", projectId, shotId]`
- `["final-videos", projectId]`
- `["final-video", projectId, videoId]`
- `["task-log", taskId]`

推荐失效策略：

- 创建项目成功后：跳页，不需要失效
- 上传素材成功后：失效 `["project", projectId]` 和 `["project-status", projectId]`
- 触发剧本解析成功后：失效 `["project", projectId]` 和 `["project-status", projectId]`
- 触发剧本解析成功后：额外失效 `["shots", projectId]`
- 创建角色成功后：失效 `["characters", projectId]`
- 生成视觉素材成功后：失效 `["visual-assets", projectId, shotId]`
- 生成语音成功后：失效 `["voice-assets", projectId, shotId]`
- 生成字幕成功后：失效 `["subtitle-segments", projectId, shotId]`
- 创建 BGM 成功后：失效 `["bgm-assets", projectId]`
- 混音成功后：视 UI 结构失效 `["audio-mix", projectId, shotId]` 或刷新当前页数据
- 触发成片导出成功后：失效 `["project", projectId]`，并在导出完成后刷新 `["final-videos", projectId]`

## 10. 推荐组件拆分

页面级组件：

- `ProjectListPage`
- `ProjectCreatePage`
- `ProjectSetupPage`
- `ProjectDashboardPage`
- `ShotListPage`
- `CharacterListPage`
- `CharacterDetailPage`
- `ShotVisualAssetPage`
- `ShotVoiceAssetPage`
- `ShotSubtitlePage`
- `ProjectBgmAssetPage`
- `ShotAudioMixPage`
- `FinalVideoListPage`
- `FinalVideoDetailPage`
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
- `ShotDialoguePreview`
- `VoiceAssetList`
- `SubtitleSegmentList`
- `BgmAssetForm`
- `BgmAssetTable`
- `AudioMixForm`
- `FinalVideoExportForm`
- `FinalVideoTable`
- `TaskLogViewer`

## 11. 当前已知限制

1. `UC025` 镜头列表目前已完成 Spec，但后端实现可能尚未落地
- 前端可以先完成镜头页结构和类型定义

2. 图片文件当前只保存为本地路径
- 还没有静态资源访问 URL
- 前端暂时无法稳定预览本地图片文件

3. 角色档案没有编辑接口
- 当前只能创建、列表、详情

4. 视觉素材目前只支持单镜头单次生成
- 还没有批量生成接口

5. 语音、字幕、BGM、混音、成片导出目前多数仍处于 `SPEC_READY`
- 前端可以先按接口契约开发页面骨架和 service 层
- 联调前需要再次确认真实实现状态

6. `prompt_constraints` 和 `seed_policy` 目前是弱约束 JSON
- 前端可以先做宽松 JSON 结构

7. 音频、视频、图片当前大多返回本地文件路径
- 还没有统一的静态资源访问方案
- 页面设计上先按“元数据展示优先”处理

## 12. 推荐开发顺序

建议前端按下面顺序推进，这样每一步都能单独联调：

1. 项目列表页
2. 项目创建页
3. 项目准备页
4. 项目工作台
5. 镜头列表页
6. 角色管理页
7. 角色详情页
8. 单镜头视觉素材页
9. 单镜头语音与字幕页
10. 项目 BGM 管理页
11. 单镜头混音页
12. 成片导出与结果页
13. 任务日志页

## 13. 后续扩展方向

等后端继续补接口后，前端可以自然扩展：

1. 分镜详情编辑页
2. 角色编辑页
3. 视觉素材选中页
4. 混音版本选择页
5. 最终视频预览与播放页
6. 项目级自动工作流看板
