"""Utility cron jobs for the service."""

import asyncio
from sqlalchemy import update

from src.core.database import AsyncSessionLocal
from src.models.user import User

MAX_ENERGY = 50
ENERGY_RESTORE_INTERVAL = 60 * 60  # every hour


async def restore_energy() -> None:
    """Restore 1 energy for all users up to MAX_ENERGY."""

    async with AsyncSessionLocal() as session:
        await session.execute(
            update(User)
            .where(User.energy < MAX_ENERGY)
            .values(energy=User.energy + 1)
        )
        await session.commit()


async def energy_restore_worker() -> None:
    """Background task to periodically restore energy."""

    while True:
        await restore_energy()
        await asyncio.sleep(ENERGY_RESTORE_INTERVAL)

