"""Utility cron jobs for the service."""

import asyncio
from sqlalchemy import update

from src.core.database import AsyncSessionLocal
from src.models.user import User

MAX_ENERGY = 50


async def restore_energy() -> None:
    """Restore 1 energy for all users up to MAX_ENERGY."""
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(User)
            .where(User.energy < MAX_ENERGY)
            .values(energy=User.energy + 1)
        )
        await session.commit()


if __name__ == "__main__":
    asyncio.run(restore_energy())

