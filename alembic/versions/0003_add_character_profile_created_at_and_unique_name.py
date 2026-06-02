"""add character profile created_at and unique name per project

Revision ID: 0003_add_character_profile_created_at_and_unique_name
Revises: 0002_add_render_task_log_file_path
Create Date: 2026-06-02 18:20:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003_add_character_profile_created_at_and_unique_name"
down_revision: Union[str, Sequence[str], None] = "0002_add_render_task_log_file_path"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("character_profile") as batch_op:
        batch_op.add_column(
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            )
        )
        batch_op.create_unique_constraint(
            "uq_character_profile_project_name",
            ["project_id", "name"],
        )


def downgrade() -> None:
    with op.batch_alter_table("character_profile") as batch_op:
        batch_op.drop_constraint("uq_character_profile_project_name", type_="unique")
        batch_op.drop_column("created_at")
