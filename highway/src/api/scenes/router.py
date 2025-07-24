from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.tg_auth import authenticated_user
from src.core.database import get_session
from src.models.scene import Scene
from src.models.game_session import GameSession
from .schemas import SceneCreate, SceneOut
from .scene_service import create_and_store_scene
import json
import uuid

router = APIRouter(prefix="/api/v1/sessions", tags=["scenes"])


@router.post("/{id}/scenes", response_model=SceneOut, status_code=status.HTTP_201_CREATED)
async def generate_scene(id: str, payload: SceneCreate | None = None, user_data: dict = Depends(authenticated_user), db: AsyncSession = Depends(get_session)):
    # just verify session belongs to user
    sid = uuid.UUID(id)
    res = await db.get(GameSession, sid)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if str(res.user_id) != str(user_data.get("user_id") or user_data.get("id") or json.loads(user_data.get("user", "{}")).get("id")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    scene = await create_and_store_scene(db, sid, payload.choice_text if payload else None)
    return SceneOut(id=str(scene.id), description=scene.description, image_url=scene.image_path, choices_json=scene.generated_choices)


@router.post("/{id}/choice", response_model=SceneOut, status_code=status.HTTP_201_CREATED)
async def choose_and_generate(id: str, payload: SceneCreate, user_data: dict = Depends(authenticated_user), db: AsyncSession = Depends(get_session)):
    return await generate_scene(id, payload, user_data, db)


@router.get("/{id}/scenes/{scene_id}", response_model=SceneOut)
async def get_scene(id: str, scene_id: str, user_data: dict = Depends(authenticated_user), db: AsyncSession = Depends(get_session)):
    scene = await db.get(Scene, uuid.UUID(scene_id))
    if not scene or str(scene.session_id) != id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return SceneOut(id=str(scene.id), description=scene.description, image_url=scene.image_path, choices_json=scene.generated_choices)


@router.get("/{id}/history", response_model=list[SceneOut])
async def history(id: str, user_data: dict = Depends(authenticated_user), db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(Scene).where(Scene.session_id == uuid.UUID(id)).order_by(Scene.order_num))
    scenes = list(res.scalars())
    return [SceneOut(id=str(s.id), description=s.description, image_url=s.image_path, choices_json=s.generated_choices) for s in scenes]


@router.put("/{id}/scenes/{scene_id}", response_model=SceneOut)
async def update_scene(id: str, scene_id: str, payload: SceneOut, user_data: dict = Depends(authenticated_user), db: AsyncSession = Depends(get_session)):
    scene = await db.get(Scene, uuid.UUID(scene_id))
    if not scene or str(scene.session_id) != id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    scene.description = payload.description
    scene.image_path = payload.image_url
    scene.generated_choices = payload.choices_json
    await db.commit()
    await db.refresh(scene)
    return SceneOut(id=str(scene.id), description=scene.description, image_url=scene.image_path, choices_json=scene.generated_choices)

