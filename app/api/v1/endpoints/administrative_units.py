from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.administrative_unit import AdministrativeUnit
from app.schemas.administrative_unit import (
    AdministrativeUnitCreate,
    AdministrativeUnitRead,
    AdministrativeUnitUpdate,
)

router = APIRouter()


@router.get("", response_model=list[AdministrativeUnitRead])
def list_units(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[AdministrativeUnit]:
    stmt = select(AdministrativeUnit).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


@router.get("/{unit_id}", response_model=AdministrativeUnitRead)
def get_unit(unit_id: int, db: Session = Depends(get_db)) -> AdministrativeUnit:
    unit = db.get(AdministrativeUnit, unit_id)
    if unit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")
    return unit


@router.post("", response_model=AdministrativeUnitRead, status_code=status.HTTP_201_CREATED)
def create_unit(payload: AdministrativeUnitCreate, db: Session = Depends(get_db)) -> AdministrativeUnit:
    if db.get(AdministrativeUnit, payload.id) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unit already exists")

    unit = AdministrativeUnit(**payload.model_dump())
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit


@router.put("/{unit_id}", response_model=AdministrativeUnitRead)
def update_unit(unit_id: int, payload: AdministrativeUnitUpdate, db: Session = Depends(get_db)) -> AdministrativeUnit:
    unit = db.get(AdministrativeUnit, unit_id)
    if unit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(unit, key, value)

    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit


@router.delete("/{unit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_unit(unit_id: int, db: Session = Depends(get_db)) -> None:
    unit = db.get(AdministrativeUnit, unit_id)
    if unit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")

    db.delete(unit)
    db.commit()
    return None
