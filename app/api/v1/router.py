from fastapi import APIRouter, Depends

from app.api.v1.endpoints import (
	administrative_regions,
	administrative_units,
	health,
	provinces,
	wards,
)
from app.core.security import enforce_api_key_for_non_get

api_router = APIRouter(dependencies=[Depends(enforce_api_key_for_non_get)])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(
	administrative_regions.router,
	prefix="/administrative-regions",
	tags=["administrative-regions"],
)
api_router.include_router(
	administrative_units.router,
	prefix="/administrative-units",
	tags=["administrative-units"],
)
api_router.include_router(provinces.router, prefix="/provinces", tags=["provinces"])
api_router.include_router(wards.router, prefix="/wards", tags=["wards"])
