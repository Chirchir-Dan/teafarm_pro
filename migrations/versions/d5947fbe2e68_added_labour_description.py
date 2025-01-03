"""added labour description

Revision ID: d5947fbe2e68
Revises: 
Create Date: 2024-12-30 21:29:46.965774

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5947fbe2e68'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('labours', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.String(length=128), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('labours', schema=None) as batch_op:
        batch_op.drop_column('description')

    # ### end Alembic commands ###
