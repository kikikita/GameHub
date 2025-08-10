"""Async MongoDB-backed user state storage (replica set ready)."""

from __future__ import annotations

import json
import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from src.game.agent.models import UserState
from src.config import settings

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for storing UserState objects in MongoDB.

    Stores one document per user with `_id` = user_id and `data` = serialized state.
    """

    def __init__(self, mongodb_uri: Optional[str] = None, database_name: Optional[str] = None) -> None:
        uri = mongodb_uri or settings.mongodb_uri
        db_name = database_name or settings.mongodb_db

        self.client = AsyncIOMotorClient(uri, uuidRepresentation="standard")
        self.db = self.client[db_name]
        self.collection: AsyncIOMotorCollection = self.db[settings.mongodb_collection or "user_states"]

    async def get(self, user_id: str) -> UserState:
        """Return user state for the given id, creating it if absent."""
        logger.debug("[MongoState] Fetching state for %s", user_id)
        doc = await self.collection.find_one({"_id": user_id})
        if doc is None or "data" not in doc:
            return UserState()
        # Ensure we validate against the Pydantic model
        return UserState.model_validate(doc["data"])  # type: ignore[arg-type]

    async def set(self, user_id: str, state: UserState) -> None:
        """Persist updated user state."""
        logger.debug("[MongoState] Saving state for %s", user_id)
        # Convert to plain dict to avoid non-JSON types
        state_dict = json.loads(state.model_dump_json())
        await self.collection.update_one(
            {"_id": user_id},
            {"$set": {"data": state_dict}},
            upsert=True,
        )

    async def reset(self, user_id: str) -> None:
        """Remove stored state for a user."""
        logger.debug("[MongoState] Resetting state for %s", user_id)
        await self.collection.delete_one({"_id": user_id})


_repo = UserRepository()


async def get_user_state(user_hash: str) -> UserState:
    logger.debug("get_user_state for %s", user_hash)
    return await _repo.get(user_hash)


async def set_user_state(user_hash: str, state: UserState) -> None:
    logger.debug("set_user_state for %s", user_hash)
    await _repo.set(user_hash, state)


async def reset_user_state(user_hash: str) -> None:
    logger.debug("reset_user_state for %s", user_hash)
    await _repo.reset(user_hash)


