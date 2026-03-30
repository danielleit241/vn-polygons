from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.administrative_unit import AdministrativeUnit
from app.models.province import Province
from app.models.ward import Ward
from app.schemas.ward import WardCreate, WardUpdate


def list_wards(
    db: Session,
    province_code: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[Ward]:
    stmt = select(Ward)
    if province_code:
        stmt = stmt.where(Ward.province_code == province_code)
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_ward(db: Session, ward_code: str) -> Ward:
    ward = db.get(Ward, ward_code)
    if ward is None:
        raise LookupError("Ward not found")
    return ward


def create_ward(db: Session, payload: WardCreate) -> Ward:
    if db.get(Ward, payload.code) is not None:
        raise ValueError("Ward already exists")

    if payload.province_code is not None and db.get(Province, payload.province_code) is None:
        raise ValueError("Province not found")

    if payload.administrative_unit_id is not None:
        if db.get(AdministrativeUnit, payload.administrative_unit_id) is None:
            raise ValueError("Administrative unit not found")

    ward = Ward(**payload.model_dump())
    db.add(ward)
    db.commit()
    db.refresh(ward)
    return ward


def update_ward(db: Session, ward_code: str, payload: WardUpdate) -> Ward:
    ward = get_ward(db, ward_code)

    changes = payload.model_dump(exclude_unset=True)
    if "province_code" in changes and changes["province_code"] is not None:
        if db.get(Province, changes["province_code"]) is None:
            raise ValueError("Province not found")

    if "administrative_unit_id" in changes and changes["administrative_unit_id"] is not None:
        if db.get(AdministrativeUnit, changes["administrative_unit_id"]) is None:
            raise ValueError("Administrative unit not found")

    for key, value in changes.items():
        setattr(ward, key, value)

    db.add(ward)
    db.commit()
    db.refresh(ward)
    return ward


def delete_ward(db: Session, ward_code: str) -> None:
    ward = get_ward(db, ward_code)
    db.delete(ward)
    db.commit()
