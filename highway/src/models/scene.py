"""Database model representing a scene within a session."""

import uuid

from sqlalchemy import Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

class Scene(Base):
    """A single scene in the interactive story."""

    __tablename__ = "scenes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("game_sessions.id")
    )
    order_num: Mapped[int] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_choices: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    image_path: Mapped[str | None] = mapped_column(Text, nullable=True)

    session: Mapped["GameSession"] = relationship(back_populates="scenes")
    choices: Mapped[list["Choice"]] = relationship(back_populates="scene")

    def __repr__(self) -> str:
        return (
            f"Scene(id={self.id}, session_id={self.session_id}, "
            f"order_num={self.order_num})"
        )
