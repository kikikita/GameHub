"""convert text fields to jsonb for i18n

Revision ID: 3c1b6f541aa5
Revises: 2a6ae631907c
Create Date: 2024-01-01 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3c1b6f541aa5'
down_revision: Union[str, Sequence[str], None] = '2a6ae631907c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'worlds',
        'title',
        type_=postgresql.JSONB(),
        existing_type=sa.Text(),
        existing_nullable=True,
        postgresql_using="jsonb_build_object('ru', title)",
    )
    op.alter_column(
        'worlds',
        'world_desc',
        type_=postgresql.JSONB(),
        existing_type=sa.Text(),
        existing_nullable=True,
        postgresql_using="jsonb_build_object('ru', world_desc)",
    )
    op.alter_column(
        'stories',
        'title',
        type_=postgresql.JSONB(),
        existing_type=sa.Text(),
        existing_nullable=True,
        postgresql_using="jsonb_build_object('ru', title)",
    )
    op.alter_column(
        'stories',
        'story_desc',
        type_=postgresql.JSONB(),
        existing_type=sa.Text(),
        existing_nullable=True,
        postgresql_using="jsonb_build_object('ru', story_desc)",
    )


def downgrade() -> None:
    op.alter_column(
        'stories',
        'story_desc',
        type_=sa.Text(),
        existing_type=postgresql.JSONB(),
        existing_nullable=True,
        postgresql_using="story_desc->>'ru'",
    )
    op.alter_column(
        'stories',
        'title',
        type_=sa.Text(),
        existing_type=postgresql.JSONB(),
        existing_nullable=True,
        postgresql_using="title->>'ru'",
    )
    op.alter_column(
        'worlds',
        'world_desc',
        type_=sa.Text(),
        existing_type=postgresql.JSONB(),
        existing_nullable=True,
        postgresql_using="world_desc->>'ru'",
    )
    op.alter_column(
        'worlds',
        'title',
        type_=sa.Text(),
        existing_type=postgresql.JSONB(),
        existing_nullable=True,
        postgresql_using="title->>'ru'",
    )
