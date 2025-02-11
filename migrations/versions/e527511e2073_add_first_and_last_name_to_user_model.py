"""Add first and last name to User model

Revision ID: e527511e2073
Revises: 12cf5d92d668
Create Date: 2025-02-09 00:13:16.101813

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e527511e2073'
down_revision = '12cf5d92d668'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('first_name', sa.String(length=64), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('last_name', sa.String(length=64), nullable=False, server_default=''))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('last_name')
        batch_op.drop_column('first_name')

    # ### end Alembic commands ###
