# UC024 查询成片详情 API

## 1. 基本信息

- 用例 ID：UC024
- 类型：HTTP API
- 方法/路径：`GET /api/v1/projects/{project_id}/final-videos/{video_id}`
- 目标：返回单个成片的完整信息，供前端详情页、播放页或下载页使用。

## 2. 请求定义

### Path

- `project_id`：项目 ID（必填，自增整数）
- `video_id`：成片 ID（必填，自增整数）

## 3. 响应定义

### 200

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "video_id": 5,
    "project_id": 12,
    "resolution": "720p",
    "duration_sec": 58.4,
    "file_path": "storage/projects/12/final_video/final_720p.mp4",
    "cover_image_path": "storage/projects/12/final_video/final_720p_cover.png",
    "created_at": "2026-06-18T18:30:00+08:00"
  }
}
```

### 404

- 项目不存在
- 成片不存在
- `video_id` 不属于当前项目

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

1. `video_id` 必须属于路径中的 `project_id`。
2. 当前返回的是“成片元数据”，不直接返回视频二进制流。
3. `file_path` 与 `cover_image_path` 当前仍为本地文件路径，后续若接对象存储或静态资源服务，再扩展为访问 URL。

## 6. 与 PRD 对齐

- 对齐模块：2.7 视频合成与导出模块
- 对齐功能点：可稳定导出 MP4，支持结果查看

## 7. 后续演进

1. 增加播放地址与下载地址
2. 增加导出参数回显，例如是否带字幕
3. 增加导出任务来源 `task_id` 关联
