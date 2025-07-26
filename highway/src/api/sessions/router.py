from fastapi import APIRouter, Depends, HTTPException, status, WebSocket
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.tg_auth import authenticated_user
from src.core.database import get_session
from src.models.game_session import GameSession
from src.models.scene import Scene
from .schemas import SessionCreate, SessionOut
from src.api.scenes.schemas import SceneOut
from src.api.utils import resolve_user_id
import uuid
import os

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


@router.post("", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
async def create_session(payload: SessionCreate, user_data: dict = Depends(authenticated_user), db: AsyncSession = Depends(get_session)):
    user_id = await resolve_user_id(db, user_data)
    template_id = uuid.UUID(payload.template_id) if payload.template_id else None
    session_obj = GameSession(user_id=user_id, template_id=template_id)
    db.add(session_obj)
    await db.commit()
    await db.refresh(session_obj)
    return SessionOut(id=str(session_obj.id), started_at=session_obj.started_at, share_code=str(session_obj.share_code))


@router.get("/{id}", response_model=SceneOut | None)
async def get_current(id: str, user_data: dict = Depends(authenticated_user), db: AsyncSession = Depends(get_session)):
    sid = uuid.UUID(id)
    session_obj = await db.get(GameSession, sid)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    res = await db.execute(select(Scene).where(Scene.session_id == sid).order_by(Scene.order_num.desc()))
    scene = res.scalars().first()
    if not scene:
        return None
    return SceneOut(id=str(scene.id), description=scene.description, image_url=scene.image_path, choices_json=scene.generated_choices)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(id: str, user_data: dict = Depends(authenticated_user), db: AsyncSession = Depends(get_session)):
    sid = uuid.UUID(id)
    session_obj = await db.get(GameSession, sid)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await db.delete(session_obj)
    await db.commit()


@router.websocket("/{session_id}/audio")
async def audio_stream(ws: WebSocket, session_id: str):
    await ws.accept()
    file_path = os.path.join("assets", f"{session_id}.wav")
    try:
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(32 * 1024)
                if not chunk:
                    break
                await ws.send_bytes(chunk)
    except FileNotFoundError:
        await ws.close(code=1000)
        return
    await ws.close()

