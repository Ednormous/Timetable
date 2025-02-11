"""Convert Tutor centre relationship to many-to-many

Revision ID: 12cf5d92d668
Revises: 04ac06a3b47a
Create Date: 2025-02-08 23:44:57.070732

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '12cf5d92d668'
down_revision = '04ac06a3b47a'
branch_labels = None
depends_on = None


def upgrade():
    # Skip creating the 'centre' table if it already exists.
    # op.create_table('centre',
    #     sa.Column('id', sa.Integer(), nullable=False),
    #     sa.Column('name', sa.String(length=64), nullable=False),
    #     sa.PrimaryKeyConstraint('id'),
    #     sa.UniqueConstraint('name')
    # )
    op.create_table('tutor_centres',
        sa.Column('tutor_id', sa.Integer(), nullable=False),
        sa.Column('centre_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['centre_id'], ['centre.id'], name='fk_tutor_centres_centre'),
        sa.ForeignKeyConstraint(['tutor_id'], ['tutor.id'], name='fk_tutor_centres_tutor'),
        sa.PrimaryKeyConstraint('tutor_id', 'centre_id')
    )
    with op.batch_alter_table('room', schema=None) as batch_op:
        batch_op.add_column(sa.Column('centre_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key('fk_room_centre', 'centre', ['centre_id'], ['id'])


def downgrade():
    with op.batch_alter_table('room', schema=None) as batch_op:
        batch_op.drop_constraint('fk_room_centre', type_='foreignkey')
        batch_op.drop_column('centre_id')
    op.drop_table('tutor_centres')
    # Skip dropping 'centre' table as it was not created in this migration.
