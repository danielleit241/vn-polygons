from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
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


@app.get("/", tags=["root"], include_in_schema=False)
def read_root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


app.include_router(api_router, prefix=settings.API_V1_PREFIX)
