"""Add student_number and student_names to Session

Revision ID: 72bf574f4c21
Revises: e527511e2073
Create Date: 2025-02-09 00:44:01.968581

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '72bf574f4c21'
down_revision = 'e527511e2073'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('session', schema=None) as batch_op:
        batch_op.add_column(sa.Column('student_number', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('student_names', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('session', schema=None) as batch_op:
        batch_op.drop_column('student_names')
        batch_op.drop_column('student_number')

    # ### end Alembic commands ###
