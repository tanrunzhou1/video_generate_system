# UC014 分页查询项目列表 API

## 1. 基本信息

- 用例 ID：UC014
- 类型：HTTP API
- 方法/路径：`GET /api/v1/projects`
- 目标：分页返回系统中已创建的项目列表，支持按创建时间倒序查看，供前端项目首页、历史项目列表页使用。

## 2. 请求定义

### Query

- `page`：页码（可选，正整数，默认 `1`）
- `page_size`：每页条数（可选，正整数，默认 `10`）

## 3. 响应定义

### 200

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
        "created_at": "2026-06-03T10:00:00",
        "updated_at": "2026-06-03T10:05:00"
      },
      {
        "project_id": 11,
        "name": "古风练习片",
        "description": "角色一致性测试",
        "target_duration_sec": 45,
        "style_preset": "oriental",
        "status": "running",
        "created_at": "2026-06-03T09:30:00",
        "updated_at": "2026-06-03T09:42:00"
      }
    ]
  }
}
```

### 400

- `page` 非法，例如小于 `1`
- `page_size` 非法，例如小于 `1`

## 4. 数据读取

- 主表：`project`
- 读取字段：
  - `id`
  - `name`
  - `description`
  - `target_duration_sec`
  - `style_preset`
  - `status`
  - `created_at`
  - `updated_at`

## 5. 业务规则

1. 列表按 `created_at` 倒序返回，最新创建的项目排在前面。
2. 当 `created_at` 相同时，可按 `id` 倒序作为稳定兜底排序。
3. `page` 默认值为 `1`，`page_size` 默认值为 `10`。
4. `page_size` 建议设置最大值上限，MVP 可取 `100`，避免一次性返回过大数据量。
5. 当前阶段仅支持基础分页，不做关键字搜索、状态筛选和排序切换。

## 6. 与 PRD 对齐

- 对齐模块：2.1 项目管理模块
- 对齐功能点：分页查询已创建项目列表（支持按创建时间倒序查看）

## 7. 前端使用建议

1. 适合作为项目首页或“历史项目”页面主接口。
2. 列表项建议展示：
   - 项目名称
   - 项目状态
   - 目标时长
   - 风格预设
   - 创建时间
   - 更新时间
3. 点击行或卡片跳转到 `GET /api/v1/projects/{project_id}` 对应详情页。

## 8. Postman 测试步骤

### 前置条件

1. 已通过 `UC002` 创建多个项目。

### 请求配置

- Method: `GET`
- URL: `http://127.0.0.1:8000/api/v1/projects?page=1&page_size=10`

### 成功判定

1. HTTP 状态码为 `200`
2. `data.page` 等于请求页码
3. `data.page_size` 等于请求分页大小
4. `data.total` 为大于等于 `0` 的整数
5. `data.items` 为数组
6. `data.items` 中每项均包含 `project_id/name/status/created_at/updated_at`
7. 列表顺序满足“创建时间倒序”

## 9. 后续演进

1. 增加按项目名称关键字搜索
2. 增加按状态筛选
3. 增加按更新时间排序
4. 增加项目素材准备度摘要，减少前端二次详情请求
