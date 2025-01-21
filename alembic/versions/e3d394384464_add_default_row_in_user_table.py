"""add default row in user table

Revision ID: e3d394384464
Revises: 27812c761e4e
Create Date: 2025-01-20 17:51:49.476503

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3d394384464'
down_revision: Union[str, None] = '27812c761e4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(
        """
        INSERT INTO users (name, email, age)
        VALUES ('admin', 'admin@gmail.com', '24');
        """
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
        op.execute(
        """
        delete from users where name='admin' and email = 'admin@gmail.com' and age = '24';
        """
    )
    # ### end Alembic commands ###
