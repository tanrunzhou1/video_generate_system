# UC002 创建项目 API

## 1. 基本信息

- 用例 ID：UC002
- 类型：HTTP API
- 方法/路径：`POST /api/v1/projects`
- 目标：创建短片生成项目，进入 `created` 初始状态。

## 2. 请求定义

### Headers

- `Content-Type: application/json`

### Body

```json
{
  "name": "我的毕业设计短片",
  "description": "可选，项目描述",
  "target_duration_sec": 60,
  "style_preset": "cinematic"
}
```

### 字段约束

- `name`：必填，1~255 字符
- `description`：可选，最长 5000 字符
- `target_duration_sec`：必填，范围建议 10~600
- `style_preset`：可选，最长 128 字符

## 3. 响应定义

### 200

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "project_id": "prj_01J...",
    "name": "我的毕业设计短片",
    "status": "created",
    "target_duration_sec": 60,
    "created_at": "2026-05-29T12:00:00Z"
  }
}
```

### 4xx/5xx

- `400`：参数校验失败
- `409`：项目名称重复
- `500`：数据库写入失败

## 4. 数据落库

- 表：`project`
- 写入字段：`id/name/description/target_duration_sec/style_preset/status/created_at/updated_at`
- 状态初始值：`created`

## 5. 业务规则

1. `name` 不允许空白字符串，且全局唯一（项目不能同名）。
2. `target_duration_sec` 非法时拒绝请求。
3. 创建成功后返回 `project_id`，作为后续上传素材和状态查询的主键。

## 6. 与 PRD 对齐

- 对齐模块：2.1 项目管理模块（创建项目）
- 对齐验收：用户可快速完成任务创建。
