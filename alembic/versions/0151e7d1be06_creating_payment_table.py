"""Creating Payment Table

Revision ID: 0151e7d1be06
Revises: 799c54acba97
Create Date: 2023-12-18 13:25:49.187645

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import rules_system.types as rs


# revision identifiers, used by Alembic.
revision: str = '0151e7d1be06'
down_revision: Union[str, None] = '799c54acba97'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'payment',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('data', rs.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('payment')
    # ### end Alembic commands ###