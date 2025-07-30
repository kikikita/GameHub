"""Endpoints for worlds."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
