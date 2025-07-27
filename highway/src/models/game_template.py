"""SQLAlchemy model for game templates."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, TIMESTAMP, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class GameTemplate(Base):
    """Template used to start a new game session."""

    __tablename__ = "game_templates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    setting_desc: Mapped[str | None] = mapped_column(Text, nullable=True)
    char_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    char_age: Mapped[str | None] = mapped_column(Text, nullable=True)
    char_background: Mapped[str | None] = mapped_column(Text, nullable=True)
    char_personality: Mapped[str | None] = mapped_column(Text, nullable=True)
    genre: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.utcnow,
    )

    user: Mapped["User"] = relationship(back_populates="templates")
    sessions: Mapped[list["GameSession"]] = relationship(
        back_populates="template",
    )

    def __repr__(self) -> str:
        return f"GameTemplate(id={self.id}, user_id={self.user_id})"
