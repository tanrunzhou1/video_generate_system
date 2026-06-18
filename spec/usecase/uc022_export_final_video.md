# UC022 导出项目成片 API

## 1. 基本信息

- 用例 ID：UC022
- 类型：HTTP API
- 方法/路径：`POST /api/v1/projects/{project_id}/final-videos`
- 目标：基于项目下已生成的视觉素材、镜头级混音结果与字幕片段，触发一次项目成片合成与导出。

## 2. 请求定义

### Path

- `project_id`：项目 ID（必填，自增整数）

### Body

```json
{
  "resolution": "720p",
  "include_subtitles": true,
  "transition_mode": "none"
}
```

字段说明：

- `resolution`：导出分辨率，MVP 建议支持 `720p`、`1080p`
- `include_subtitles`：是否叠加字幕
- `transition_mode`：转场模式，MVP 固定支持 `none`

## 3. 响应定义

### 200

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "project_id": 12,
    "task_id": 58,
    "status": "pending",
    "resolution": "720p",
    "include_subtitles": true,
    "transition_mode": "none",
    "log_file_path": "logs/tasks/project_12/task_58.log"
  }
}
```

### 400

- 项目下没有可用镜头视觉素材
- 项目下没有可用镜头混音结果
- `resolution` 不支持
- `transition_mode` 不支持

### 404

- 项目不存在

## 4. 数据与文件产物

- 输入数据来源：
  - `visual_asset`
  - `audio_mix_asset`
  - `subtitle_segment`
- 过程任务：
  - `render_task.stage = "final_video_export"`
- 输出表：
  - `final_video`
- 输出文件建议路径：
  - `storage/projects/{project_id}/final_video/final_{resolution}.mp4`

## 5. 业务规则

1. 导出前必须保证项目至少存在可用的镜头视觉素材。
2. 若项目要求带音频，必须存在对应镜头已选中或最新的 `audio_mix_asset` 结果；MVP 阶段默认要求音频链路已准备完成。
3. `include_subtitles=true` 时，系统从 `subtitle_segment` 叠加字幕。
4. `transition_mode` 在 MVP 阶段只支持 `none`，后续再扩展淡入淡出、交叉溶解等。
5. 当前接口以“触发导出任务”为主，成片文件生成后通过查询接口查看结果。
6. 对每个镜头，导出时应优先使用 `is_selected=true` 的视觉素材与混音素材；若不存在，则回退到最新一条记录。

## 6. 与 PRD 对齐

- 对齐模块：2.7 视频合成与导出模块
- 对齐功能点：
  - 镜头拼接、转场（可选）
  - 配音轨道合入
  - 字幕叠加
  - 多规格导出

## 7. 前端使用建议

1. 在项目工作台或导出页面提供“导出成片”按钮。
2. 表单先暴露最小字段：
   - 分辨率
   - 是否叠加字幕
3. 提交成功后，直接跳转任务日志页或项目成片列表页。

## 8. Postman 测试步骤

### 前置条件

1. 已创建项目
2. 项目已有镜头视觉素材
3. 项目已有镜头语音/混音与字幕数据

### 请求配置

- Method: `POST`
- URL: `http://127.0.0.1:8000/api/v1/projects/{{project_id}}/final-videos`
- Header: `Content-Type: application/json`

### 请求体

```json
{
  "resolution": "720p",
  "include_subtitles": true,
  "transition_mode": "none"
}
```

### 成功判定

1. HTTP 状态码为 `200`
2. 返回 `task_id`
3. 返回 `status` 为任务初始状态
4. 返回 `log_file_path`

## 9. 后续演进

1. 支持异步轮询导出进度
2. 支持更多转场模式
3. 支持仅导出无字幕版本
4. 支持封面图自动生成
