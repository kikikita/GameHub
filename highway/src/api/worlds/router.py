"""Endpoints for worlds."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.tg_auth import authenticated_user
from src.api.utils import ensure_pro_plan, resolve_user_id, get_localized
from src.core.database import get_session
from src.config import settings
from src.utils.cache import AsyncTTLCache, cached, invalidate_prefix
from src.models.world import World
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/worlds", tags=["worlds"])

# In-process cache for worlds listings and individual world fetches
_worlds_cache: AsyncTTLCache | None = None


def _get_worlds_cache() -> AsyncTTLCache | None:
    global _worlds_cache
    if not settings.cache_enabled:
        return None
    if _worlds_cache is None:
        _worlds_cache = AsyncTTLCache(
            max_items=settings.cache_max_items,
            ttl_seconds=settings.worlds_cache_ttl_seconds,
        )
    return _worlds_cache


class WorldOut(BaseModel):
    id: uuid.UUID
    title: str | None = None
    world_desc: str | None = None
    image_url: str | None = None
    is_free: bool | None = None
    is_preset: bool | None = None


class WorldCreate(BaseModel):
    title: dict | None = None
    world_desc: dict | None = None
    image_url: str | None = None
    is_free: bool | None = None


@router.get("/", response_model=list[WorldOut])
@cached(_get_worlds_cache, include=["lang", "tg_id"], prefix="worlds:list")
async def list_worlds(
    lang: str = "ru",
    tg_id: int = Depends(authenticated_user),
    db: AsyncSession = Depends(get_session),
) -> list[WorldOut]:
    user_id = await resolve_user_id(tg_id, db)
    res = await db.execute(
        select(World).where(
            (World.is_preset.is_(True)) | (World.user_id == user_id)
        )
    )
    worlds = list(res.scalars())
    result = [
        WorldOut(
            id=w.id,
            title=get_localized(w.title, lang),
            world_desc=get_localized(w.world_desc, lang),
            image_url=w.image_url,
            is_free=w.is_free,
            is_preset=w.is_preset,
        )
        for w in worlds
    ]
    return result


@router.get("/{world_id}/", response_model=WorldOut)
@cached(_get_worlds_cache, include=["lang", "world_id"], prefix="worlds:get")
async def get_world(
    world_id: str, lang: str = "ru", db: AsyncSession = Depends(get_session)
) -> WorldOut:
    obj = await db.get(World, uuid.UUID(world_id))
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    result = WorldOut(
        id=obj.id,
        title=get_localized(obj.title, lang),
        world_desc=get_localized(obj.world_desc, lang),
        image_url=obj.image_url,
        is_free=obj.is_free,
        is_preset=obj.is_preset,
    )
    return result


@router.post("/", response_model=WorldOut, status_code=status.HTTP_201_CREATED)
async def create_world(
    payload: WorldCreate,
    tg_id: int = Depends(authenticated_user),
    db: AsyncSession = Depends(get_session),
    lang: str = "ru",
) -> WorldOut:
    user_id = await resolve_user_id(tg_id, db)
    await ensure_pro_plan(db, user_id)
    world = World(user_id=user_id, **payload.model_dump())
    db.add(world)
    await db.commit()
    await db.refresh(world)
    # Invalidate caches related to this user and worlds
    await invalidate_prefix(_get_worlds_cache, "worlds:")

    return WorldOut(
        id=world.id,
        title=get_localized(world.title, lang),
        world_desc=get_localized(world.world_desc, lang),
        image_url=world.image_url,
        is_free=world.is_free,
        is_preset=world.is_preset,
    )

