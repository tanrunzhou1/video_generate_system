# UC009 创建角色档案 API

## 1. 基本信息

- 用例 ID：UC009
- 类型：HTTP API
- 方法/路径：`POST /api/v1/projects/{project_id}/characters`
- 目标：为项目创建角色档案，保存角色名、人设文本、音色风格、参考图路径、提示词约束和 seed 策略。

## 2. 请求定义

### Path

- `project_id`：项目 ID（必填，自增整数）

### Body

```json
{
  "name": "主角",
  "persona_text": "17 岁女高中生，冷静但有行动力。",
  "voice_style": "young_female_calm",
  "reference_image_asset_ids": [21, 22],
  "prompt_constraints": {
    "positive": ["黑色短发", "校服", "电影感光影"],
    "negative": ["多余手指", "面部崩坏"]
  },
  "seed_policy": {
    "mode": "fixed",
    "seed": 123456
  }
}
```

## 3. 响应定义

### 200

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "character_id": 7,
    "project_id": 12,
    "name": "主角",
    "voice_style": "young_female_calm",
    "reference_image_paths": [
      "storage/projects/12/character_image/hero_1.jpg",
      "storage/projects/12/character_image/hero_2.jpg"
    ],
    "created_at": "2026-06-02T16:00:00"
  }
}
```

### 400

- `name` 为空
- `persona_text` 为空
- `reference_image_asset_ids` 为空
- 指定的素材不存在，或素材类型不是 `character_image`

### 404

- 项目不存在

### 409

- 同一项目下角色名重复

## 4. 数据落库

- 主表：`character_profile`
- 依赖表：`project_asset`
- 关键写入字段：
  - `project_id`
  - `name`
  - `persona_text`
  - `voice_style`
  - `reference_image_paths`
  - `prompt_constraints`
  - `seed_policy`

## 5. 业务规则

1. 角色名在同一项目内必须唯一。
2. `reference_image_asset_ids` 必须全部属于当前项目，且素材类型为 `character_image`。
3. `reference_image_paths` 采用 `project_asset.file_path` 回填保存，MVP 不单独复制图片。
4. `prompt_constraints` 和 `seed_policy` 允许保留简化 JSON 结构，但必须可被后续视觉生成模块直接读取。
5. MVP 阶段先不做 CLIP 特征提取，只保存后续一致性模块所需的输入数据。

## 6. 与 PRD 对齐

- 对齐模块：2.3 角色一致性与素材检索模块
- 对齐功能点：
  - 建立角色资产库（参考图、关键词、禁用词、seed）
  - 风格约束模板注入（prompt 模板）

## 7. Postman 测试步骤

### 前置条件

1. 已创建项目
2. 已通过 `UC003` 上传至少一张 `character_image`
3. 已拿到可用的角色图素材 ID

### 请求配置

- Method: `POST`
- URL: `http://127.0.0.1:8000/api/v1/projects/{{project_id}}/characters`
- Header: `Content-Type: application/json`

### 成功判定

1. HTTP 状态码为 `200`
2. 返回体 `code=0`
3. `data.character_id` 为整数
4. `data.reference_image_paths` 非空

## 8. 后续演进

1. 增加角色图多版本管理
2. 增加 CLIP embedding 持久化
3. 增加角色约束模板编辑能力
