"""Endpoints for stories and preset import."""

import uuid
import json

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.tg_auth import authenticated_user
from src.api.utils import ensure_admin, resolve_user_id, get_localized
from src.core.database import get_session
from src.models.story import Story
from src.models.world import World
from src.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["stories"])


class StoryOut(BaseModel):
    id: uuid.UUID
    world_id: uuid.UUID
    title: str | None = None
    story_desc: str | None = None
    genre: str | None = None
    character: dict | None = None
    story_frame: dict | None = None
    is_public: bool | None = None
    is_free: bool | None = None
    is_preset: bool | None = None


class StoryCreate(BaseModel):
    title: dict | None = None
    story_desc: dict | None = None
    genre: str | None = None
    character: dict | None = None
    story_frame: dict | None = None
    is_public: bool | None = None
    is_free: bool | None = None


def story_to_out(story: Story, lang: str) -> StoryOut:
    return StoryOut(
        id=story.id,
        world_id=story.world_id,
        title=get_localized(story.title, lang),
        story_desc=get_localized(story.story_desc, lang),
        genre=story.genre,
        character=get_localized(story.character, lang),
        story_frame=get_localized(story.story_frame, lang),
        is_public=story.is_public,
        is_free=story.is_free,
        is_preset=story.is_preset,
    )


@router.get("/worlds/{world_id}/stories/", response_model=list[StoryOut])
async def list_stories(
    world_id: str, lang: str = "ru", db: AsyncSession = Depends(get_session)
) -> list[StoryOut]:
    res = await db.execute(
        select(Story).where(Story.world_id == uuid.UUID(world_id))
    )
    stories = list(res.scalars())
    return [story_to_out(s, lang) for s in stories]


@router.get("/stories/preset/", response_model=list[StoryOut])
async def list_preset_stories(
    lang: str = "ru", db: AsyncSession = Depends(get_session)
) -> list[StoryOut]:
    res = await db.execute(
        select(Story).where(Story.is_preset.is_(True), Story.is_free.is_(True))
    )
    stories = list(res.scalars())
    return [story_to_out(s, lang) for s in stories]


@router.get("/stories/{story_id}/", response_model=StoryOut)
async def get_story(
    story_id: str, lang: str = "ru", db: AsyncSession = Depends(get_session)
) -> StoryOut:
    obj = await db.get(Story, uuid.UUID(story_id))
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return story_to_out(obj, lang)


@router.post("/stories/", response_model=StoryOut, status_code=status.HTTP_201_CREATED)
async def create_story(
    payload: StoryCreate,
    tg_id: int = Depends(authenticated_user),
    db: AsyncSession = Depends(get_session),
    lang: str = "ru",
) -> StoryOut:
    user_id = await resolve_user_id(tg_id, db)
    user = await db.get(User, user_id)
    cost = 5
    if not user or user.wishes < cost:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="not_enough_wishes")
    user.wishes -= cost
    res = await db.execute(select(World).where(World.user_id == user_id))
    world = res.scalars().first()
    if not world:
        world = World(
            user_id=user_id,
            title=payload.title,
            world_desc=payload.story_desc,
        )
        db.add(world)
        await db.flush()
    story = Story(world_id=world.id, user_id=user_id, **payload.model_dump())
    db.add(story)
    await db.commit()
    await db.refresh(story)
    return story_to_out(story, lang)


async def _import_presets(db: AsyncSession, data: dict) -> None:
    if not isinstance(data, dict) or "worlds" not in data:
        raise ValueError("invalid structure")
    for w in data["worlds"]:
        world = World(
            title=w.get("title"),
            world_desc=w.get("world_desc"),
            image_url=w.get("image_url"),
            is_free=w.get("is_free", False),
            is_preset=True,
            user_id=w.get("user_id"),
        )
        db.add(world)
        await db.flush()
        for s in w.get("stories", []):
            story = Story(
                world_id=world.id,
                title=s.get("title"),
                story_desc=s.get("story_desc"),
                genre=s.get("genre"),
                character=s.get("character"),
                story_frame=s.get("story_frame"),
                is_public=s.get("is_public", False),
                is_free=s.get("is_free", False),
                is_preset=True,
                user_id=s.get("user_id"),
            )
            db.add(story)
    await db.commit()


@router.post("/presets/upload/", status_code=status.HTTP_201_CREATED)
async def upload_presets(
    file: UploadFile,
    tg_id: int = Depends(authenticated_user),
    db: AsyncSession = Depends(get_session),
) -> None:
    ensure_admin(tg_id)
    content = await file.read()
    data = json.loads(content.decode())
    await _import_presets(db, data)

