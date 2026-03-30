from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.administrative_region import AdministrativeRegion
from app.schemas.administrative_region import (
    AdministrativeRegionCreate,
    AdministrativeRegionRead,
    AdministrativeRegionUpdate,
)

router = APIRouter()


@router.get("", response_model=list[AdministrativeRegionRead])
def list_regions(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[AdministrativeRegion]:
    stmt = select(AdministrativeRegion).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


@router.get("/{region_id}", response_model=AdministrativeRegionRead)
def get_region(region_id: int, db: Session = Depends(get_db)) -> AdministrativeRegion:
    region = db.get(AdministrativeRegion, region_id)
    if region is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Region not found")
    return region


@router.post("", response_model=AdministrativeRegionRead, status_code=status.HTTP_201_CREATED)
def create_region(
    payload: AdministrativeRegionCreate,
    db: Session = Depends(get_db),
) -> AdministrativeRegion:
    if db.get(AdministrativeRegion, payload.id) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Region already exists")

    region = AdministrativeRegion(**payload.model_dump())
    db.add(region)
    db.commit()
    db.refresh(region)
    return region


@router.put("/{region_id}", response_model=AdministrativeRegionRead)
def update_region(
    region_id: int,
    payload: AdministrativeRegionUpdate,
    db: Session = Depends(get_db),
) -> AdministrativeRegion:
    region = db.get(AdministrativeRegion, region_id)
    if region is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Region not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(region, key, value)

    db.add(region)
    db.commit()
    db.refresh(region)
    return region


@router.delete("/{region_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_region(region_id: int, db: Session = Depends(get_db)) -> None:
    region = db.get(AdministrativeRegion, region_id)
    if region is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Region not found")

    db.delete(region)
    db.commit()
    return None
