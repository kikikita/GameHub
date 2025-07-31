"""rename setting_desc and add story fields"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'df5e3b8d1a2c'
down_revision: Union[str, Sequence[str], None] = 'b1c2d3e4f5ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('worlds') as batch:
        batch.alter_column('setting_desc', new_column_name='world_desc')
        batch.drop_column('genre')
    with op.batch_alter_table('stories') as batch:
        batch.add_column(sa.Column('story_desc', sa.Text(), nullable=True))
        batch.add_column(sa.Column('genre', sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('stories') as batch:
        batch.drop_column('genre')
        batch.drop_column('story_desc')
    with op.batch_alter_table('worlds') as batch:
        batch.add_column(sa.Column('genre', sa.Text(), nullable=True))
        batch.alter_column('world_desc', new_column_name='setting_desc')
