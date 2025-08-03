"""add energy and wishes columns to users"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "1b2c3d4e5f6a"
down_revision: Union[str, Sequence[str], None] = '3c1b6f541aa5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column("energy", sa.Integer(), nullable=False, server_default="50"),
    )
    op.add_column(
        "users",
        sa.Column("wishes", sa.Integer(), nullable=False, server_default="0"),
    )
    op.alter_column("users", "energy", server_default=None)
    op.alter_column("users", "wishes", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "wishes")
    op.drop_column("users", "energy")

