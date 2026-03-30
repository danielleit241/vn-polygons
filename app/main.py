from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.models import AdministrativeRegion, AdministrativeUnit, Province, Ward  # noqa: F401

app = FastAPI(title=settings.APP_NAME)


@app.get("/", tags=["root"], include_in_schema=False)
def read_root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


app.include_router(api_router, prefix=settings.API_V1_PREFIX)
