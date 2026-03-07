import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base


class PropertyAmenity(Base):
    __tablename__ = "property_amenities"

    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), primary_key=True
    )
    amenity_id: Mapped[int] = mapped_column(
        ForeignKey("amenities.id", ondelete="CASCADE"), primary_key=True
    )
