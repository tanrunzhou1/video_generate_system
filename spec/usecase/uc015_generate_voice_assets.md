# UC015 生成镜头配音素材 API

## 1. 基本信息

- 用例 ID：UC015
- 类型：HTTP API
- 方法/路径：`POST /api/v1/projects/{project_id}/shots/{shot_id}/voice-assets`
- 目标：基于 `shot_dialogue` 中已落库的镜头台词与角色音色配置，为单个镜头生成多角色配音音频并落库。

## 2. 请求定义

### Path

- `project_id`：项目 ID（必填，自增整数）
- `shot_id`：镜头 ID（必填，自增整数）

### Body

```json
{
  "provider": "xtts-v2",
  "source": "shot_dialogues"
}
```

字段说明：

- `provider`：TTS 提供方，MVP 默认建议为 `xtts-v2`
- `source`：台词来源，MVP 固定为 `shot_dialogues`

## 3. 响应定义

### 200

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "project_id": 12,
    "shot_id": 33,
    "provider": "xtts-v2",
    "source": "shot_dialogues",
    "items": [
      {
        "voice_asset_id": 21,
        "character_id": 3,
        "dialogue_id": 101,
        "line_text": "今天开始行动。",
        "voice_provider": "xtts-v2",
        "audio_path": "storage/projects/12/voice/shot_33_line_1.wav",
        "start_time_sec": 0.0,
        "end_time_sec": 1.8
      },
      {
        "voice_asset_id": 22,
        "character_id": 4,
        "dialogue_id": 102,
        "line_text": "我会配合你。",
        "voice_provider": "xtts-v2",
        "audio_path": "storage/projects/12/voice/shot_33_line_2.wav",
        "start_time_sec": 1.8,
        "end_time_sec": 3.4
      }
    ]
  }
}
```

### 400

- `source` 不支持
- 当前镜头没有可用 `shot_dialogue`
- `shot_dialogue.character_name` 无法匹配到角色档案
- `provider` 不支持

### 404

- 项目不存在
- 镜头不存在
- 角色不存在

## 4. 数据写入

- 主表：`voice_asset`
- 输入表：`shot_dialogue`
- 写入字段：
  - `project_id`
  - `shot_id`
  - `character_id`
  - `line_text`
  - `voice_provider`
  - `audio_path`
  - `start_time_sec`
  - `end_time_sec`

## 5. 业务规则

1. 语音生成默认从 `shot_dialogue` 读取镜头台词，不再要求前端重复传入 `lines`。
2. 每条 `shot_dialogue` 默认生成 1 条 `voice_asset` 记录。
3. `voice_style` 默认从 `character_profile.voice_style` 读取，MVP 阶段不在请求体中重复传递。
4. `start_time_sec` 与 `end_time_sec` 由 TTS 时长计算或顺序累加得到。
5. 当前阶段只处理“单镜头内台词顺序配音”，不做跨镜头音频拼接。
6. 当前镜头总配音时长不应明显超过 `shot_plan.duration_sec`；若超过，先记录告警，后续再补强校验策略。
7. `shot_dialogue.character_name` 必须能映射到当前项目中的 `character_profile.name`。

## 6. 与 PRD 对齐

- 对齐模块：2.5 语音与字幕模块
- 对齐功能点：
  - 角色音色映射与多角色 TTS
  - 台词音频合成（按镜头/按句）

## 7. 前端使用建议

1. 适合作为“单镜头语音生成”按钮的触发接口。
2. 前端不再手动录入台词，而是先展示 `UC025` 镜头详情中的 `dialogue_count` 与台词预览。
3. 生成成功后，立即刷新该镜头的语音素材列表。

## 8. Postman 测试步骤

### 前置条件

1. 已创建项目
2. 已解析出有效镜头 `shot_id`
3. 当前镜头已通过 `UC006` 落库 `shot_dialogue`
4. 已创建角色档案并保证角色名可匹配

### 请求配置

- Method: `POST`
- URL: `http://127.0.0.1:8000/api/v1/projects/{{project_id}}/shots/{{shot_id}}/voice-assets`
- Header: `Content-Type: application/json`

### 请求体

```json
{
  "provider": "xtts-v2",
  "source": "shot_dialogues"
}
```

### 成功判定

1. HTTP 状态码为 `200`
2. `data.project_id` 等于 `{{project_id}}`
3. `data.shot_id` 等于 `{{shot_id}}`
4. `data.items` 为数组，至少 1 条
5. 每条记录包含 `voice_asset_id/dialogue_id/audio_path/start_time_sec/end_time_sec`

## 9. 后续演进

1. 支持按角色覆盖音色参数
2. 支持批量生成项目全部镜头配音
3. 支持重生成单条 `shot_dialogue`
4. 支持情绪标签、语速、停顿等高级参数
