import uuid
from datetime import datetime
import enum
from sqlalchemy import String, Text, Numeric, SmallInteger, Boolean, DateTime, ForeignKey, Enum as SAEnum, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry

from src.core.database import Base


class PropertyType(str, enum.Enum):
    house      = "house"
    apartment  = "apartment"
    commercial = "commercial"
    villa      = "villa"


class OperationType(str, enum.Enum):
    sale = "sale"
    rent = "rent"


class Currency(str, enum.Enum):
    DOP = "DOP"
    USD = "USD"


class PropertyStatus(str, enum.Enum):
    draft    = "draft"
    active   = "active"
    inactive = "inactive"
    sold     = "sold"
    rented   = "rented"


class Property(Base):
    __tablename__ = "properties"
    __table_args__ = (
        CheckConstraint(
            "(agent_id IS NOT NULL AND owner_id IS NULL) OR (agent_id IS NULL AND owner_id IS NOT NULL)",
            name="chk_single_publisher"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Publicador (agente o propietario, nunca ambos)
    agent_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"))
    owner_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("owners.id", ondelete="SET NULL"))

    # Info básica
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    property_type: Mapped[PropertyType] = mapped_column(SAEnum(PropertyType, name="property_type"), nullable=False)
    operation_type: Mapped[OperationType] = mapped_column(SAEnum(OperationType, name="operation_type"), nullable=False)

    # Precio
    price: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[Currency] = mapped_column(SAEnum(Currency, name="currency"), default=Currency.USD, nullable=False)

    # Características
    bedrooms: Mapped[int | None] = mapped_column(SmallInteger)
    bathrooms: Mapped[int | None] = mapped_column(SmallInteger)
    parking_spots: Mapped[int | None] = mapped_column(SmallInteger)
    area_m2: Mapped[float | None] = mapped_column(Numeric(10, 2))
    floors: Mapped[int | None] = mapped_column(SmallInteger)
    year_built: Mapped[int | None] = mapped_column(SmallInteger)

    # Ubicación — ahora con FK a catálogos (Opción B)
    country: Mapped[str] = mapped_column(String(100), default="República Dominicana", nullable=False)
    province_id: Mapped[int] = mapped_column(ForeignKey("provinces.id"), nullable=False)
    sector_id: Mapped[int | None] = mapped_column(ForeignKey("sectors.id"))
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255))
    location: Mapped[object | None] = mapped_column(Geometry(geometry_type="POINT", srid=4326))

    # Estado
    status: Mapped[PropertyStatus] = mapped_column(SAEnum(PropertyStatus, name="property_status"), default=PropertyStatus.draft, nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relaciones
    agent: Mapped["Agent"] = relationship("Agent", back_populates="properties")
    owner: Mapped["Owner"] = relationship("Owner", back_populates="properties")
    province: Mapped["Province"] = relationship("Province", back_populates="properties")
    sector: Mapped["Sector | None"] = relationship("Sector", back_populates="properties")
    images: Mapped[list["PropertyImage"]] = relationship("PropertyImage", back_populates="property", cascade="all, delete-orphan")
    favorited_by: Mapped[list["Favorite"]] = relationship("Favorite", back_populates="property", cascade="all, delete-orphan")
    amenities: Mapped[list["Amenity"]] = relationship("Amenity", secondary="property_amenities", back_populates="properties")
