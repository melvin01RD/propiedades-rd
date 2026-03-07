import enum
from sqlalchemy import String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class AmenityCategory(str, enum.Enum):
    security   = "security"
    recreation = "recreation"
    services   = "services"
    exterior   = "exterior"


class Amenity(Base):
    __tablename__ = "amenities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    category: Mapped[AmenityCategory] = mapped_column(SAEnum(AmenityCategory, name="amenity_category"), nullable=False)
    icon: Mapped[str | None] = mapped_column(String(50))

    properties: Mapped[list["Property"]] = relationship(
        "Property", secondary="property_amenities", back_populates="amenities"
    )
