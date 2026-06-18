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

## 2. 当前混音产物

当前阶段没有独立数据库表保存镜头混音结果，先采用“文件落盘 + 接口直接返回路径”的轻量方案。

建议输出路径：

- `storage/projects/{project_id}/audio_mix/shot_{shot_id}_mix.wav`

NEED_VERIFY：

1. 后续是否新增 `audio_mix_asset` 表，记录：
   - `project_id`
   - `shot_id`
   - `bgm_asset_id`
   - `mixed_audio_path`
   - `ducking_gain_db`
   - `fade_in_sec`
   - `fade_out_sec`
2. 若要支持多个混音版本，是否增加 `version_no` 或 `is_selected`
