from collections.abc import Generator
from functools import lru_cache
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


UNSUPPORTED_DB_URL_OPTIONS = {"supa"}


def _normalize_database_url(database_url: str) -> str:
    normalized_url = database_url

    if normalized_url.startswith("postgres://"):
        normalized_url = normalized_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif normalized_url.startswith("postgresql://"):
        normalized_url = normalized_url.replace("postgresql://", "postgresql+psycopg://", 1)

    parsed_url = urlsplit(normalized_url)
    query_params = parse_qsl(parsed_url.query, keep_blank_values=True)
    filtered_query_params = [
        (key, value)
        for key, value in query_params
        if key.lower() not in UNSUPPORTED_DB_URL_OPTIONS
    ]

    if len(filtered_query_params) == len(query_params):
        return normalized_url

    return urlunsplit(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            urlencode(filtered_query_params, doseq=True),
            parsed_url.fragment,
        )
    )


@lru_cache(maxsize=1)
def get_engine():
    normalized_url = _normalize_database_url(settings.DATABASE_URL)
    return create_engine(normalized_url, pool_pre_ping=True)


@lru_cache(maxsize=1)
def get_session_local() -> sessionmaker:
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def get_db() -> Generator[Session, None, None]:
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()
