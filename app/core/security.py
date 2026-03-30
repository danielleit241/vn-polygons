from secrets import compare_digest

from fastapi import Header, HTTPException, Request, status

from app.core.config import settings


def enforce_api_key_for_non_get(
    request: Request,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    method = request.method.upper()
    if method in {"GET", "HEAD", "OPTIONS"}:
        return

    if not x_api_key or not compare_digest(x_api_key, settings.API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
