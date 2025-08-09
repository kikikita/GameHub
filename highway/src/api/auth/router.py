"""Authentication related API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.core.database import get_session
from src.models.user import User
from src.auth.tg_auth import authenticated_user
import httpx
from src.config import settings

router = APIRouter(prefix="/api/v1")

client = httpx.AsyncClient(
    base_url=settings.bot_server_url,
    timeout=httpx.Timeout(60.0),
    headers={"X-Server-Auth": settings.server_auth_token.get_secret_value()},
)


class RegisterIn(BaseModel):
    """Payload schema for the user registration endpoint."""

    tg_id: int
    username: str | None = None
    language: str | None = None
    image_format: str | None = None


class UserOut(BaseModel):
    """Response schema for user related endpoints."""

    id: int
    tg_id: int
    username: str | None = None
    language: str | None = None
    image_format: str
    energy: int
    wishes: int

    class Config:
        from_attributes = True


@router.post(
    "/auth/register/",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    payload: RegisterIn, session: AsyncSession = Depends(get_session)
) -> User:
    """Create a new user in the database."""

    res = await session.execute(select(User).where(User.tg_id == payload.tg_id))
    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )
    user = User(
        tg_id=payload.tg_id,
        username=payload.username,
        language=payload.language,
        image_format=payload.image_format or "vertical",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.get("/users/me/", response_model=UserOut)
async def get_me(
    tg_id: int = Depends(authenticated_user),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Return a user identified by Telegram authentication data."""
    res = await session.execute(select(User).where(User.tg_id == tg_id))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


class UserUpdate(BaseModel):
    language: str | None = None
    image_format: str | None = None


@router.patch("/users/me/", response_model=UserOut)
async def update_me(
    payload: UserUpdate,
    tg_id: int = Depends(authenticated_user),
    session: AsyncSession = Depends(get_session),
) -> User:
    res = await session.execute(select(User).where(User.tg_id == tg_id))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.language is not None:
        await client.post(
            "/api/v1/cache/language/update/",
            json={"language": payload.language, "user_id": tg_id},
        )
        user.language = payload.language
    if payload.image_format is not None:
        user.image_format = payload.image_format
    await session.commit()
    await session.refresh(user)
    return user
