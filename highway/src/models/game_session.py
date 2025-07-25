import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class GameSession(Base):
    __tablename__ = "game_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    template_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("game_templates.id"), nullable=True)
    started_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    share_code: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4)

    user: Mapped["User"] = relationship(back_populates="sessions")
    template: Mapped["GameTemplate | None"] = relationship(back_populates="sessions")
    scenes: Mapped[list["Scene"]] = relationship(back_populates="session")

    def __repr__(self) -> str:
        return f"GameSession(id={self.id}, user_id={self.user_id})"

