from pydantic import BaseModel, ConfigDict, Field


class AdministrativeRegionBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    name_en: str = Field(min_length=1, max_length=255)
    code_name: str | None = Field(default=None, max_length=255)
    code_name_en: str | None = Field(default=None, max_length=255)


class AdministrativeRegionCreate(AdministrativeRegionBase):
    id: int


class AdministrativeRegionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    name_en: str | None = Field(default=None, min_length=1, max_length=255)
    code_name: str | None = Field(default=None, max_length=255)
    code_name_en: str | None = Field(default=None, max_length=255)


class AdministrativeRegionRead(AdministrativeRegionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
