"""Base model for SQLAlchemy ORM."""

import uuid
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    metadata = MetaData()

