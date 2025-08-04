from fastapi import APIRouter, Depends
from auth.tg_auth import authenticated_user
from handlers.game import handle_create_story, handle_external_game_start
import asyncio

router = APIRouter(prefix="/api/v1/stories", tags=["stories"])


@router.post("/start/{id}/")
async def start_story(id: str, tg_id: int = Depends(authenticated_user)):
    asyncio.create_task(handle_external_game_start(id, tg_id))
    return {"message": "Game started"}

@router.post("/")
async def create_story(tg_id: int = Depends(authenticated_user)):
    asyncio.create_task(handle_create_story(tg_id))
    return {"message": "Game started"}