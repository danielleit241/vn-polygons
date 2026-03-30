from pydantic import BaseModel, ConfigDict, Field


class WardBase(BaseModel):
    code: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=255)
    name_en: str | None = Field(default=None, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    full_name_en: str | None = Field(default=None, max_length=255)
    code_name: str | None = Field(default=None, max_length=255)
    province_code: str | None = Field(default=None, max_length=20)
    administrative_unit_id: int | None = None


class WardCreate(WardBase):
    pass


class WardUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    name_en: str | None = Field(default=None, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    full_name_en: str | None = Field(default=None, max_length=255)
    code_name: str | None = Field(default=None, max_length=255)
    province_code: str | None = Field(default=None, max_length=20)
    administrative_unit_id: int | None = None


class WardRead(WardBase):
    model_config = ConfigDict(from_attributes=True)
