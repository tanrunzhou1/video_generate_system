# UC018 查询镜头字幕片段列表 API

## 1. 基本信息

- 用例 ID：UC018
- 类型：HTTP API
- 方法/路径：`GET /api/v1/projects/{project_id}/shots/{shot_id}/subtitle-segments`
- 目标：按镜头返回已生成字幕片段列表，供前端预览、校对和后续视频合成使用。

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
        "subtitle_segment_id": 31,
        "text": "今天开始行动。",
        "start_time_sec": 0.0,
        "end_time_sec": 1.8
      },
      {
        "subtitle_segment_id": 32,
        "text": "我会配合你。",
        "start_time_sec": 1.8,
        "end_time_sec": 3.4
      }
    ]
  }
}
```

### 404

- 项目不存在
- 镜头不存在

## 4. 数据读取

- 主表：`subtitle_segment`
- 读取字段：
  - `id`
  - `project_id`
  - `shot_id`
  - `text`
  - `start_time_sec`
  - `end_time_sec`

## 5. 业务规则

1. 仅返回当前项目、当前镜头的字幕数据。
2. 默认按 `start_time_sec` 升序返回。
3. MVP 阶段不分页。
4. 当前返回结构以“结构化字幕片段”为主，不直接返回 `.srt` 文本。

## 6. 与 PRD 对齐

- 对齐模块：2.5 语音与字幕模块
- 对齐功能点：音频-字幕时间对齐

## 7. 后续演进

1. 增加项目级字幕列表接口
2. 增加 SRT 文本导出
3. 增加字幕编辑与校准接口
