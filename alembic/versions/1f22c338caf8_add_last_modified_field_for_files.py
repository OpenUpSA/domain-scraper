"""Add last modified field for files

Revision ID: 1f22c338caf8
Revises: c32038686f51
Create Date: 2022-08-12 06:01:54.446902

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f22c338caf8'
down_revision = 'c32038686f51'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('file_observation', sa.Column('last_modified', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('file_observation', 'last_modified')
    # ### end Alembic commands ###
