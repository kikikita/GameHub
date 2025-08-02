from fastapi import APIRouter, Depends
from auth.tg_auth import verify_tg_data
import json
from handlers.game import handle_external_game_start
import asyncio

router = APIRouter(prefix="/api/v1/stories", tags=["stories"])


@router.post("/start/{id}/")
async def start_story(id: str, user_data: dict = Depends(verify_tg_data)):
    user_info = json.loads(user_data.get("user", "{}"))
    user_id = user_info.get("id")
    asyncio.create_task(handle_external_game_start(id, user_id))
    return {"message": "Game started"}