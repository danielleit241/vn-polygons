from pydantic import BaseModel, ConfigDict, Field


class AdministrativeUnitBase(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)
    full_name_en: str | None = Field(default=None, max_length=255)
    short_name: str | None = Field(default=None, max_length=255)
    short_name_en: str | None = Field(default=None, max_length=255)
    code_name: str | None = Field(default=None, max_length=255)
    code_name_en: str | None = Field(default=None, max_length=255)


class AdministrativeUnitCreate(AdministrativeUnitBase):
    id: int


class AdministrativeUnitUpdate(AdministrativeUnitBase):
    pass


class AdministrativeUnitRead(AdministrativeUnitBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
