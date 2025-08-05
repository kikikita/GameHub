from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.tg_auth import authenticate_server
from src.api.utils import ensure_admin
from src.core.database import get_session
from src.models.user import User

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


class GrantWishesIn(BaseModel):
    """Payload schema for granting wishes to a user."""

    username: str
    wishes: int = 1


@router.post("/grant_wishes/")
async def grant_wishes(
    payload: GrantWishesIn,
    tg_id: int = Depends(authenticate_server),
    db: AsyncSession = Depends(get_session),
) -> dict:
    """Grant the specified amount of wishes to the user with *username*.

    Requires that the requester is an admin (validated by ``ensure_admin``).
    The username can be provided with or without the leading ``@`` symbol.
    """

    # Ensure the requester has admin privileges
    ensure_admin(tg_id)

    normalized_username = payload.username.lstrip("@")

    # Fetch user by username
    result = await db.execute(select(User).where(User.username == normalized_username))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update wishes balance
    user.wishes += payload.wishes
    await db.commit()
    await db.refresh(user)

    return {
        "status": "success",
        "user_id": user.id,
        "username": user.username,
        "wishes": user.wishes,
        "granted": payload.wishes,
    }
