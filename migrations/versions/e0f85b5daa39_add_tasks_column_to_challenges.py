"""add tasks column to challenges

Revision ID: e0f85b5daa39
Revises: fe272d4790cd
Create Date: 2026-01-01 03:52:27.890014

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e0f85b5daa39'
down_revision = 'fe272d4790cd'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('challenges') as batch_op:
        batch_op.add_column(
            sa.Column('tasks', sa.Text(), nullable=True)
        )


def downgrade():
    with op.batch_alter_table('challenges') as batch_op:
        batch_op.drop_column('tasks')
