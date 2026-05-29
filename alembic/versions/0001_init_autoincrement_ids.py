"""init schema with autoincrement ids

Revision ID: 0001_init_autoincrement_ids
Revises:
Create Date: 2026-05-29 18:40:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_init_autoincrement_ids"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "project",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("target_duration_sec", sa.Integer(), nullable=False),
        sa.Column("style_preset", sa.String(length=128), nullable=True),
        sa.Column("status", sa.Enum("CREATED", "RUNNING", "SUCCEEDED", "FAILED", name="project_status"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("name", name="uq_project_name"),
    )

    op.create_table(
        "character_profile",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("persona_text", sa.Text(), nullable=False),
        sa.Column("voice_style", sa.String(length=128), nullable=False),
        sa.Column("reference_image_paths", sa.JSON(), nullable=False),
        sa.Column("prompt_constraints", sa.JSON(), nullable=False),
        sa.Column("seed_policy", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
    )
    op.create_index("ix_character_profile_project_id", "character_profile", ["project_id"])

    op.create_table(
        "script_scene",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("scene_index", sa.Integer(), nullable=False),
        sa.Column("scene_text", sa.Text(), nullable=False),
        sa.Column("mood", sa.String(length=64), nullable=True),
        sa.Column("estimated_duration_sec", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
    )
    op.create_index("ix_script_scene_project_id", "script_scene", ["project_id"])

    op.create_table(
        "shot_plan",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("scene_id", sa.Integer(), nullable=False),
        sa.Column("shot_index", sa.Integer(), nullable=False),
        sa.Column("duration_sec", sa.Float(), nullable=False),
        sa.Column("characters", sa.JSON(), nullable=False),
        sa.Column("camera_instruction", sa.String(length=512), nullable=True),
        sa.Column("visual_prompt", sa.Text(), nullable=False),
        sa.Column("status", sa.Enum("PLANNED", "GENERATED", "SELECTED", "FAILED", name="shot_status"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
        sa.ForeignKeyConstraint(["scene_id"], ["script_scene.id"]),
    )
    op.create_index("ix_shot_plan_project_id", "shot_plan", ["project_id"])
    op.create_index("ix_shot_plan_scene_id", "shot_plan", ["scene_id"])

    op.create_table(
        "visual_asset",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("shot_id", sa.Integer(), nullable=False),
        sa.Column("asset_type", sa.Enum("IMAGE", "VIDEO", name="asset_type"), nullable=False),
        sa.Column("file_path", sa.String(length=512), nullable=False),
        sa.Column("provider", sa.String(length=128), nullable=False),
        sa.Column("prompt_used", sa.Text(), nullable=False),
        sa.Column("seed", sa.Integer(), nullable=True),
        sa.Column("consistency_score", sa.Float(), nullable=True),
        sa.Column("is_selected", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
        sa.ForeignKeyConstraint(["shot_id"], ["shot_plan.id"]),
    )
    op.create_index("ix_visual_asset_project_id", "visual_asset", ["project_id"])
    op.create_index("ix_visual_asset_shot_id", "visual_asset", ["shot_id"])

    op.create_table(
        "voice_asset",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("shot_id", sa.Integer(), nullable=False),
        sa.Column("character_id", sa.Integer(), nullable=False),
        sa.Column("line_text", sa.Text(), nullable=False),
        sa.Column("voice_provider", sa.String(length=128), nullable=False),
        sa.Column("audio_path", sa.String(length=512), nullable=False),
        sa.Column("start_time_sec", sa.Float(), nullable=False),
        sa.Column("end_time_sec", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["character_id"], ["character_profile.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
        sa.ForeignKeyConstraint(["shot_id"], ["shot_plan.id"]),
    )
    op.create_index("ix_voice_asset_character_id", "voice_asset", ["character_id"])
    op.create_index("ix_voice_asset_project_id", "voice_asset", ["project_id"])
    op.create_index("ix_voice_asset_shot_id", "voice_asset", ["shot_id"])

    op.create_table(
        "subtitle_segment",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("shot_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("start_time_sec", sa.Float(), nullable=False),
        sa.Column("end_time_sec", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
        sa.ForeignKeyConstraint(["shot_id"], ["shot_plan.id"]),
    )
    op.create_index("ix_subtitle_segment_project_id", "subtitle_segment", ["project_id"])
    op.create_index("ix_subtitle_segment_shot_id", "subtitle_segment", ["shot_id"])

    op.create_table(
        "bgm_asset",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("file_path", sa.String(length=512), nullable=False),
        sa.Column("mood_tag", sa.String(length=64), nullable=True),
        sa.Column("start_time_sec", sa.Float(), nullable=False),
        sa.Column("end_time_sec", sa.Float(), nullable=False),
        sa.Column("gain_db", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
    )
    op.create_index("ix_bgm_asset_project_id", "bgm_asset", ["project_id"])

    op.create_table(
        "render_task",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("stage", sa.String(length=128), nullable=False),
        sa.Column("status", sa.Enum("PENDING", "RUNNING", "SUCCEEDED", "FAILED", name="render_task_status"), nullable=False),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("error_code", sa.String(length=128), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
    )
    op.create_index("ix_render_task_project_id", "render_task", ["project_id"])

    op.create_table(
        "final_video",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("resolution", sa.String(length=32), nullable=False),
        sa.Column("duration_sec", sa.Float(), nullable=False),
        sa.Column("file_path", sa.String(length=512), nullable=False),
        sa.Column("cover_image_path", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
    )
    op.create_index("ix_final_video_project_id", "final_video", ["project_id"])

    op.create_table(
        "project_asset",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column(
            "asset_type",
            sa.Enum(
                "SCRIPT_FILE",
                "PERSONA_DOC",
                "CHARACTER_IMAGE",
                "STYLE_REFERENCE",
                name="project_asset_type",
            ),
            nullable=False,
        ),
        sa.Column("file_path", sa.String(length=512), nullable=False),
        sa.Column("original_name", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=128), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
    )


def downgrade() -> None:
    op.drop_table("project_asset")
    op.drop_index("ix_final_video_project_id", table_name="final_video")
    op.drop_table("final_video")
    op.drop_index("ix_render_task_project_id", table_name="render_task")
    op.drop_table("render_task")
    op.drop_index("ix_bgm_asset_project_id", table_name="bgm_asset")
    op.drop_table("bgm_asset")
    op.drop_index("ix_subtitle_segment_shot_id", table_name="subtitle_segment")
    op.drop_index("ix_subtitle_segment_project_id", table_name="subtitle_segment")
    op.drop_table("subtitle_segment")
    op.drop_index("ix_voice_asset_shot_id", table_name="voice_asset")
    op.drop_index("ix_voice_asset_project_id", table_name="voice_asset")
    op.drop_index("ix_voice_asset_character_id", table_name="voice_asset")
    op.drop_table("voice_asset")
    op.drop_index("ix_visual_asset_shot_id", table_name="visual_asset")
    op.drop_index("ix_visual_asset_project_id", table_name="visual_asset")
    op.drop_table("visual_asset")
    op.drop_index("ix_shot_plan_scene_id", table_name="shot_plan")
    op.drop_index("ix_shot_plan_project_id", table_name="shot_plan")
    op.drop_table("shot_plan")
    op.drop_index("ix_script_scene_project_id", table_name="script_scene")
    op.drop_table("script_scene")
    op.drop_index("ix_character_profile_project_id", table_name="character_profile")
    op.drop_table("character_profile")
    op.drop_table("project")
