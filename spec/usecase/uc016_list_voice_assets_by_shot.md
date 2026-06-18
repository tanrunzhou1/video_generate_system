# UC016 查询镜头配音素材列表 API

## 1. 基本信息

- 用例 ID：UC016
- 类型：HTTP API
- 方法/路径：`GET /api/v1/projects/{project_id}/shots/{shot_id}/voice-assets`
- 目标：按镜头返回已生成的配音素材列表，供前端播放、检查时长与后续字幕生成使用。

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
        "voice_asset_id": 21,
        "character_id": 3,
        "line_text": "今天开始行动。",
        "voice_provider": "xtts-v2",
        "audio_path": "storage/projects/12/voice/shot_33_line_1.wav",
        "start_time_sec": 0.0,
        "end_time_sec": 1.8
      }
    ]
  }
}
```

### 404

- 项目不存在
- 镜头不存在

## 4. 数据读取

- 主表：`voice_asset`
- 读取字段：
  - `id`
  - `project_id`
  - `shot_id`
  - `character_id`
  - `line_text`
  - `voice_provider`
  - `audio_path`
  - `start_time_sec`
  - `end_time_sec`

## 5. 业务规则

1. 仅返回当前项目、当前镜头的语音素材。
2. 默认按 `start_time_sec` 升序返回，便于前端直接按播放顺序展示。
3. MVP 阶段不分页。
4. 返回结果可直接作为字幕生成接口的输入基础。

## 6. 与 PRD 对齐

- 对齐模块：2.5 语音与字幕模块
- 对齐功能点：台词音频合成（按镜头/按句）

## 7. 后续演进

1. 增加按 `character_id` 过滤
2. 增加播放时长汇总
3. 增加语音波形图或音频元信息
