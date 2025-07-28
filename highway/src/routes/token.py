from google import genai
from fastapi import APIRouter, Depends, Response
from src.auth.tg_auth import verify_tg_data
from src.config import settings
import datetime

client = genai.Client(
    api_key=settings.gemini_api_key.get_secret_value(),
    http_options={
        "api_version": "v1alpha",
    }
)

token_router = APIRouter(prefix="/token", tags=["token"])


@token_router.post("/create-ephemeral-token")
async def create_token(response: Response, user_data: dict = Depends(verify_tg_data)):
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    token = client.auth_tokens.create(
        config={
            "uses": 5,
            'expire_time': now + datetime.timedelta(hours=10),
            'new_session_expire_time':now + datetime.timedelta(hours=5),
            "live_connect_constraints": {
                "model": "models/lyria-realtime-exp",
            }
        }
    )
    
    return { "token": token }
