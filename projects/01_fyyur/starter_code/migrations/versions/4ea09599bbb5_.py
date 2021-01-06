"""empty message

Revision ID: 4ea09599bbb5
Revises: 828df2d040c1
Create Date: 2020-12-23 13:41:08.501931

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4ea09599bbb5'
down_revision = '828df2d040c1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artist', 'seeking_description')
    op.drop_column('artist', 'address')
    op.drop_column('artist', 'website')
    op.drop_column('artist', 'seeking_talent')
    op.add_column('venue', sa.Column('seeking_description', sa.String(length=120), nullable=True))
    op.add_column('venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('venue', sa.Column('website', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'website')
    op.drop_column('venue', 'seeking_talent')
    op.drop_column('venue', 'seeking_description')
    op.add_column('artist', sa.Column('seeking_talent', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('artist', sa.Column('website', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column('artist', sa.Column('address', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column('artist', sa.Column('seeking_description', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
