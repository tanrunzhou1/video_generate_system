# UC003 上传项目素材 API

## 1. 基本信息

- 用例 ID：UC003
- 类型：HTTP API（multipart/form-data）
- 方法/路径：`POST /api/v1/projects/{project_id}/assets`
- 目标：上传剧本、人设图、人设文档、可选风格参考，并记录素材元数据。

## 2. 请求定义

### Path

- `project_id`：项目 ID（必填）

### Form-Data 字段

- `script_file`：剧本文件（必填，`txt/md/docx/pdf`）
- `persona_doc`：人物设定文档（必填，`txt/md/docx/pdf`）
- `character_images`：人物设定图（必填，多文件，`png/jpg/jpeg/webp`）
- `style_reference`：风格参考（可选，`png/jpg/jpeg/webp`）

### 文件约束（MVP 建议）

- 单文件大小：<= 20MB
- 单次上传文件总数：<= 20

## 3. 响应定义

### 200

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "project_id": 1001,
    "uploaded": [
      {
        "asset_id": 1,
        "asset_type": "script_file",
        "file_path": "storage/projects/1001/script_file/xxx.md"
      }
    ],
    "failed": []
  }
}
```

### 4xx/5xx

- `404`：项目不存在
- `400`：文件类型/大小不合法
- `500`：文件写盘或数据库写入失败

## 4. 数据落库

- 表：`project_asset`（新增，见 `spec/arch/database/project_asset_tables.md`）
- 存储目录：`storage/projects/{project_id}/{asset_type}/`

## 5. 业务规则

1. 必填素材缺失时返回 `400`。
2. 同类型重复上传允许，默认保留历史并以最新为主（MVP 简化策略）。
3. 上传完成后可触发项目状态推进逻辑（如素材齐全后可进入 `running`，具体由工作流接入时确定）。

## 6. 与 PRD 对齐

- 对齐模块：2.1 项目管理模块（上传输入素材）
- 对齐验收：任务创建与素材上传流程可在短时间内完成。

## 7. Postman 测试步骤

### 前置条件

1. 服务已启动（`make dev`）。
2. 先调用 `UC002` 创建项目，拿到 `project_id`（int）。
3. 本地准备测试文件：`script.md`、`persona.md`、`a.jpg`、`b.jpg`。

### 请求配置

- Method: `POST`
- URL: `http://127.0.0.1:8000/api/v1/projects/{{project_id}}/assets`
- Body: `form-data`
  - `script_file`（File）= `script.md`
  - `persona_doc`（File）= `persona.md`
  - `character_images`（File）= `a.jpg`
  - `character_images`（File）= `b.jpg`
  - `style_reference`（File，可选）= `style.jpg`

### 成功判定

1. HTTP 状态码为 `200`。
2. 返回体 `code=0`、`data.project_id={{project_id}}`。
3. `data.uploaded` 数组长度大于等于 4（不含可选风格图时）。
4. 数据库可查到素材记录（`project_asset` 表）。
