"""add render task log file path

Revision ID: 0002_add_render_task_log_file_path
Revises: 0001_init_autoincrement_ids
Create Date: 2026-06-02 15:55:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_add_render_task_log_file_path"
down_revision: Union[str, Sequence[str], None] = "0001_init_autoincrement_ids"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("render_task") as batch_op:
        batch_op.add_column(sa.Column("log_file_path", sa.String(length=512), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("render_task") as batch_op:
        batch_op.drop_column("log_file_path")
