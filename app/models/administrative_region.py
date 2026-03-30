from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AdministrativeRegion(Base):
    __tablename__ = "administrative_regions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    code_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    code_name_en: Mapped[str | None] = mapped_column(String(255), nullable=True)
