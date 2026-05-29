"""project name unique

Revision ID: 5109f3f9f339
Revises: d01a5b71b879
Create Date: 2026-05-29 18:16:50.311295

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5109f3f9f339'
down_revision: Union[str, Sequence[str], None] = 'd01a5b71b879'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        WITH ranked AS (
            SELECT id, name,
                   ROW_NUMBER() OVER (PARTITION BY name ORDER BY created_at, id) AS rn
            FROM project
        )
        UPDATE project
        SET name = name || '_' || substr(id, 1, 6)
        WHERE id IN (SELECT id FROM ranked WHERE rn > 1);
        """
    )
    with op.batch_alter_table("project") as batch_op:
        batch_op.create_unique_constraint("uq_project_name", ["name"])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("project") as batch_op:
        batch_op.drop_constraint("uq_project_name", type_="unique")
