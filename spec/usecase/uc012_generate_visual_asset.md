# UC012 生成视觉素材 API

## 1. 基本信息

- 用例 ID：UC012
- 类型：HTTP API
- 方法/路径：`POST /api/v1/projects/{project_id}/shots/{shot_id}/visual-assets`
- 目标：基于镜头分镜与角色约束，调用 `qwen-image-2.0` 为指定镜头生成 1 份图片素材并落库。

## 2. 请求定义

### Path

- `project_id`：项目 ID（必填，自增整数）
- `shot_id`：镜头 ID（必填，自增整数）

### Body

```json
{
  "provider": "qwen-image-2.0",
  "resolution": "720p",
  "override_prompt": null
}
```

### 字段说明

- `provider`：视觉生成提供方，MVP 固定为 `qwen-image-2.0`
- `resolution`：图片分辨率档位，支持 `360p`、`480p`、`720p`、`1080p`
- `override_prompt`：可选人工覆盖提示词；为空时默认使用 `shot_plan.visual_prompt` 并拼装角色约束

## 3. 响应定义

### 200

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "asset_id": 15,
    "project_id": 12,
    "shot_id": 33,
    "asset_type": "image",
    "provider": "qwen-image-2.0",
    "resolution": "720p",
    "file_path": "storage/projects/12/visual/shot_33_asset_15.png",
    "prompt_used": "夜景街道，主角独自行走。角色约束：黑色短发，校服，电影感光影。",
    "seed": 123456,
    "is_selected": false
  }
}
```

### 400

- `provider` 为空或不是 `qwen-image-2.0`
- `resolution` 不在支持范围内
- 镜头未配置可用提示词

### 404

- 项目不存在
- 镜头不存在
- 镜头不属于当前项目

## 4. 数据读写

### 读取

- `shot_plan`：读取镜头角色、画面提示词
- `character_profile`：按角色名称读取提示词约束和 seed 策略

### 写入

- 主表：`visual_asset`
- 关键字段：
  - `project_id`
  - `shot_id`
  - `asset_type=image`
  - `file_path`
  - `provider=qwen-image-2.0`
  - `prompt_used`
  - `seed`
  - `is_selected`

## 5. 业务规则

1. 仅允许为当前项目下的镜头生成图片素材。
2. 基础提示词默认来自 `shot_plan.visual_prompt`。
3. 若镜头角色可匹配到 `character_profile.name`，应附加角色人设、正向约束和负向约束。
4. 若提供 `override_prompt`，优先使用覆盖提示词，再附加角色约束。
5. MVP 阶段每次请求只生成 1 张图，不做 Top-K、多候选和失败重试。
6. 生成成功后必须落库 `visual_asset`，并保存 `file_path`、`prompt_used`、`seed` 和分辨率信息。
7. 若项目未单独配置图片尺寸，则使用系统默认尺寸映射。

## 6. 分辨率约定

MVP 阶段对外暴露分辨率档位，不直接暴露底层宽高：

- `360p`
- `480p`
- `720p`
- `1080p`

实现层可将档位映射为 `qwen-image-2.0` 所需的具体尺寸参数。

## 7. 与 PRD 对齐

- 对齐模块：2.4 视觉生成模块
- 对齐功能点：
  - 基于分镜与角色约束生成视觉素材
  - 接入 `qwen-image-2.0`
  - 保存生成结果（路径、提示词、分辨率、生成参数）

## 8. Postman 测试步骤

### 前置条件

1. 已创建项目
2. 已上传剧本与角色图素材
3. 已完成 `UC006` 剧本解析，得到 `shot_id`
4. 已完成 `UC009` 角色档案创建

### 请求配置

- Method: `POST`
- URL: `http://127.0.0.1:8000/api/v1/projects/{{project_id}}/shots/{{shot_id}}/visual-assets`
- Header: `Content-Type: application/json`

### 请求体示例

```json
{
  "provider": "qwen-image-2.0",
  "resolution": "720p"
}
```

### 成功判定

1. HTTP 状态码为 `200`
2. 返回体 `code=0`
3. `data.asset_id` 为整数
4. `data.file_path` 非空
5. `data.prompt_used` 非空
6. `data.resolution` 等于请求值

## 9. 后续演进

1. 支持项目级默认分辨率配置
2. 支持按项目批量生成全部镜头素材
3. 增加人工选中素材接口
