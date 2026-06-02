"""add visual asset resolution

Revision ID: 0004_add_visual_asset_resolution
Revises: 0003_add_character_profile_created_at_and_unique_name
Create Date: 2026-06-02 20:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004_add_visual_asset_resolution"
down_revision: Union[str, Sequence[str], None] = "0003_add_character_profile_created_at_and_unique_name"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("visual_asset") as batch_op:
        batch_op.add_column(sa.Column("resolution", sa.String(length=32), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("visual_asset") as batch_op:
        batch_op.drop_column("resolution")
