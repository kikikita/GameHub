"""init

Revision ID: 1b77e27f91fb
Revises: 
Create Date: 2025-07-23 15:01:26.248258

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '1b77e27f91fb'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('tg_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.UniqueConstraint('tg_id'),
    )

    op.create_table(
        'game_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('setting_desc', sa.Text(), nullable=True),
        sa.Column('char_name', sa.Text(), nullable=True),
        sa.Column('char_age', sa.Text(), nullable=True),
        sa.Column('char_background', sa.Text(), nullable=True),
        sa.Column('char_personality', sa.Text(), nullable=True),
        sa.Column('genre', sa.Text(), nullable=True),
        sa.Column('is_public', sa.Boolean(), server_default=sa.text('false')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    )

    op.create_table(
        'game_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('game_templates.id'), nullable=True),
        sa.Column('started_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('ended_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('share_code', postgresql.UUID(as_uuid=True), nullable=False),
    )

    op.create_table(
        'scenes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('game_sessions.id'), nullable=False),
        sa.Column('order_num', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('generated_choices', postgresql.JSONB(), nullable=True),
        sa.Column('image_path', sa.Text(), nullable=True),
    )

    op.create_table(
        'choices',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('scene_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('scenes.id'), nullable=False),
        sa.Column('choice_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    )

    op.create_table(
        'subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('plan', sa.Text(), nullable=True),
        sa.Column('started_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('status', sa.Text(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('subscriptions')
    op.drop_table('choices')
    op.drop_table('scenes')
    op.drop_table('game_sessions')
    op.drop_table('game_templates')
    op.drop_table('users')
