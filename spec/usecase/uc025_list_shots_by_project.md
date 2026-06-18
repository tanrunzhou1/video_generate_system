# UC025 查询项目镜头列表 API

## 1. 基本信息

- 用例 ID：UC025
- 类型：HTTP API
- 方法/路径：`GET /api/v1/projects/{project_id}/shots`
- 目标：返回项目下已解析出的镜头列表，作为视觉生成、语音生成、字幕生成、混音与视频导出的统一上游入口。

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
        "shot_id": 33,
        "scene_id": 7,
        "scene_index": 1,
        "shot_index": 1,
        "duration_sec": 5.0,
        "characters": ["主角"],
        "camera_instruction": "中景，跟拍",
        "visual_prompt": "夜景街道，主角独自行走",
        "status": "planned",
        "dialogue_count": 2
      },
      {
        "shot_id": 34,
        "scene_id": 7,
        "scene_index": 1,
        "shot_index": 2,
        "duration_sec": 4.0,
        "characters": ["朋友"],
        "camera_instruction": "近景，侧拍",
        "visual_prompt": "朋友在路灯下回头",
        "status": "planned",
        "dialogue_count": 1
      }
    ]
  }
}
```

### 404

- 项目不存在

## 4. 数据读取

- 主表：`shot_plan`
- 关联表：
  - `script_scene`
  - `shot_dialogue`
- 读取字段：
  - `shot_plan.id`
  - `shot_plan.scene_id`
  - `shot_plan.shot_index`
  - `shot_plan.duration_sec`
  - `shot_plan.characters`
  - `shot_plan.camera_instruction`
  - `shot_plan.visual_prompt`
  - `shot_plan.status`
  - `script_scene.scene_index`
  - `shot_dialogue` 计数

## 5. 业务规则

1. 仅返回当前项目下的镜头，不跨项目聚合。
2. 默认按 `scene_index` 升序、`shot_index` 升序返回，便于前端按时间线展示。
3. `dialogue_count` 从 `shot_dialogue` 聚合得到，用于提示镜头是否已具备语音生成输入。
4. MVP 阶段不分页；若镜头数量增多，再补分页参数。

## 6. 与 PRD 对齐

- 对齐模块：2.2 剧本解析与分镜规划模块
- 对齐用途：为 2.4/2.5/2.6/2.7 后续模块提供稳定的镜头入口

## 7. 后续演进

1. 增加镜头筛选，例如按 `status` 过滤
2. 增加镜头下游产物摘要，如 `visual_asset_count`、`voice_asset_count`
3. 增加镜头编辑接口
