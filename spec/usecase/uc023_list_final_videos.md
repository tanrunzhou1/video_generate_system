# UC023 查询项目成片列表 API

## 1. 基本信息

- 用例 ID：UC023
- 类型：HTTP API
- 方法/路径：`GET /api/v1/projects/{project_id}/final-videos`
- 目标：返回项目下已导出的成片列表，供前端展示历史导出记录与结果选择。

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
        "video_id": 5,
        "resolution": "720p",
        "duration_sec": 58.4,
        "file_path": "storage/projects/12/final_video/final_720p.mp4",
        "cover_image_path": "storage/projects/12/final_video/final_720p_cover.png",
        "created_at": "2026-06-18T18:30:00+08:00"
      }
    ]
  }
}
```

### 404

- 项目不存在

## 4. 数据读取

- 主表：`final_video`
- 读取字段：
  - `id`
  - `project_id`
  - `resolution`
  - `duration_sec`
  - `file_path`
  - `cover_image_path`
  - `created_at`

## 5. 业务规则

1. 仅返回当前项目下的成片记录。
2. 默认按 `created_at` 倒序返回，最新导出的成片排在前面。
3. MVP 阶段不分页；若后续导出版本增多，再补分页参数。

## 6. 与 PRD 对齐

- 对齐模块：2.7 视频合成与导出模块
- 对齐功能点：多规格导出

## 7. 后续演进

1. 增加分页与按分辨率过滤
2. 增加“当前推荐版本”标记
3. 增加下载 URL 与预览 URL
