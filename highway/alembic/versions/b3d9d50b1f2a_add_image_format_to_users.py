"""add image_format column to users"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b3d9d50b1f2a"
down_revision: Union[str, Sequence[str], None] = "f9ddc695d680"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column("image_format", sa.Text(), nullable=False, server_default="vertical"),
    )
    op.alter_column("users", "image_format", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "image_format")
