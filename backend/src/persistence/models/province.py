import enum
from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Province(Base):
    __tablename__ = "provinces"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)

    sectors: Mapped[list["Sector"]] = relationship("Sector", back_populates="province", cascade="all, delete-orphan")
    properties: Mapped[list["Property"]] = relationship("Property", back_populates="province")
