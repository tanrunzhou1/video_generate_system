# 角色档案表说明（Character Profile MVP）

## 1. 范围

本文档细化 PRD 2.3 模块在 MVP 阶段依赖的角色档案数据结构，重点覆盖角色资产库与后续视觉生成所需约束字段。

## 2. 主表：`character_profile`

- 主键：`id`（int，自增）
- 外键：`project_id -> project.id`

### 字段说明

- `name`：角色名称，同一项目内建议唯一
- `persona_text`：角色人设描述，用于提示词扩展与配音风格映射
- `voice_style`：角色音色风格标识
- `reference_image_paths`：角色参考图路径数组，来源于 `project_asset` 中的 `character_image`
- `prompt_constraints`：提示词约束 JSON，MVP 建议包含：
  - `positive`
  - `negative`
  - `style`
- `seed_policy`：随机种子策略 JSON，MVP 建议包含：
  - `mode`
  - `seed`
- `created_at`：角色档案创建时间，用于列表排序与前端展示

## 3. 与素材表的关系

- `character_profile` 不直接存素材 ID，只保存最终可用的 `reference_image_paths`
- 创建角色档案时，应校验参考图素材来自当前项目，且 `asset_type=character_image`
- 原始素材元信息继续保留在 `project_asset`

## 4. 与分镜表的关系

- `shot_plan.characters` 当前保存角色名称数组
- 后续视觉生成时，通过角色名称匹配 `character_profile.name`
- NEED_VERIFY：后续是否需要把 `shot_plan.characters` 升级为角色 ID 数组或“名称 + ID”混合结构

## 5. MVP 约束

1. 先支持角色档案的创建、列表和详情查询
2. 先不做 CLIP embedding、FAISS 索引和相似度持久化
3. 先不做角色图片裁剪、人脸校验和自动标签提取
4. 同一项目内角色名必须唯一

## 6. 后续演进

1. 新增角色约束编辑与版本管理
2. 新增角色 embedding 存储表或向量索引映射
3. 增加角色一致性检测结果与自动重试记录
