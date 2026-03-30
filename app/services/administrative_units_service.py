from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.administrative_unit import AdministrativeUnit
from app.schemas.administrative_unit import AdministrativeUnitCreate, AdministrativeUnitUpdate


def list_units(db: Session, skip: int = 0, limit: int = 20) -> list[AdministrativeUnit]:
    stmt = select(AdministrativeUnit).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_unit(db: Session, unit_id: int) -> AdministrativeUnit:
    unit = db.get(AdministrativeUnit, unit_id)
    if unit is None:
        raise LookupError("Unit not found")
    return unit


def create_unit(db: Session, payload: AdministrativeUnitCreate) -> AdministrativeUnit:
    if db.get(AdministrativeUnit, payload.id) is not None:
        raise ValueError("Unit already exists")

    unit = AdministrativeUnit(**payload.model_dump())
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit


def update_unit(db: Session, unit_id: int, payload: AdministrativeUnitUpdate) -> AdministrativeUnit:
    unit = get_unit(db, unit_id)

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(unit, key, value)

    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit


def delete_unit(db: Session, unit_id: int) -> None:
    unit = get_unit(db, unit_id)
    db.delete(unit)
    db.commit()
