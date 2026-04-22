import string
import secrets
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_setting
from app.core.exceptions import NotFoundError, ShortCodeCollisionError
from app.models.short_url import ShortUrl
from app.schemas.short_url import ShortUrlDTO

_ALPHABET = string.ascii_letters + string.digits
_MAX_RETRIES = 5


def _generate_short_code(length: int) -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(length))


class UrlShortenerService:

    def __init__(self, setting = None):
        self._setting = setting or get_setting()


    async def _get_by_code(self, session: AsyncSession, short_code: str) -> ShortUrl:
        result = await session.execute(
            select(ShortUrl).where(ShortUrl.shortCode == short_code)
        )
        obj = result.scalar_one_or_none()
        if obj is None:
            raise NotFoundError(short_code)
        return obj

    async def _unique_short_code(self, session: AsyncSession) -> str:
        length = self._setting.short_code_length
        for _ in range(_MAX_RETRIES):
            code = _generate_short_code(length)
            result = await session.execute(
                select(ShortUrl.id).where(ShortUrl.shortCode == code)
            )
            if result.scalar_one_or_none() is None:
                return code
        raise ShortCodeCollisionError()


    async def create(self, session: AsyncSession, url: str) -> ShortUrlDTO:
        short_code = await self._unique_short_code(session)
        now = datetime.now(timezone.utc)
        obj = ShortUrl(
            url = url,
            short_code=short_code,
            access_count=0,
            created_at = now,
            updated_at = now,
        )
        session.add(obj)
        await session.flush()
        await session.refresh(obj)
        return ShortUrlDTO.model_validate(obj)


    async def get_by_code(self, session: AsyncSession, short_code: str) -> ShortUrlDTO:
        obj = await self._get_by_code(session, short_code)

        await session.execute(
            update(ShortUrl).where(ShortUrl.id == obj.id).values(access_count=ShortUrl.access_count + 1)
        )
        return ShortUrlDTO.model_validate(obj)


    async def update(self, session: AsyncSession, short_code: str, url: str) -> ShortUrlDTO:
        obj = await self._get_by_code(session, short_code)
        obj.url = url
        obj.updatedAt = datetime.now(timezone.utc)
        await session.flush()
        await session.refresh(obj)
        return ShortUrlDTO.model_validate(obj)


    async def delete(self, session: AsyncSession, short_code: str) -> None
        obj = await self._get_by_code(session, short_code)
        await session.delete(obj)
        await session.flush()


    async def get_stats(self, session: AsyncSession, short_code: str) -> ShortUrlDTO:
        obj = await self._get_by_code(session, short_code)
        return ShortUrlDTO.model_validate(obj)


