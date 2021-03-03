"""add unique constraint on likes

Revision ID: 882e83e5abcf
Revises: 638254862657
Create Date: 2021-03-03 09:14:41.335063

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '882e83e5abcf'
down_revision = '638254862657'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'app_likes', ['user_id', 'message_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'app_likes', type_='unique')
    # ### end Alembic commands ###
