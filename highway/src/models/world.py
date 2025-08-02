"""SQLAlchemy model for story worlds."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, TIMESTAMP, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class World(Base):
    """A setting that groups multiple stories."""

    __tablename__ = "worlds"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    title: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    world_desc: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_free: Mapped[bool] = mapped_column(Boolean, default=False)
    is_preset: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow
    )

    user: Mapped["User"] = relationship(back_populates="worlds")
    stories: Mapped[list["Story"]] = relationship(back_populates="world")

    def __repr__(self) -> str:
        return f"World(id={self.id})"
