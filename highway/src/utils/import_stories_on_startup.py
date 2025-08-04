from src.core.database import AsyncSessionLocal
from src.models.world import World
from src.api.stories.router import _import_presets
from pathlib import Path
import json
from sqlalchemy import select
from src.config import settings

import logging

logger = logging.getLogger(__name__)

async def import_stories_on_startup():
    # Automatically import preset worlds and stories on first startup if none exist
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(World).where(World.is_preset.is_(True)))
        if res.scalars().first() is None:
            presets_path = Path(settings.presets_file_path)
            if not presets_path.is_absolute():
                presets_path = Path(__file__).resolve().parent.parent / presets_path
            try:
                data = json.loads(presets_path.read_text(encoding="utf-8"))
                await _import_presets(session, data)
                logger.info("Default presets imported from %s", presets_path)
            except FileNotFoundError:
                logger.warning("Presets file %s not found, skipping import", presets_path)
            except Exception as exc:
                logger.exception("Failed to import presets: %s", exc)
        else:
            logger.info("Presets already imported")