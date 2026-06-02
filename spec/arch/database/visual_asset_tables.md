# 视觉素材表说明（Visual Asset MVP）

## 1. 范围

本文档细化 PRD 2.4 模块在 MVP 阶段的视觉素材数据结构，重点覆盖 `qwen-image-2.0` 图片生成与镜头级查询场景。

## 2. 主表：`visual_asset`

- 主键：`id`（int，自增）
- 外键：
  - `project_id -> project.id`
  - `shot_id -> shot_plan.id`

### 字段说明

- `asset_type`：素材类型，MVP 固定为 `image`
- `file_path`：图片文件本地路径
- `provider`：生成服务提供方，MVP 固定为 `qwen-image-2.0`
- `prompt_used`：最终实际用于生成的提示词
- `seed`：生成时使用的随机种子，可为空
- `consistency_score`：角色一致性评分，MVP 阶段可为空
- `is_selected`：是否被人工或系统标记为最终选中素材

## 3. 分辨率说明

当前 `visual_asset` 已增加 `resolution` 字段，用于持久化记录生成时使用的分辨率档位。

MVP 阶段支持的档位：

1. `360p`
2. `480p`
3. `720p`
4. `1080p`

## 4. 与分镜和角色的关系

- `shot_plan.visual_prompt` 是基础提示词输入
- `shot_plan.characters` 提供当前镜头角色名称列表
- `character_profile` 提供角色人设、提示词约束和 seed 策略
- 视觉生成阶段应将这些信息拼装为最终 `prompt_used`

## 5. MVP 约束

1. 每次仅为 1 个镜头生成 1 张图片
2. 先不做多候选 Top-K
3. 先不做失败重试与自动降级
4. 先支持本地文件保存和数据库落库
5. 先固定接入 `qwen-image-2.0`

## 6. 后续演进

1. 为 `visual_asset` 增加 `resolution` 持久化字段
2. 增加人工选中与筛选能力
3. 增加角色一致性评分写回
