from pydantic import BaseModel, ConfigDict, Field


class ProvinceBase(BaseModel):
    code: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=255)
    name_en: str | None = Field(default=None, max_length=255)
    full_name: str = Field(min_length=1, max_length=255)
    full_name_en: str | None = Field(default=None, max_length=255)
    code_name: str | None = Field(default=None, max_length=255)
    boundary_geojson: dict | None = None
    administrative_unit_id: int | None = None


class ProvinceCreate(ProvinceBase):
    pass


class ProvinceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    name_en: str | None = Field(default=None, max_length=255)
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    full_name_en: str | None = Field(default=None, max_length=255)
    code_name: str | None = Field(default=None, max_length=255)
    boundary_geojson: dict | None = None
    administrative_unit_id: int | None = None


class ProvinceRead(BaseModel):
    code: str
    name: str
    name_en: str | None = None
    full_name: str
    full_name_en: str | None = None
    code_name: str | None = None
    administrative_unit_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class ProvinceBoundaryRead(BaseModel):
    code: str
    name: str
    boundary_geojson: dict

    model_config = ConfigDict(from_attributes=True)


class ProvincePolygonImportResult(BaseModel):
    updated: int
    missing_files: list[str]
    failed_files: list[str]
