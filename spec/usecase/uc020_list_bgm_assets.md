# UC020 查询项目背景音乐素材列表 API

## 1. 基本信息

- 用例 ID：UC020
- 类型：HTTP API
- 方法/路径：`GET /api/v1/projects/{project_id}/bgm-assets`
- 目标：返回项目下已登记的背景音乐素材列表，供前端选择混音输入。

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
        "bgm_asset_id": 9,
        "file_path": "storage/projects/12/bgm/calm_theme.mp3",
        "mood_tag": "calm",
        "start_time_sec": 0.0,
        "end_time_sec": 18.0,
        "gain_db": -6.0
      }
    ]
  }
}
```

### 404

- 项目不存在

## 4. 数据读取

- 主表：`bgm_asset`
- 读取字段：
  - `id`
  - `project_id`
  - `file_path`
  - `mood_tag`
  - `start_time_sec`
  - `end_time_sec`
  - `gain_db`

## 5. 业务规则

1. 仅返回当前项目下的 BGM 记录。
2. 默认按 `start_time_sec` 升序返回，便于前端按时间线展示。
3. MVP 阶段不分页。

## 6. 与 PRD 对齐

- 对齐模块：2.6 音乐与音频混合模块
- 对齐功能点：按情绪/节奏选择背景音乐

## 7. 后续演进

1. 增加按 `mood_tag` 过滤
2. 增加音频时长元信息
3. 增加当前 BGM 是否已用于混音结果的标记
