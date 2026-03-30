from contextlib import asynccontextmanager
from pathlib import Path
from secrets import compare_digest

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import get_engine
from app.models import AdministrativeRegion, AdministrativeUnit, Province, Ward  # noqa: F401
from app.models.base import Base

_SEED_SQL = Path(__file__).parent.parent / "sql" / "seed-data.sql"


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM administrative_regions")).scalar()
        if count == 0:
            conn.execute(text(_SEED_SQL.read_text(encoding="utf-8")))
            conn.commit()
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)


@app.middleware("http")
async def enforce_api_key_for_non_get(request: Request, call_next):
    method = request.method.upper()
    if method in {"GET", "HEAD", "OPTIONS"}:
        return await call_next(request)

    provided_key = request.headers.get("X-API-Key")
    if not provided_key or not compare_digest(provided_key, settings.API_KEY):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid or missing API key"},
        )

    return await call_next(request)


@app.get("/", tags=["root"], include_in_schema=False)
def read_root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


app.include_router(api_router, prefix=settings.API_V1_PREFIX)
