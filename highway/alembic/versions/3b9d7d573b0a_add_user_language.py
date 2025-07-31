"""add user language field

Revision ID: 3b9d7d573b0a
Revises: df5e3b8d1a2c
Create Date: 2025-08-01 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '3b9d7d573b0a'
down_revision: Union[str, Sequence[str], None] = 'df5e3b8d1a2c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('users') as batch:
        batch.add_column(sa.Column('language', sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('users') as batch:
        batch.drop_column('language')

