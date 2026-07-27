"""multi payday sources and amortize expenses

Revision ID: f4fb05b82465
Revises: 2f2a8ced20c5
Create Date: 2026-07-27 00:00:00.000000

"""
from datetime import date, datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4fb05b82465'
down_revision: Union[str, None] = '2f2a8ced20c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'payday_sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('wallet_id', sa.Integer(), nullable=True),
        sa.Column('wallet_label', sa.String(length=50), nullable=True),
        sa.Column('label', sa.String(length=50), nullable=True),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('category', sa.String(length=20), nullable=False),
        sa.Column('recurrence', sa.String(length=20), nullable=False),
        sa.Column('next_date', sa.Date(), nullable=False),
        sa.Column('note', sa.String(length=140), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    connection = op.get_bind()
    users = connection.execute(
        sa.text(
            'SELECT id, next_payday, payday_amount, payday_wallet_id, payday_category, payday_note '
            'FROM users WHERE next_payday IS NOT NULL'
        )
    ).fetchall()

    payday_sources = sa.table(
        'payday_sources',
        sa.column('user_id', sa.Integer()),
        sa.column('wallet_id', sa.Integer()),
        sa.column('wallet_label', sa.String()),
        sa.column('label', sa.String()),
        sa.column('amount', sa.Numeric()),
        sa.column('category', sa.String()),
        sa.column('recurrence', sa.String()),
        sa.column('next_date', sa.Date()),
        sa.column('note', sa.String()),
        sa.column('created_at', sa.DateTime()),
    )
    for user in users:
        wallet_label = None
        if user.payday_wallet_id is not None:
            wallet_row = connection.execute(
                sa.text('SELECT label FROM wallets WHERE id = :id'), {'id': user.payday_wallet_id}
            ).fetchone()
            wallet_label = wallet_row.label if wallet_row else None

        next_date = user.next_payday
        if isinstance(next_date, str):
            next_date = date.fromisoformat(next_date)

        op.bulk_insert(
            payday_sources,
            [
                {
                    'user_id': user.id,
                    'wallet_id': user.payday_wallet_id,
                    'wallet_label': wallet_label,
                    'label': None,
                    'amount': user.payday_amount,
                    'category': user.payday_category or 'salary',
                    'recurrence': 'one_time',
                    'next_date': next_date,
                    'note': user.payday_note,
                    'created_at': datetime.utcnow(),
                }
            ],
        )

    bind = op.get_bind()
    with op.batch_alter_table('users') as batch_op:
        if bind.dialect.name == 'postgresql':
            batch_op.drop_constraint('fk_users_payday_wallet_id_wallets', type_='foreignkey')
        batch_op.drop_column('next_payday')
        batch_op.drop_column('payday_amount')
        batch_op.drop_column('payday_wallet_id')
        batch_op.drop_column('payday_category')
        batch_op.drop_column('payday_note')

    with op.batch_alter_table('expenses') as batch_op:
        batch_op.add_column(sa.Column('amortize', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    with op.batch_alter_table('expenses') as batch_op:
        batch_op.drop_column('amortize')

    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('next_payday', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('payday_amount', sa.Numeric(precision=12, scale=2), nullable=True))
        batch_op.add_column(sa.Column('payday_wallet_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('payday_category', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('payday_note', sa.String(length=140), nullable=True))

    with op.batch_alter_table('users') as batch_op:
        batch_op.create_foreign_key(
            'fk_users_payday_wallet_id_wallets', 'wallets', ['payday_wallet_id'], ['id']
        )

    connection = op.get_bind()
    sources = connection.execute(
        sa.text(
            'SELECT user_id, MIN(next_date) as next_date FROM payday_sources GROUP BY user_id'
        )
    ).fetchall()
    for row in sources:
        source = connection.execute(
            sa.text(
                'SELECT amount, wallet_id, category, note FROM payday_sources '
                'WHERE user_id = :user_id AND next_date = :next_date LIMIT 1'
            ),
            {'user_id': row.user_id, 'next_date': row.next_date},
        ).fetchone()
        connection.execute(
            sa.text(
                'UPDATE users SET next_payday = :next_date, payday_amount = :amount, '
                'payday_wallet_id = :wallet_id, payday_category = :category, payday_note = :note '
                'WHERE id = :user_id'
            ),
            {
                'next_date': row.next_date,
                'amount': source.amount if source else None,
                'wallet_id': source.wallet_id if source else None,
                'category': source.category if source else None,
                'note': source.note if source else None,
                'user_id': row.user_id,
            },
        )

    op.drop_table('payday_sources')
