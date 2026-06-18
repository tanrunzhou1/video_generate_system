# 音乐与音频混合表说明

## 范围

本文档补充说明 2.6 音乐与音频混合模块在当前数据库中的核心表结构与使用语义。

## 1. bgm_asset

- 主键：`id`（int，自增）
- 外键：
  - `project_id -> project.id`

字段说明：

- `file_path`：背景音乐文件路径
- `mood_tag`：音乐情绪标签
- `start_time_sec`：音乐片段在项目时间线中的开始时间
- `end_time_sec`：音乐片段在项目时间线中的结束时间
- `gain_db`：默认增益值

当前使用约定：

1. `bgm_asset` 作为项目级背景音乐素材登记表。
2. 一个项目可登记多条背景音乐片段。
3. `mood_tag` 用于支撑“按情绪/节奏选择背景音乐”的最小实现。

## 2. audio_mix_asset

- 主键：`id`（int，自增）
- 外键：
  - `project_id -> project.id`
  - `shot_id -> shot_plan.id`
  - `bgm_asset_id -> bgm_asset.id`

建议字段：

- `mixed_audio_path`：混音结果文件路径
- `ducking_gain_db`：BGM 压低量
- `fade_in_sec`：淡入时长
- `fade_out_sec`：淡出时长
- `is_selected`：是否为当前镜头选中的混音版本
- `created_at`：创建时间

当前使用约定：

1. 每次 `UC021` 混音成功后新增 1 条 `audio_mix_asset` 记录。
2. 一个镜头允许存在多个混音版本。
3. `UC022` 导出成片时优先消费 `is_selected=true` 的版本，否则回退到最新版本。

建议输出路径：

- `storage/projects/{project_id}/audio_mix/shot_{shot_id}_mix.wav`

## 3. NEED_VERIFY

1. 是否增加 `peak_db`、`lufs` 等混音质量指标字段。
2. 若要支持多版本回滚，是否增加 `version_no`。
