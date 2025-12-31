"""Fix foreign key relationship between Category and Challenge

Revision ID: c390de4c0fc7
Revises: bec2cb6ffd90
Create Date: 2025-12-29 18:16:20.044365
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c390de4c0fc7'
down_revision = 'bec2cb6ffd90'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('challenges', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('category_id', sa.Integer(), nullable=False)
        )
        #  FK 이름 반드시 명시 (SQLite 필수)
        batch_op.create_foreign_key(
            'challenges_category_id_fkey',
            'categories',
            ['category_id'],
            ['id']
        )
        batch_op.drop_column('challenge_id')


def downgrade():
    with op.batch_alter_table('challenges', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('challenge_id', sa.VARCHAR(length=50), nullable=True)
        )
        # SQLite에서는 drop_constraint가 불안정하므로 생략
        batch_op.drop_column('category_id')
