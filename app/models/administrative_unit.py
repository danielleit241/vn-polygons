from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AdministrativeUnit(Base):
    __tablename__ = "administrative_units"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name_en: Mapped[str | None] = mapped_column(String(255), nullable=True)
    short_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    short_name_en: Mapped[str | None] = mapped_column(String(255), nullable=True)
    code_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    code_name_en: Mapped[str | None] = mapped_column(String(255), nullable=True)

    provinces = relationship("Province", back_populates="administrative_unit")
    wards = relationship("Ward", back_populates="administrative_unit")
