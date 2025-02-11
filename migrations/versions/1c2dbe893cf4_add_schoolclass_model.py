"""Add SchoolClass model

Revision ID: 1c2dbe893cf4
Revises: 72bf574f4c21
Create Date: 2025-02-09 00:53:07.918516

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1c2dbe893cf4'
down_revision = '72bf574f4c21'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('school_class',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name_key', sa.String(length=64), nullable=False),
    sa.Column('full_name', sa.String(length=128), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name_key')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('school_class')
    # ### end Alembic commands ###
