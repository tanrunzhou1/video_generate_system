# UC013 查询镜头视觉素材列表 API

## 1. 基本信息

- 用例 ID：UC013
- 类型：HTTP API
- 方法/路径：`GET /api/v1/projects/{project_id}/shots/{shot_id}/visual-assets`
- 目标：按镜头返回已生成的图片素材列表，供前端查看生成结果。

## 2. 请求定义

### Path

- `project_id`：项目 ID（必填，自增整数）
- `shot_id`：镜头 ID（必填，自增整数）

## 3. 响应定义

### 200

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "project_id": 12,
    "shot_id": 33,
    "items": [
      {
        "asset_id": 15,
        "asset_type": "image",
        "provider": "qwen-image-2.0",
        "resolution": "720p",
        "file_path": "storage/projects/12/visual/shot_33_asset_15.png",
        "prompt_used": "夜景街道，主角独自行走。角色约束：黑色短发，校服，电影感光影。",
        "seed": 123456,
        "is_selected": false
      }
    ]
  }
}
```

### 404

- 项目不存在
- 镜头不存在
- 镜头不属于当前项目

## 4. 数据读取

- 主表：`visual_asset`
- 依赖表：`shot_plan`
- 读取字段：
  - `id`
  - `asset_type`
  - `provider`
  - `file_path`
  - `prompt_used`
  - `seed`
  - `is_selected`

## 5. 业务规则

1. 仅返回当前项目、当前镜头下已生成的视觉素材。
2. 默认按生成顺序返回。
3. MVP 阶段不做分页。
4. 若镜头尚未生成素材，返回空数组，不视为错误。
5. 返回结果中应包含分辨率信息，便于前端直接展示。

## 6. 与 PRD 对齐

- 对齐模块：2.4 视觉生成模块
- 对齐功能点：支持按镜头查看已生成素材

## 7. Postman 测试步骤

### 前置条件

1. 已完成 `UC012`
2. 已拿到有效的 `project_id` 和 `shot_id`

### 请求配置

- Method: `GET`
- URL: `http://127.0.0.1:8000/api/v1/projects/{{project_id}}/shots/{{shot_id}}/visual-assets`

### 成功判定

1. HTTP 状态码为 `200`
2. `data.project_id` 等于 `{{project_id}}`
3. `data.shot_id` 等于 `{{shot_id}}`
4. `data.items` 为数组
5. 若已有素材，则每项均包含 `file_path`、`prompt_used`、`resolution`

## 8. 后续演进

1. 增加项目维度素材汇总查询
2. 增加人工选择与 `is_selected` 更新接口
