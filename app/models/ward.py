from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Ward(Base):
    __tablename__ = "wards"
    __table_args__ = (
        Index("idx_wards_province", "province_code"),
        Index("idx_wards_unit", "administrative_unit_id"),
    )

    code: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name_en: Mapped[str | None] = mapped_column(String(255), nullable=True)
    code_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    province_code: Mapped[str | None] = mapped_column(
        String(20),
        ForeignKey("provinces.code"),
        nullable=True,
    )
    administrative_unit_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("administrative_units.id"),
        nullable=True,
    )

    province = relationship("Province", back_populates="wards")
    administrative_unit = relationship("AdministrativeUnit", back_populates="wards")
