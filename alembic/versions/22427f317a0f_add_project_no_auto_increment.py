"""add project_no auto increment

Revision ID: 22427f317a0f
Revises: 5109f3f9f339
Create Date: 2026-05-29 18:21:25.549883

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '22427f317a0f'
down_revision: Union[str, Sequence[str], None] = '5109f3f9f339'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('project', sa.Column('project_no', sa.Integer(), nullable=True))
    op.execute(
        """
        WITH ranked AS (
            SELECT id, ROW_NUMBER() OVER (ORDER BY created_at, id) AS rn
            FROM project
        )
        UPDATE project
        SET project_no = (SELECT rn FROM ranked WHERE ranked.id = project.id)
        WHERE project_no IS NULL;
        """
    )
    with op.batch_alter_table("project") as batch_op:
        batch_op.create_unique_constraint("uq_project_project_no", ["project_no"])
    op.execute(
        """
        CREATE TRIGGER IF NOT EXISTS trg_project_project_no_autoinc
        AFTER INSERT ON project
        FOR EACH ROW
        WHEN NEW.project_no IS NULL
        BEGIN
          UPDATE project
          SET project_no = (
            SELECT COALESCE(MAX(project_no), 0) + 1 FROM project
          )
          WHERE id = NEW.id;
        END;
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS trg_project_project_no_autoinc;")
    with op.batch_alter_table("project") as batch_op:
        batch_op.drop_constraint("uq_project_project_no", type_="unique")
    op.drop_column('project', 'project_no')
