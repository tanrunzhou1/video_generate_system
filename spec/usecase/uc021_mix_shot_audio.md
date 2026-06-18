# UC021 生成镜头混音结果 API

## 1. 基本信息

- 用例 ID：UC021
- 类型：HTTP API
- 方法/路径：`POST /api/v1/projects/{project_id}/shots/{shot_id}/audio-mix`
- 目标：基于镜头配音素材与项目背景音乐素材，生成镜头级混音结果，完成最小音量平衡与淡入淡出处理。

## 2. 请求定义

### Path

- `project_id`：项目 ID（必填，自增整数）
- `shot_id`：镜头 ID（必填，自增整数）

### Body

```json
{
  "bgm_asset_id": 9,
  "ducking_gain_db": -10.0,
  "fade_in_sec": 0.3,
  "fade_out_sec": 0.5
}
```

字段说明：

- `bgm_asset_id`：所选背景音乐素材 ID
- `ducking_gain_db`：配音出现时 BGM 压低量，单位 dB
- `fade_in_sec`：淡入时长
- `fade_out_sec`：淡出时长

## 3. 响应定义

### 200

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "project_id": 12,
    "shot_id": 33,
    "bgm_asset_id": 9,
    "voice_asset_ids": [21, 22],
    "mixed_audio_path": "storage/projects/12/audio_mix/shot_33_mix.wav",
    "ducking_gain_db": -10.0,
    "fade_in_sec": 0.3,
    "fade_out_sec": 0.5
  }
}
```

### 400

- 当前镜头没有可用 `voice_asset`
- `bgm_asset_id` 不属于当前项目
- `fade_in_sec` 或 `fade_out_sec` 非法

### 404

- 项目不存在
- 镜头不存在
- BGM 不存在

## 4. 数据与文件产物

- 输入表：
  - `voice_asset`
  - `bgm_asset`
- 输出文件：
  - `storage/projects/{project_id}/audio_mix/shot_{shot_id}_mix.wav`

## 5. 业务规则

1. 当前镜头必须已有至少 1 条 `voice_asset`。
2. `bgm_asset_id` 必须属于当前项目。
3. 混音结果优先保证台词清晰，BGM 通过 `ducking_gain_db` 做压低。
4. MVP 阶段采用镜头级混音，不做项目全局音频总线处理。
5. 当前阶段混音结果先产出文件，不强制新增数据库表；NEED_VERIFY 后续是否新增 `audio_mix_asset`。

## 6. 与 PRD 对齐

- 对齐模块：2.6 音乐与音频混合模块
- 对齐功能点：
  - 自动裁剪与淡入淡出
  - 配音与 BGM 音量平衡（ducking）

## 7. 前端使用建议

1. 在镜头语音准备完成后，展示“选择 BGM 并混音”操作区。
2. 可先以表单方式暴露：
   - BGM 选择
   - ducking 值
   - fade in/out 参数
3. 混音成功后展示 `mixed_audio_path`，后续可接音频预览。

## 8. Postman 测试步骤

### 前置条件

1. 已创建项目
2. 当前镜头已有 `voice_asset`
3. 项目已登记至少 1 条 `bgm_asset`

### 请求配置

- Method: `POST`
- URL: `http://127.0.0.1:8000/api/v1/projects/{{project_id}}/shots/{{shot_id}}/audio-mix`
- Header: `Content-Type: application/json`

### 请求体

```json
{
  "bgm_asset_id": 9,
  "ducking_gain_db": -10.0,
  "fade_in_sec": 0.3,
  "fade_out_sec": 0.5
}
```

### 成功判定

1. HTTP 状态码为 `200`
2. 返回 `mixed_audio_path`
3. 返回 `voice_asset_ids` 非空
4. 返回的 `bgm_asset_id` 与请求一致

## 9. 后续演进

1. 增加项目级整片混音接口
2. 增加自动按情绪选择 BGM 的策略接口
3. 增加混音结果持久化表
4. 增加峰值、电平等质量检查结果
