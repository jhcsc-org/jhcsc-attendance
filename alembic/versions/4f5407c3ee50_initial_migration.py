"""Initial migration

Revision ID: 4f5407c3ee50
Revises: 3ab5bd17cd7d
Create Date: 2024-11-20 10:07:50.055598

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f5407c3ee50'
down_revision: Union[str, None] = '3ab5bd17cd7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
