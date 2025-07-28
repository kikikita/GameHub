"""add template extras

Revision ID: 760e50129cab
Revises: 1b77e27f91fb
Create Date: 2025-07-28 23:15:48.709659

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '760e50129cab'
down_revision: Union[str, Sequence[str], None] = '1b77e27f91fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("game_templates") as batch:
        batch.alter_column("user_id", existing_type=sa.Integer(), nullable=True)
        batch.add_column(sa.Column("title", sa.Text(), nullable=True))
        batch.add_column(sa.Column("story_frame", sa.dialects.postgresql.JSONB(), nullable=True))
        batch.add_column(
            sa.Column(
                "is_free",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            )
        )
        batch.add_column(
            sa.Column(
                "is_preset",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            )
        )

    with op.batch_alter_table("game_sessions") as batch:
        batch.add_column(sa.Column("story_frame", sa.dialects.postgresql.JSONB(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("game_sessions") as batch:
        batch.drop_column("story_frame")

    with op.batch_alter_table("game_templates") as batch:
        batch.drop_column("is_preset")
        batch.drop_column("is_free")
        batch.drop_column("story_frame")
        batch.drop_column("title")
        batch.alter_column("user_id", existing_type=sa.Integer(), nullable=False)
