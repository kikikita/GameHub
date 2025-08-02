"""Scene generation and retrieval endpoints."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.tg_auth import authenticated_user
from src.core.database import get_session
from src.models.scene import Scene
from src.models.game_session import GameSession
from src.models.story import Story
from src.models.user import User
from .schemas import SceneCreate, SceneOut, scene_to_out
from .scene_service import create_and_store_scene
from src.api.utils import resolve_user_id

router = APIRouter(prefix="/api/v1/sessions", tags=["scenes"])


@router.post(
    "/{id}/scenes/",
    response_model=SceneOut,
    status_code=status.HTTP_201_CREATED,
)
async def generate_scene(
    id: str,
    payload: SceneCreate,
    tg_id: int = Depends(authenticated_user),
    db: AsyncSession = Depends(get_session),
) -> SceneOut:
    """Generate the next scene for a session."""
    user_id = await resolve_user_id(tg_id, db)
    sid = uuid.UUID(id)
    res = await db.get(GameSession, sid)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if res.user_id != user_id :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    story = None
    if res.story_id:
        story = await db.get(Story, res.story_id)
        if story:
            await db.refresh(story, ["world"])
    scene = await create_and_store_scene(
        db,
        res,
        payload.choice_text if payload else None,
        story,
    )
    return scene_to_out(scene)


@router.post(
    "/{id}/choice/",
    response_model=SceneOut,
    status_code=status.HTTP_201_CREATED,
)
async def choose_and_generate(
    id: str,
    payload: SceneCreate,
    tg_id: int = Depends(authenticated_user),
    db: AsyncSession = Depends(get_session),
) -> SceneOut:
    """Generate the next scene using the chosen option."""
    user_id = await resolve_user_id(tg_id, db)
    user = await db.get(User, user_id)
    cost = payload.energy_cost or 1
    if not user or user.energy < cost:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="not_enough_energy")
    user.energy -= cost
    await db.commit()
    await db.refresh(user)
    payload_dict = payload.model_dump()
    payload_dict.pop("energy_cost", None)
    return await generate_scene(id, SceneCreate(**payload_dict), tg_id, db)


@router.get("/{id}/scenes/{scene_id}/", response_model=SceneOut)
async def get_scene(
    id: str,
    scene_id: str,
    tg_id: int = Depends(authenticated_user),
    db: AsyncSession = Depends(get_session),
) -> SceneOut:
    """Retrieve a specific scene for a session."""

    scene = await db.get(Scene, uuid.UUID(scene_id))
    if not scene or str(scene.session_id) != id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return scene_to_out(scene)


@router.get("/{id}/history/", response_model=list[SceneOut])
async def history(
    id: str,
    tg_id: int = Depends(authenticated_user),
    db: AsyncSession = Depends(get_session),
) -> list[SceneOut]:
    """Return the full scene history for a session."""

    res = await db.execute(
        select(Scene)
        .where(Scene.session_id == uuid.UUID(id))
        .order_by(Scene.order_num)
    )
    scenes = list(res.scalars())
    return [scene_to_out(s) for s in scenes]


@router.put("/{id}/scenes/{scene_id}/", response_model=SceneOut)
async def update_scene(
    id: str,
    scene_id: str,
    payload: SceneOut,
    tg_id: int = Depends(authenticated_user),
    db: AsyncSession = Depends(get_session),
) -> SceneOut:
    """Persist edits to an existing scene."""

    scene = await db.get(Scene, uuid.UUID(scene_id))
    if not scene or str(scene.session_id) != id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    scene.description = payload.description
    # Update only if provided (legacy clients may still send image_url)
    if payload.image_url:
        scene.image_path = payload.image_url
    scene.generated_choices = payload.choices_json
    await db.commit()
    await db.refresh(scene)
    return scene_to_out(scene)

