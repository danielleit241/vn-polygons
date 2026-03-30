import json
import unicodedata
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.administrative_unit import AdministrativeUnit
from app.models.province import Province
from app.schemas.province import ProvinceCreate, ProvincePolygonImportResult, ProvinceUpdate


def _slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    return "_".join("".join(ch.lower() if ch.isalnum() else " " for ch in ascii_only).split())


def _province_polygon_candidates(province: Province) -> list[str]:
    candidates: list[str] = []
    if province.code_name:
        candidates.append(province.code_name)

    candidates.append(_slugify(province.name))
    if province.name_en:
        candidates.append(_slugify(province.name_en))

    if province.code_name == "ho_chi_minh":
        candidates.append("tp_ho_chi_minh")

    return list(dict.fromkeys(filter(None, candidates)))


def _read_geometry_from_geojson(file_path: Path) -> dict:
    data = json.loads(file_path.read_text(encoding="utf-8"))
    features = data.get("features")
    if not isinstance(features, list) or not features:
        raise ValueError("GeoJSON has no features")

    geometry = features[0].get("geometry")
    if not isinstance(geometry, dict):
        raise ValueError("GeoJSON feature has no geometry")

    return geometry


def list_provinces(db: Session, skip: int = 0, limit: int = 20) -> list[Province]:
    stmt = select(Province).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_province(db: Session, province_code: str) -> Province:
    province = db.get(Province, province_code)
    if province is None:
        raise LookupError("Province not found")
    return province


def create_province(db: Session, payload: ProvinceCreate) -> Province:
    if db.get(Province, payload.code) is not None:
        raise ValueError("Province already exists")

    if payload.administrative_unit_id is not None:
        unit = db.get(AdministrativeUnit, payload.administrative_unit_id)
        if unit is None:
            raise ValueError("Administrative unit not found")

    province = Province(**payload.model_dump())
    db.add(province)
    db.commit()
    db.refresh(province)
    return province


def update_province(db: Session, province_code: str, payload: ProvinceUpdate) -> Province:
    province = get_province(db, province_code)

    changes = payload.model_dump(exclude_unset=True)
    if "administrative_unit_id" in changes and changes["administrative_unit_id"] is not None:
        unit = db.get(AdministrativeUnit, changes["administrative_unit_id"])
        if unit is None:
            raise ValueError("Administrative unit not found")

    for key, value in changes.items():
        setattr(province, key, value)

    db.add(province)
    db.commit()
    db.refresh(province)
    return province


def delete_province(db: Session, province_code: str) -> None:
    province = get_province(db, province_code)
    db.delete(province)
    db.commit()


def import_province_polygons(
    db: Session,
    polygons_dir: str,
    overwrite: bool = False,
) -> ProvincePolygonImportResult:
    polygon_dir = Path(polygons_dir)
    if not polygon_dir.exists() or not polygon_dir.is_dir():
        raise ValueError(f"Polygon directory not found: {polygon_dir}")

    provinces = list(db.scalars(select(Province)).all())
    updated = 0
    missing_files: list[str] = []
    failed_files: list[str] = []

    for province in provinces:
        if province.boundary_geojson is not None and not overwrite:
            continue

        candidates = _province_polygon_candidates(province)
        matched_file: Path | None = None

        for candidate in candidates:
            file_path = polygon_dir / f"{candidate}.json"
            if file_path.exists():
                matched_file = file_path
                break

        if matched_file is None:
            missing_files.append(province.code)
            continue

        try:
            province.boundary_geojson = _read_geometry_from_geojson(matched_file)
            updated += 1
        except Exception:
            failed_files.append(f"{province.code}:{matched_file.name}")

    db.commit()
    return ProvincePolygonImportResult(
        updated=updated,
        missing_files=missing_files,
        failed_files=failed_files,
    )
