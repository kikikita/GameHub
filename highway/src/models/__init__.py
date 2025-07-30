"""Base model for SQLAlchemy ORM."""

import uuid
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase



class Base(DeclarativeBase):
    metadata = MetaData()


from .user import User
from .world import World
from .story import Story
from .game_session import GameSession
from .scene import Scene
from .choice import Choice
from .subscription import Subscription
