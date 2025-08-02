"""Endpoints related to gameplay sessions."""

from fastapi import APIRouter, Depends, HTTPException, status
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.tg_auth import authenticated_user
from src.core.database import get_session
from src.models.game_session import GameSession
from src.models.scene import Scene
from src.models.story import Story
from src.api.scenes.scene_service import create_and_store_scene
from .schemas import SessionCreate, SessionOut
from src.api.scenes.schemas import SceneOut, scene_to_out
from src.api.utils import resolve_user_id

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


@router.post("/", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: SessionCreate,
    tg_id: int = Depends(authenticated_user),
    db: AsyncSession = Depends(get_session),
) -> SessionOut:
    """Create a new gameplay session."""

    user_id = await resolve_user_id(tg_id, db)
    story_id = (
        uuid.UUID(payload.story_id) if payload.story_id else None
    )
    session_obj = GameSession(user_id=user_id, story_id=story_id)
    db.add(session_obj)
    await db.commit()
    await db.refresh(session_obj)

    if story_id:
        story = await db.get(Story, story_id)
        if story:
            await db.refresh(story, ["world"])
            await create_and_store_scene(db, session_obj, None, story)

    return SessionOut(
        id=str(session_obj.id),
        started_at=session_obj.started_at,
        share_code=str(session_obj.share_code),
        story_frame=session_obj.story_frame,
        is_finished=session_obj.is_finished,
    )


@router.get("/{id}/", response_model=SceneOut | None)
async def get_current(
    id: str,
    tg_id: int = Depends(authenticated_user),
    db: AsyncSession = Depends(get_session),
) -> SceneOut | None:
    """Return the latest scene for a session."""

    sid = uuid.UUID(id)
    session_obj = await db.get(GameSession, sid)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    res = await db.execute(
        select(Scene)
        .where(Scene.session_id == sid)
        .order_by(Scene.order_num.desc())
    )
    scene = res.scalars().first()
    if not scene:
        return None
    return scene_to_out(scene)


@router.delete("/{id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    id: str,
    tg_id: int = Depends(authenticated_user),
    db: AsyncSession = Depends(get_session),
) -> None:
    """Remove a session and its data."""

    sid = uuid.UUID(id)
    session_obj = await db.get(GameSession, sid)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await db.delete(session_obj)
    await db.commit()


