"""Base model for SQLAlchemy ORM."""

import uuid
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase



class Base(DeclarativeBase):
    metadata = MetaData()

# Import models so Alembic can discover them
from .world import World  # noqa: F401
from .story import Story  # noqa: F401

