import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.game_template import GameTemplate


async def create_template(db: AsyncSession, user_id: uuid.UUID, data: dict) -> GameTemplate:
    template = GameTemplate(user_id=user_id, **data)
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


async def list_templates(db: AsyncSession, user_id: uuid.UUID) -> list[GameTemplate]:
    res = await db.execute(select(GameTemplate).where(GameTemplate.user_id == user_id))
    return list(res.scalars())


async def get_template(db: AsyncSession, user_id: uuid.UUID, template_id: uuid.UUID) -> GameTemplate | None:
    res = await db.execute(
        select(GameTemplate).where(GameTemplate.user_id == user_id, GameTemplate.id == template_id)
    )
    return res.scalar_one_or_none()


async def share_template(db: AsyncSession, user_id: uuid.UUID, template_id: uuid.UUID) -> GameTemplate | None:
    template = await get_template(db, user_id, template_id)
    if not template:
        return None
    template.is_public = True
    await db.commit()
    await db.refresh(template)
    return template


async def get_shared_template(db: AsyncSession, share_code: str) -> GameTemplate | None:
    try:
        tid = uuid.UUID(share_code)
    except Exception:
        return None
    res = await db.execute(
        select(GameTemplate).where(GameTemplate.id == tid, GameTemplate.is_public.is_(True))
    )
    return res.scalar_one_or_none()

