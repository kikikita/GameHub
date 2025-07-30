"""Endpoints for worlds."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.tg_auth import authenticated_user
from src.api.utils import resolve_user_id, ensure_pro_plan
from src.core.database import get_session
from src.models.world import World
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/worlds", tags=["worlds"])


class WorldOut(BaseModel):
    id: str
    title: str | None = None
    setting_desc: str | None = None
    genre: str | None = None
    image_url: str | None = None
    is_free: bool | None = None
    is_preset: bool | None = None

    class Config:
        from_attributes = True


class WorldCreate(BaseModel):
    title: str | None = None
    setting_desc: str | None = None
    genre: str | None = None
    image_url: str | None = None
    is_free: bool | None = None


@router.get("", response_model=list[WorldOut])
async def list_worlds(db: AsyncSession = Depends(get_session)) -> list[WorldOut]:
    res = await db.execute(select(World))
    worlds = list(res.scalars())
    return [WorldOut.from_orm(w) for w in worlds]


@router.get("/{world_id}", response_model=WorldOut)
async def get_world(world_id: str, db: AsyncSession = Depends(get_session)) -> WorldOut:
    obj = await db.get(World, uuid.UUID(world_id))
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return WorldOut.from_orm(obj)


@router.post("", response_model=WorldOut, status_code=status.HTTP_201_CREATED)
async def create_world(
    payload: WorldCreate,
    user_data: dict = Depends(authenticated_user),
    db: AsyncSession = Depends(get_session),
) -> WorldOut:
    user_id = await resolve_user_id(db, user_data)
    await ensure_pro_plan(db, user_id)
    world = World(user_id=user_id, **payload.model_dump())
    db.add(world)
    await db.commit()
    await db.refresh(world)
    return WorldOut.from_orm(world)

