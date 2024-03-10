"""Add UserRole

Revision ID: de520cb6226d
Revises: 002f556d1251
Create Date: 2024-03-10 18:41:27.415491

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de520cb6226d'
down_revision: Union[str, None] = '002f556d1251'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('role', sa.Enum('BACKOFFICER', 'USER', name='userrole', native_enum=False), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'role')
    # ### end Alembic commands ###