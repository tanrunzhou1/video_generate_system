"""add audio_mix_asset table

Revision ID: 0006_add_audio_mix_asset_table
Revises: 0005_add_shot_dialogue_table
Create Date: 2026-06-18 20:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0006_add_audio_mix_asset_table"
down_revision: str | None = "0005_add_shot_dialogue_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "audio_mix_asset",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("shot_id", sa.Integer(), nullable=False),
        sa.Column("bgm_asset_id", sa.Integer(), nullable=False),
        sa.Column("mixed_audio_path", sa.String(length=512), nullable=False),
        sa.Column("ducking_gain_db", sa.Float(), nullable=False),
        sa.Column("fade_in_sec", sa.Float(), nullable=False),
        sa.Column("fade_out_sec", sa.Float(), nullable=False),
        sa.Column("is_selected", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["bgm_asset_id"], ["bgm_asset.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
        sa.ForeignKeyConstraint(["shot_id"], ["shot_plan.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audio_mix_asset_project_id"), "audio_mix_asset", ["project_id"], unique=False)
    op.create_index(op.f("ix_audio_mix_asset_shot_id"), "audio_mix_asset", ["shot_id"], unique=False)
    op.create_index(op.f("ix_audio_mix_asset_bgm_asset_id"), "audio_mix_asset", ["bgm_asset_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_audio_mix_asset_bgm_asset_id"), table_name="audio_mix_asset")
    op.drop_index(op.f("ix_audio_mix_asset_shot_id"), table_name="audio_mix_asset")
    op.drop_index(op.f("ix_audio_mix_asset_project_id"), table_name="audio_mix_asset")
    op.drop_table("audio_mix_asset")
