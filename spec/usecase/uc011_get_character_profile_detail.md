# UC011 查询角色详情 API

## 1. 基本信息

- 用例 ID：UC011
- 类型：HTTP API
- 方法/路径：`GET /api/v1/projects/{project_id}/characters/{character_id}`
- 目标：返回单个角色档案的完整详情，供前端查看与后续视觉生成提示词拼装使用。

## 2. 请求定义

### Path

- `project_id`：项目 ID（必填，自增整数）
- `character_id`：角色 ID（必填，自增整数）

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
    "persona_text": "17 岁女高中生，冷静但有行动力。",
    "voice_style": "young_female_calm",
    "reference_image_paths": [
      "storage/projects/12/character_image/hero_1.jpg",
      "storage/projects/12/character_image/hero_2.jpg"
    ],
    "prompt_constraints": {
      "positive": ["黑色短发", "校服", "电影感光影"],
      "negative": ["多余手指", "面部崩坏"]
    },
    "seed_policy": {
      "mode": "fixed",
      "seed": 123456
    }
  }
}
```

### 404

- 项目不存在
- 角色不存在
- 角色不属于当前项目

## 4. 数据读取

- 主表：`character_profile`
- 关键字段：
  - `name`
  - `persona_text`
  - `voice_style`
  - `reference_image_paths`
  - `prompt_constraints`
  - `seed_policy`

## 5. 业务规则

1. `character_id` 必须属于路径中的 `project_id`。
2. `prompt_constraints` 原样返回，便于后续提示词注入。
3. `seed_policy` 原样返回，便于后续视觉生成阶段复用。
4. MVP 阶段不返回 CLIP embedding、相似度分数等派生数据。

## 6. 与 PRD 对齐

- 对齐模块：2.3 角色一致性与素材检索模块
- 对齐功能点：
  - 建立角色资产库
  - 风格约束模板注入

## 7. Postman 测试步骤

### 前置条件

1. 已创建项目
2. 已成功创建角色档案，并拿到 `character_id`

### 请求配置

- Method: `GET`
- URL: `http://127.0.0.1:8000/api/v1/projects/{{project_id}}/characters/{{character_id}}`

### 成功判定

1. HTTP 状态码为 `200`
2. `data.character_id` 等于 `{{character_id}}`
3. `data.reference_image_paths` 为数组
4. `data.prompt_constraints` 与 `data.seed_policy` 存在

## 8. 后续演进

1. 增加角色编辑接口
2. 增加角色一致性评分查询接口
