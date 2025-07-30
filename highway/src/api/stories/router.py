"""Endpoints for stories and preset import."""

import uuid
import json

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.tg_auth import authenticated_user
from src.api.utils import ensure_admin
from src.core.database import get_session
from src.models.story import Story
from src.models.world import World
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["stories"])


class StoryOut(BaseModel):
    id: str
    world_id: str
    title: str | None = None
    character: dict | None = None
    story_frame: dict | None = None
    is_public: bool | None = None
    is_free: bool | None = None
    is_preset: bool | None = None

    class Config:
        from_attributes = True


@router.get("/worlds/{world_id}/stories", response_model=list[StoryOut])
async def list_stories(world_id: str, db: AsyncSession = Depends(get_session)) -> list[StoryOut]:
    res = await db.execute(
        select(Story).where(Story.world_id == uuid.UUID(world_id))
    )
    stories = list(res.scalars())
    return [StoryOut.from_orm(s) for s in stories]


@router.get("/stories/{story_id}", response_model=StoryOut)
async def get_story(story_id: str, db: AsyncSession = Depends(get_session)) -> StoryOut:
    obj = await db.get(Story, uuid.UUID(story_id))
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return StoryOut.from_orm(obj)


async def _import_presets(db: AsyncSession, data: dict) -> None:
    if not isinstance(data, dict) or "worlds" not in data:
        raise ValueError("invalid structure")
    for w in data["worlds"]:
        world = World(
            title=w.get("title"),
            setting_desc=w.get("setting_desc"),
            genre=w.get("genre"),
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
                character=s.get("character"),
                story_frame=s.get("story_frame"),
                is_public=s.get("is_public", False),
                is_free=s.get("is_free", False),
                is_preset=True,
                user_id=s.get("user_id"),
            )
            db.add(story)
    await db.commit()


@router.post("/presets/upload", status_code=status.HTTP_201_CREATED)
async def upload_presets(
    file: UploadFile,
    user_data: dict = Depends(authenticated_user),
    db: AsyncSession = Depends(get_session),
) -> None:
    ensure_admin(user_data)
    content = await file.read()
    data = json.loads(content.decode())
    await _import_presets(db, data)
