"""rename expenses.amortize to is_need

Revision ID: 9c0cba826290
Revises: f4fb05b82465
Create Date: 2026-07-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c0cba826290'
down_revision: Union[str, None] = 'f4fb05b82465'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('expenses') as batch_op:
        batch_op.alter_column('amortize', new_column_name='is_need')


def downgrade() -> None:
    with op.batch_alter_table('expenses') as batch_op:
        batch_op.alter_column('is_need', new_column_name='amortize')
