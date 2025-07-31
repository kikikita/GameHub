"""SQLAlchemy model for individual stories."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, TIMESTAMP, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class Story(Base):
    """Story that can be used to start a session."""

    __tablename__ = "stories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    world_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("worlds.id")
    )
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    story_desc: Mapped[str | None] = mapped_column(Text, nullable=True)
    genre: Mapped[str | None] = mapped_column(Text, nullable=True)
    character: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    story_frame: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    is_free: Mapped[bool] = mapped_column(Boolean, default=False)
    is_preset: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow
    )

    world: Mapped["World"] = relationship(back_populates="stories")
    user: Mapped["User"] = relationship(back_populates="stories")
    sessions: Mapped[list["GameSession"]] = relationship(back_populates="story")

    def __repr__(self) -> str:
        return f"Story(id={self.id}, world_id={self.world_id})"
