import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, SmallInteger, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base


class PropertyImage(Base):
    __tablename__ = "property_images"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    cloudinary_url: Mapped[str] = mapped_column(String(500), nullable=False)
    cloudinary_public_id: Mapped[str] = mapped_column(String(255), nullable=False)
    is_cover: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    property: Mapped["Property"] = relationship("Property", back_populates="images")
