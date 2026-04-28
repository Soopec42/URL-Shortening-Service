from fastapi import APIRouter,  Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ShortCodeCollisionError
from app.db.session import get_db
from app.schemas.short_url import (
    ShortUrlResponse,
    ShortUrlStatsResponse,
    UrlCreateRequest,
)
from app.services.url_shortener import UrlShortenerService

router = APIRouter(prefix="/shorten", tags=["Short URLs"])

_service = UrlShortenerService()

@router.post(
    "",
    response_model=ShortUrlResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new short URL",
)
async def create_short_url(
    body: UrlCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> ShortUrlResponse:
    try:
        dto = await _service.create(db, str(body.url))
    except ShortCodeCollisionError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    return dto.to_response()


@router.get(
    "/{short_code}",
    response_model=ShortUrlResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve Original URL",
)
async def get_short_url(
    short_code: str,
    db: AsyncSession = Depends(get_db),
) -> ShortUrlResponse:
    try:
        dto = await _service.get_by_code(db, short_code)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return dto.to_response()


@router.put(
    "/{short_code}",
    response_model=ShortUrlResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Short URL",
)
async def update_short_url(
    short_code: str,
    body: UrlCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> ShortUrlResponse:
    try:
        dto = await _service.update(db, short_code, str(body.url))
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return dto.to_response()


@router.delete(
    "/{short_code}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Short URL",
)
async def delete_short_url(
    short_code: str,
    db: AsyncSession = Depends(get_db),
) -> Response:
    try:
        await _service.delete(db, short_code)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{short_code}/stats",
    response_model=ShortUrlStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get URL Statistics",
)
async def get_short_url_stats(
    short_code: str,
    db: AsyncSession = Depends(get_db),
) -> ShortUrlStatsResponse:
    try:
        dto = await _service.get_stats(db, short_code)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return dto.to_stats_response()



