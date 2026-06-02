# UC006 工作流剧本解析

## 1. 基本信息

- 用例 ID：UC006
- 类型：内部工作流节点
- 节点名称：`parse_script`
- 代码位置：`app/workflow/graph.py`
- 目标：把项目中的原始剧本文本解析为结构化分镜输入，为后续 `scene`、`shot`、视觉生成与语音流程提供基础数据。

## 2. 输入定义

当前工作流状态：

```python
{
  "project_id": 1001,
  "script_text": "剧本文本",
  "shots": [],
  "status": "created"
}
```

### 字段说明

- `project_id`：项目 ID（必填）
- `script_text`：原始剧本文本（必填）
- `shots`：镜头列表（首次进入节点时允许为空）
- `status`：当前工作流状态

## 3. 输出定义

MVP 阶段目标输出：

```python
{
  "project_id": 1001,
  "script_text": "剧本文本",
  "shots": [
    {
      "scene_index": 1,
      "shot_index": 1,
      "duration_sec": 5.0,
      "characters": ["主角"],
      "visual_prompt": "夜景街道，主角独自行走",
      "dialogue": "我要出发了"
    }
  ],
  "status": "script_parsed"
}
```

### 当前代码状态

- 当前实现仅返回：
  - `status = "script_parsed"`
  - `shots = []`
- 尚未接入真实 LLM 拆解逻辑

## 4. 处理流程

1. 读取工作流状态中的 `script_text`
2. 对剧本文本做基础清洗（去除空白、非法字符，MVP 可选）
3. 调用 LLM 或规则引擎，执行：
   - 场景切分
   - 镜头拆解
   - 角色与台词归属
   - 画面提示词生成
4. 将结构化结果写回 `shots`
5. 更新 `status = "script_parsed"`

## 5. 业务规则

1. `script_text` 为空时，不应进入成功状态，应抛出错误或标记失败。
2. 每个镜头至少应包含：`scene_index`、`shot_index`、`duration_sec`、`characters`、`visual_prompt`
3. 解析结果应尽量与 PRD 要求的 `ShotPlan` 字段保持一致，便于后续落库。
4. MVP 阶段允许先返回简化版 `shots` 结构，不强制一次覆盖全部字段。

## 6. 错误处理

1. LLM 调用失败时，应记录任务日志并更新任务状态为失败。
2. 剧本内容为空或无有效分镜时，应返回可识别错误信息。
3. 解析结果格式不合法时，应阻断后续节点执行。

## 7. 与 PRD 对齐

- 对齐模块：2.2 剧本解析与分镜规划模块
- 对齐验收：
  - 输出结构化分镜（JSON）
  - 每个镜头至少包含时长、角色、画面描述、台词片段

## 8. 当前差距

1. 尚未接入 Qwen 或其他 LLM
2. 尚未定义 `shots` 的稳定 Pydantic/TypedDict 结构
3. 尚未将解析结果落库到 `script_scene`、`shot_plan`
4. 尚未与 `render_task` 日志链路打通

## 9. 后续实现建议

1. 先定义 `ShotDraft` 数据结构，固定节点输出格式
2. 增加 `script_text` 为空的校验逻辑
3. 接入 LLM 后增加解析失败重试机制
4. 将结果同步写入 `script_scene` 和 `shot_plan`
