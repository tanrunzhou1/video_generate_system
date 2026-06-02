# UC010 查询角色列表 API

## 1. 基本信息

- 用例 ID：UC010
- 类型：HTTP API
- 方法/路径：`GET /api/v1/projects/{project_id}/characters`
- 目标：返回项目下全部角色档案列表，供前端进行角色管理与后续镜头绑定。

## 2. 请求定义

### Path

- `project_id`：项目 ID（必填，自增整数）

## 3. 响应定义

### 200

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "project_id": 12,
    "items": [
      {
        "character_id": 7,
        "name": "主角",
        "voice_style": "young_female_calm",
        "reference_image_count": 2,
        "created_at": "2026-06-02T16:00:00"
      },
      {
        "character_id": 8,
        "name": "朋友",
        "voice_style": "young_male_bright",
        "reference_image_count": 1,
        "created_at": "2026-06-02T16:10:00"
      }
    ]
  }
}
```

### 404

- 项目不存在

## 4. 数据读取

- 主表：`character_profile`
- 读取字段：
  - `id`
  - `project_id`
  - `name`
  - `voice_style`
  - `reference_image_paths`
  - `created_at`

## 5. 业务规则

1. 列表仅返回当前项目的角色，不跨项目聚合。
2. `reference_image_count` 由 `reference_image_paths` 长度计算得到。
3. 默认按 `created_at` 升序返回，便于前端按录入顺序展示。
4. MVP 阶段不做分页；若角色数量增加，再补分页参数。

## 6. 与 PRD 对齐

- 对齐模块：2.3 角色一致性与素材检索模块
- 对齐功能点：建立角色资产库

## 7. Postman 测试步骤

### 前置条件

1. 已创建项目
2. 已成功创建至少一个角色档案

### 请求配置

- Method: `GET`
- URL: `http://127.0.0.1:8000/api/v1/projects/{{project_id}}/characters`

### 成功判定

1. HTTP 状态码为 `200`
2. `data.project_id` 等于 `{{project_id}}`
3. `data.items` 为数组
4. 每项均包含 `character_id/name/reference_image_count`

## 8. 后续演进

1. 增加分页与关键字搜索
2. 增加按角色名排序或按最近使用排序
