from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.administrative_region import AdministrativeRegion
from app.schemas.administrative_region import AdministrativeRegionCreate, AdministrativeRegionUpdate


def list_regions(db: Session, skip: int = 0, limit: int = 20) -> list[AdministrativeRegion]:
    stmt = select(AdministrativeRegion).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_region(db: Session, region_id: int) -> AdministrativeRegion:
    region = db.get(AdministrativeRegion, region_id)
    if region is None:
        raise LookupError("Region not found")
    return region


def create_region(db: Session, payload: AdministrativeRegionCreate) -> AdministrativeRegion:
    if db.get(AdministrativeRegion, payload.id) is not None:
        raise ValueError("Region already exists")

    region = AdministrativeRegion(**payload.model_dump())
    db.add(region)
    db.commit()
    db.refresh(region)
    return region


def update_region(db: Session, region_id: int, payload: AdministrativeRegionUpdate) -> AdministrativeRegion:
    region = get_region(db, region_id)

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(region, key, value)

    db.add(region)
    db.commit()
    db.refresh(region)
    return region


def delete_region(db: Session, region_id: int) -> None:
    region = get_region(db, region_id)
    db.delete(region)
    db.commit()
