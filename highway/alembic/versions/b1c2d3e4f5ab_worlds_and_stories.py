"""add worlds and stories tables and migrate sessions"""

from typing import Sequence, Union
import uuid
import json

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5ab'
down_revision: Union[str, Sequence[str], None] = '760e50129cab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'worlds',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('setting_desc', sa.Text(), nullable=True),
        sa.Column('genre', sa.Text(), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=True),
        sa.Column('is_free', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('is_preset', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    )

    op.create_table(
        'stories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('world_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('worlds.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('character', postgresql.JSONB(), nullable=True),
        sa.Column('story_frame', postgresql.JSONB(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('is_free', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('is_preset', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    )

    with op.batch_alter_table('game_sessions') as batch:
        batch.add_column(sa.Column('story_id', postgresql.UUID(as_uuid=True), nullable=True))
        batch.add_column(sa.Column('is_finished', sa.Boolean(), nullable=False, server_default=sa.text('false')))

    conn = op.get_bind()
    res = conn.execute(sa.text('SELECT * FROM game_templates'))
    templates = res.fetchall()
    for t in templates:
        world_id = uuid.uuid4()
        conn.execute(sa.text(
            "INSERT INTO worlds (id, user_id, title, setting_desc, genre, is_free, is_preset, created_at) "
            "VALUES (:id, :user_id, :title, :setting_desc, :genre, :is_free, :is_preset, :created_at)"
        ), dict(id=world_id, user_id=t.user_id, title=t.title, setting_desc=t.setting_desc,
                 genre=t.genre, is_free=t.is_free or False, is_preset=t.is_preset or False,
                 created_at=t.created_at))
        story_id = uuid.uuid4()
        character = json.dumps({
            'name': t.char_name,
            'age': t.char_age,
            'background': t.char_background,
            'personality': t.char_personality,
        })
        conn.execute(sa.text(
            "INSERT INTO stories (id, world_id, user_id, title, character, story_frame, is_public, is_free, is_preset, created_at) "
            "VALUES (:id, :world_id, :user_id, :title, :character::jsonb, :story_frame::jsonb, :is_public, :is_free, :is_preset, :created_at)"
        ), dict(id=story_id, world_id=world_id, user_id=t.user_id, title=t.title,
                 character=character, story_frame=json.dumps(t.story_frame) if t.story_frame else None,
                 is_public=t.is_public or False, is_free=t.is_free or False, is_preset=t.is_preset or False,
                 created_at=t.created_at))
        conn.execute(sa.text(
            "UPDATE game_sessions SET story_id=:sid WHERE template_id=:tid"
        ), dict(sid=story_id, tid=t.id))

    with op.batch_alter_table('game_sessions') as batch:
        batch.drop_column('template_id')

    op.drop_table('game_templates')


def downgrade() -> None:
    op.create_table(
        'game_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('story_frame', postgresql.JSONB(), nullable=True),
        sa.Column('is_free', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('is_preset', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('setting_desc', sa.Text(), nullable=True),
        sa.Column('char_name', sa.Text(), nullable=True),
        sa.Column('char_age', sa.Text(), nullable=True),
        sa.Column('char_background', sa.Text(), nullable=True),
        sa.Column('char_personality', sa.Text(), nullable=True),
        sa.Column('genre', sa.Text(), nullable=True),
        sa.Column('is_public', sa.Boolean(), server_default=sa.text('false')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    )
    with op.batch_alter_table('game_sessions') as batch:
        batch.add_column(sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=True))
        batch.drop_column('story_id')
        batch.drop_column('is_finished')

    op.drop_table('stories')
    op.drop_table('worlds')
