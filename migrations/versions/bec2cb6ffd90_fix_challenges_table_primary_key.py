"""Fix challenges table primary key

Revision ID: bec2cb6ffd90
Revises: dd27edcdc312
Create Date: 2025-12-29 18:12:58.044307
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bec2cb6ffd90'
down_revision = 'dd27edcdc312'
branch_labels = None
depends_on = None


def upgrade():
    # SQLite에서는 FK constraint 이름이 명시적으로 존재하지 않는 경우가 많아
    # drop_constraint 자체를 제거하고 컬럼 삭제만 수행한다.
    with op.batch_alter_table('challenges', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('challenge_id', sa.String(length=50), nullable=True)
        )
        batch_op.add_column(
            sa.Column('tags', sa.String(length=255), nullable=True)
        )
        batch_op.alter_column(
            'title',
            existing_type=sa.VARCHAR(length=100),
            type_=sa.String(length=255),
            existing_nullable=False
        )
        batch_op.alter_column(
            'difficulty',
            existing_type=sa.VARCHAR(length=20),
            type_=sa.String(length=50),
            existing_nullable=False
        )
        # ❌ drop_constraint 제거 (SQLite에서 오류 원인)
        batch_op.drop_column('category_id')


def downgrade():
    with op.batch_alter_table('challenges', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('category_id', sa.INTEGER(), nullable=False)
        )
        batch_op.create_foreign_key(
            'challenges_category_id_fkey',
            'categories',
            ['category_id'],
            ['id']
        )
        batch_op.alter_column(
            'difficulty',
            existing_type=sa.String(length=50),
            type_=sa.VARCHAR(length=20),
            existing_nullable=False
        )
        batch_op.alter_column(
            'title',
            existing_type=sa.String(length=255),
            type_=sa.VARCHAR(length=100),
            existing_nullable=False
        )
        batch_op.drop_column('tags')
        batch_op.drop_column('challenge_id')
