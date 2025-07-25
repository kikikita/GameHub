import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class Choice(Base):
    __tablename__ = "choices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scene_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("scenes.id"))
    choice_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    scene: Mapped["Scene"] = relationship(back_populates="choices")

    def __repr__(self) -> str:
        return f"Choice(id={self.id}, scene_id={self.scene_id})"
