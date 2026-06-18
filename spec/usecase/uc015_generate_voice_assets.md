# UC015 生成镜头配音素材 API

## 1. 基本信息

- 用例 ID：UC015
- 类型：HTTP API
- 方法/路径：`POST /api/v1/projects/{project_id}/shots/{shot_id}/voice-assets`
- 目标：基于镜头台词输入与角色音色配置，为单个镜头生成多角色配音音频并落库。

## 2. 请求定义

### Path

- `project_id`：项目 ID（必填，自增整数）
- `shot_id`：镜头 ID（必填，自增整数）

### Body

```json
{
  "provider": "xtts-v2",
  "lines": [
    {
      "character_id": 3,
      "text": "今天开始行动。"
    },
    {
      "character_id": 4,
      "text": "我会配合你。"
    }
  ]
}
```

字段说明：

- `provider`：TTS 提供方，MVP 默认建议为 `xtts-v2`
- `lines`：镜头内台词列表，至少 1 条
- `lines[].character_id`：角色 ID，必须属于当前项目
- `lines[].text`：台词文本，不能为空

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
    "items": [
      {
        "voice_asset_id": 21,
        "character_id": 3,
        "line_text": "今天开始行动。",
        "voice_provider": "xtts-v2",
        "audio_path": "storage/projects/12/voice/shot_33_line_1.wav",
        "start_time_sec": 0.0,
        "end_time_sec": 1.8
      },
      {
        "voice_asset_id": 22,
        "character_id": 4,
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

- `lines` 为空
- `text` 为空
- `character_id` 不属于当前项目
- `provider` 不支持

### 404

- 项目不存在
- 镜头不存在
- 角色不存在

## 4. 数据写入

- 主表：`voice_asset`
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

1. 请求中的 `character_id` 必须属于路径中的 `project_id`。
2. 每条台词生成 1 条 `voice_asset` 记录。
3. `voice_style` 默认从 `character_profile.voice_style` 读取，MVP 阶段不在请求体中重复传递。
4. `start_time_sec` 与 `end_time_sec` 由 TTS 时长计算或顺序累加得到。
5. 当前阶段只处理“单镜头内台词顺序配音”，不做跨镜头音频拼接。
6. 当前镜头总配音时长不应明显超过 `shot_plan.duration_sec`；若超过，先记录告警，后续再补强校验策略。
7. NEED_VERIFY：后续若 `UC006` 将台词正式落库到分镜结构，可把 `lines` 从请求体改为自动读取。

## 6. 与 PRD 对齐

- 对齐模块：2.5 语音与字幕模块
- 对齐功能点：
  - 角色音色映射与多角色 TTS
  - 台词音频合成（按镜头/按句）

## 7. 前端使用建议

1. 适合作为“单镜头语音生成”按钮的触发接口。
2. 前端表单建议按镜头维护台词数组：
   - 角色选择
   - 台词文本
3. 生成成功后，立即刷新该镜头的语音素材列表。

## 8. Postman 测试步骤

### 前置条件

1. 已创建项目
2. 已解析出有效镜头 `shot_id`
3. 已创建角色档案并拿到 `character_id`

### 请求配置

- Method: `POST`
- URL: `http://127.0.0.1:8000/api/v1/projects/{{project_id}}/shots/{{shot_id}}/voice-assets`
- Header: `Content-Type: application/json`

### 请求体

```json
{
  "provider": "xtts-v2",
  "lines": [
    {
      "character_id": 3,
      "text": "今天开始行动。"
    }
  ]
}
```

### 成功判定

1. HTTP 状态码为 `200`
2. `data.project_id` 等于 `{{project_id}}`
3. `data.shot_id` 等于 `{{shot_id}}`
4. `data.items` 为数组，至少 1 条
5. 每条记录包含 `voice_asset_id/audio_path/start_time_sec/end_time_sec`

## 9. 后续演进

1. 支持按角色覆盖音色参数
2. 支持批量生成项目全部镜头配音
3. 支持重生成单条台词
4. 支持情绪标签、语速、停顿等高级参数
