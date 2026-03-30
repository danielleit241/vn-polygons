from sqlalchemy import JSON, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Province(Base):
    __tablename__ = "provinces"
    __table_args__ = (Index("idx_provinces_unit", "administrative_unit_id"),)

    code: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name_en: Mapped[str | None] = mapped_column(String(255), nullable=True)
    code_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    boundary_geojson: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    administrative_unit_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("administrative_units.id"),
        nullable=True,
    )

    administrative_unit = relationship("AdministrativeUnit", back_populates="provinces")
    wards = relationship("Ward", back_populates="province")
