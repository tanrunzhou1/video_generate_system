"""add shot_dialogue table

Revision ID: 0005_add_shot_dialogue_table
Revises: 0004_add_visual_asset_resolution
Create Date: 2026-06-18 20:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005_add_shot_dialogue_table"
down_revision: Union[str, Sequence[str], None] = "0004_add_visual_asset_resolution"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "shot_dialogue",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("shot_id", sa.Integer(), nullable=False),
        sa.Column("character_name", sa.String(length=128), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("sequence_no", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
        sa.ForeignKeyConstraint(["shot_id"], ["shot_plan.id"]),
    )
    op.create_index("ix_shot_dialogue_project_id", "shot_dialogue", ["project_id"])
    op.create_index("ix_shot_dialogue_shot_id", "shot_dialogue", ["shot_id"])


def downgrade() -> None:
    op.drop_index("ix_shot_dialogue_shot_id", table_name="shot_dialogue")
    op.drop_index("ix_shot_dialogue_project_id", table_name="shot_dialogue")
    op.drop_table("shot_dialogue")
