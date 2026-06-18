# UC019 创建背景音乐素材 API

## 1. 基本信息

- 用例 ID：UC019
- 类型：HTTP API
- 方法/路径：`POST /api/v1/projects/{project_id}/bgm-assets`
- 目标：为项目登记 1 条背景音乐素材记录，保存音乐文件路径、情绪标签与使用时段，供后续镜头混音使用。

## 2. 请求定义

### Path

- `project_id`：项目 ID（必填，自增整数）

### Body

```json
{
  "file_path": "storage/projects/12/bgm/calm_theme.mp3",
  "mood_tag": "calm",
  "start_time_sec": 0.0,
  "end_time_sec": 18.0,
  "gain_db": -6.0
}
```

字段说明：

- `file_path`：背景音乐文件路径
- `mood_tag`：情绪标签，例如 `calm`、`tense`、`hopeful`
- `start_time_sec`：在项目时间轴中的开始时间
- `end_time_sec`：在项目时间轴中的结束时间
- `gain_db`：音量增益，单位 dB，负值表示降低音量

## 3. 响应定义

### 200

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "bgm_asset_id": 9,
    "project_id": 12,
    "file_path": "storage/projects/12/bgm/calm_theme.mp3",
    "mood_tag": "calm",
    "start_time_sec": 0.0,
    "end_time_sec": 18.0,
    "gain_db": -6.0
  }
}
```

### 400

- `file_path` 为空
- `end_time_sec <= start_time_sec`

### 404

- 项目不存在

## 4. 数据写入

- 主表：`bgm_asset`
- 写入字段：
  - `project_id`
  - `file_path`
  - `mood_tag`
  - `start_time_sec`
  - `end_time_sec`
  - `gain_db`

## 5. 业务规则

1. MVP 阶段背景音乐素材先由前端或人工准备好文件，再调用本接口登记，不强制后端自动选曲。
2. `mood_tag` 用于支持 PRD 中“按情绪/节奏选择背景音乐”的最小实现。
3. `gain_db` 默认建议为负值，例如 `-6.0`，避免压过台词。
4. 当前阶段只登记项目级 BGM 片段，不做自动裁剪产物持久化。

## 6. 与 PRD 对齐

- 对齐模块：2.6 音乐与音频混合模块
- 对齐功能点：按情绪/节奏选择背景音乐

## 7. 后续演进

1. 支持直接上传 BGM 文件而不只登记路径
2. 支持自动推荐 BGM
3. 支持项目内多个 BGM 片段拼接策略
