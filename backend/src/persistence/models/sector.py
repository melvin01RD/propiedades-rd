from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Sector(Base):
    __tablename__ = "sectors"
    __table_args__ = (
        UniqueConstraint("name", "province_id", name="uq_sector_name_province"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    province_id: Mapped[int] = mapped_column(ForeignKey("provinces.id", ondelete="CASCADE"), nullable=False)

    province: Mapped["Province"] = relationship("Province", back_populates="sectors")
    properties: Mapped[list["Property"]] = relationship("Property", back_populates="sector")
