"""SQLAlchemy models for users and related entities."""

from datetime import datetime

from sqlalchemy import Boolean, TIMESTAMP, Text, Integer, BigInteger, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class User(Base):
    """Application user."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
    )
    username: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.utcnow,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    worlds: Mapped[list["World"]] = relationship(
        back_populates="user",
    )
    stories: Mapped[list["Story"]] = relationship(
        back_populates="user",
    )
    sessions: Mapped[list["GameSession"]] = relationship(
        back_populates="user",
    )
    subscriptions: Mapped[list["Subscription"]] = relationship(
        back_populates="user",
    )
    bundle_purchases: Mapped[list["BundlePurchase"]] = relationship(
        back_populates="user",
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, tg_id={self.tg_id})"
