"""Base model for SQLAlchemy ORM."""

import uuid
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase



class Base(DeclarativeBase):
    metadata = MetaData()

# Import models so Alembic can discover them
# Import all models so that SQLAlchemy can resolve string based relationships
# during mapper configuration. Failing to import a model before it is referenced
# in another model's ``relationship`` definition results in ``InvalidRequestError``
# when SQLAlchemy tries to resolve the class name. Importing them here ensures
# they are registered with the declarative registry on startup.

from .user import User  # noqa: F401
from .world import World  # noqa: F401
from .story import Story  # noqa: F401
from .game_session import GameSession  # noqa: F401
from .scene import Scene  # noqa: F401
from .choice import Choice  # noqa: F401
from .subscription import Subscription  # noqa: F401

