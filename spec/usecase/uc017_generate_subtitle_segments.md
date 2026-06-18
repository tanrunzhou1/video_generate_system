# UC017 生成镜头字幕片段 API

## 1. 基本信息

- 用例 ID：UC017
- 类型：HTTP API
- 方法/路径：`POST /api/v1/projects/{project_id}/shots/{shot_id}/subtitle-segments`
- 目标：基于镜头配音素材生成字幕片段时间轴，并落库为可后续导出 SRT 的结构化字幕数据。

## 2. 请求定义

### Path

- `project_id`：项目 ID（必填，自增整数）
- `shot_id`：镜头 ID（必填，自增整数）

### Body

```json
{
  "source": "voice_assets"
}
```

字段说明：

- `source`：字幕来源，MVP 固定为 `voice_assets`

## 3. 响应定义

### 200

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "project_id": 12,
    "shot_id": 33,
    "source": "voice_assets",
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

### 400

- `source` 不支持
- 当前镜头没有可用语音素材

### 404

- 项目不存在
- 镜头不存在

## 4. 数据写入

- 主表：`subtitle_segment`
- 写入字段：
  - `project_id`
  - `shot_id`
  - `text`
  - `start_time_sec`
  - `end_time_sec`

## 5. 业务规则

1. MVP 阶段字幕直接从 `voice_asset.line_text + start/end_time_sec` 生成，不额外做 ASR 对齐。
2. 每条 `voice_asset` 默认生成 1 条 `subtitle_segment`。
3. 生成前可先清理当前镜头旧字幕，避免重复片段；具体覆盖策略 NEED_VERIFY。
4. 当前阶段只保证镜头级字幕结构正确，项目级 `.srt` 文件导出放在后续迭代。
5. 时间轴精度以 `voice_asset` 结果为准，目标偏差满足 PRD 中 `<300ms` 的可接受范围。
6. 闭环上游依赖 `shot_dialogue -> voice_asset -> subtitle_segment`，不再要求前端手工录入台词。

## 6. 与 PRD 对齐

- 对齐模块：2.5 语音与字幕模块
- 对齐功能点：
  - 字幕文件（SRT）生成
  - 音频-字幕时间对齐

## 7. 前端使用建议

1. 在“镜头配音生成完成”后提供“生成字幕”按钮。
2. 字幕列表页建议直接展示：
   - 文本
   - 开始时间
   - 结束时间
3. 若后端后续补全项目级 SRT 导出接口，可复用本接口结果作为预览数据。

## 8. Postman 测试步骤

### 前置条件

1. 已创建项目
2. 已拿到有效 `shot_id`
3. 当前镜头至少有 1 条 `voice_asset`

### 请求配置

- Method: `POST`
- URL: `http://127.0.0.1:8000/api/v1/projects/{{project_id}}/shots/{{shot_id}}/subtitle-segments`
- Header: `Content-Type: application/json`

### 请求体

```json
{
  "source": "voice_assets"
}
```

### 成功判定

1. HTTP 状态码为 `200`
2. `data.items` 为数组
3. 每条字幕包含 `subtitle_segment_id/text/start_time_sec/end_time_sec`
4. 字幕时间轴与语音素材时间轴一致

## 9. 后续演进

1. 支持项目级 SRT 合并导出
2. 支持字幕断句与自动换行优化
3. 支持基于 ASR 的精细时间对齐
