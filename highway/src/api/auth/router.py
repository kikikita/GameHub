from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from src.core.database import get_session
from src.models.user import User
from src.auth.tg_auth import authenticated_user
import json

router = APIRouter(prefix="/api/v1")


class RegisterIn(BaseModel):
    tg_id: int
    username: str | None = None


class UserOut(BaseModel):
    id: int
    tg_id: int
    username: str | None = None

    class Config:
        from_attributes = True


@router.post("/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(payload: RegisterIn, session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(User).where(User.tg_id == payload.tg_id))
    if res.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    user = User(tg_id=payload.tg_id, username=payload.username)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.get("/users/me", response_model=UserOut)
async def get_me(user_data: dict = Depends(authenticated_user), session: AsyncSession = Depends(get_session)):
    tg_id = None
    if "user_id" in user_data:
        tg_id = str(user_data["user_id"])
    else:
        if isinstance(user_data.get("user"), str):
            try:
                tg_id = str(json.loads(user_data["user"]).get("id"))
            except Exception:
                tg_id = None
        if tg_id is None:
            tg_id = str(user_data.get("id")) if user_data.get("id") is not None else None
    if not tg_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    res = await session.execute(select(User).where(User.tg_id == tg_id))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
