import json
import unicodedata
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.administrative_unit import AdministrativeUnit
from app.models.province import Province
from app.schemas.province import (
    ProvinceBoundaryRead,
    ProvinceCreate,
    ProvincePolygonImportResult,
    ProvinceRead,
    ProvinceUpdate,
)

router = APIRouter()


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

    # Preserve order and remove duplicates.
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


@router.get("", response_model=list[ProvinceRead])
def list_provinces(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[Province]:
    stmt = select(Province).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


@router.get("/{province_code}", response_model=ProvinceRead)
def get_province(province_code: str, db: Session = Depends(get_db)) -> Province:
    province = db.get(Province, province_code)
    if province is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Province not found")
    return province


@router.get("/{province_code}/boundary", response_model=ProvinceBoundaryRead)
def get_province_boundary(province_code: str, db: Session = Depends(get_db)) -> ProvinceBoundaryRead:
    province = db.get(Province, province_code)
    if province is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Province not found")

    if not isinstance(province.boundary_geojson, dict):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Province boundary not found")

    return ProvinceBoundaryRead(
        code=province.code,
        name=province.name,
        boundary_geojson=province.boundary_geojson,
    )


@router.post("", response_model=ProvinceRead, status_code=status.HTTP_201_CREATED)
def create_province(payload: ProvinceCreate, db: Session = Depends(get_db)) -> Province:
    existing = db.get(Province, payload.code)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Province already exists")

    if payload.administrative_unit_id is not None:
        unit = db.get(AdministrativeUnit, payload.administrative_unit_id)
        if unit is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Administrative unit not found",
            )

    province = Province(**payload.model_dump())
    db.add(province)
    db.commit()
    db.refresh(province)
    return province


@router.put("/{province_code}", response_model=ProvinceRead)
def update_province(
    province_code: str,
    payload: ProvinceUpdate,
    db: Session = Depends(get_db),
) -> Province:
    province = db.get(Province, province_code)
    if province is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Province not found")

    changes = payload.model_dump(exclude_unset=True)
    if "administrative_unit_id" in changes and changes["administrative_unit_id"] is not None:
        unit = db.get(AdministrativeUnit, changes["administrative_unit_id"])
        if unit is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Administrative unit not found",
            )

    for key, value in changes.items():
        setattr(province, key, value)

    db.add(province)
    db.commit()
    db.refresh(province)
    return province


@router.delete("/{province_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_province(province_code: str, db: Session = Depends(get_db)) -> None:
    province = db.get(Province, province_code)
    if province is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Province not found")

    db.delete(province)
    db.commit()
    return None


@router.post("/polygons/import", response_model=ProvincePolygonImportResult)
def import_province_polygons(
    overwrite: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> ProvincePolygonImportResult:
    polygon_dir = Path(settings.PROVINCE_POLYGONS_DIR)
    if not polygon_dir.exists() or not polygon_dir.is_dir():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Polygon directory not found: {polygon_dir}",
        )

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
