from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.administrative_unit import AdministrativeUnit
from app.models.province import Province
from app.models.ward import Ward
from app.schemas.ward import WardCreate, WardRead, WardUpdate

router = APIRouter()


@router.get("", response_model=list[WardRead])
def list_wards(
    province_code: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[Ward]:
    stmt = select(Ward)
    if province_code:
        stmt = stmt.where(Ward.province_code == province_code)
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


@router.get("/{ward_code}", response_model=WardRead)
def get_ward(ward_code: str, db: Session = Depends(get_db)) -> Ward:
    ward = db.get(Ward, ward_code)
    if ward is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ward not found")
    return ward


@router.post("", response_model=WardRead, status_code=status.HTTP_201_CREATED)
def create_ward(payload: WardCreate, db: Session = Depends(get_db)) -> Ward:
    if db.get(Ward, payload.code) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ward already exists")

    if payload.province_code is not None and db.get(Province, payload.province_code) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Province not found")

    if payload.administrative_unit_id is not None:
        unit = db.get(AdministrativeUnit, payload.administrative_unit_id)
        if unit is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Administrative unit not found",
            )

    ward = Ward(**payload.model_dump())
    db.add(ward)
    db.commit()
    db.refresh(ward)
    return ward


@router.put("/{ward_code}", response_model=WardRead)
def update_ward(ward_code: str, payload: WardUpdate, db: Session = Depends(get_db)) -> Ward:
    ward = db.get(Ward, ward_code)
    if ward is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ward not found")

    changes = payload.model_dump(exclude_unset=True)
    if "province_code" in changes and changes["province_code"] is not None:
        if db.get(Province, changes["province_code"]) is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Province not found")

    if "administrative_unit_id" in changes and changes["administrative_unit_id"] is not None:
        unit = db.get(AdministrativeUnit, changes["administrative_unit_id"])
        if unit is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Administrative unit not found",
            )

    for key, value in changes.items():
        setattr(ward, key, value)

    db.add(ward)
    db.commit()
    db.refresh(ward)
    return ward


@router.delete("/{ward_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ward(ward_code: str, db: Session = Depends(get_db)) -> None:
    ward = db.get(Ward, ward_code)
    if ward is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ward not found")

    db.delete(ward)
    db.commit()
    return None
