from fastapi import APIRouter, Depends
from api.auth import auth_server as auth
from pydantic import BaseModel
from utils.i18n import set_user_language

router = APIRouter(prefix="/api/v1/cache", tags=["cache"])

class LanguageUpdate(BaseModel):
    language: str
    user_id: int

@router.post("/language/update/")
async def update_user_language(data: LanguageUpdate, auth: bool = Depends(auth)):
    set_user_language(data.user_id, data.language)
    return {"message": "Language updated"}
