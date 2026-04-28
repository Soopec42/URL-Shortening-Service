import pytest
import pytest_asyncio

from app.core.exceptions import NotFoundError, ShortCodeCollisionError
from app.services.url_shortener import UrlShortenerService, _generate_short_code

SAMPLE_URL = "https://www.example.com/some/long/url"
UPDATED_URL = "https://www.example.com/some/updated/url"


class TestGenerateShortCode:
    def test_returns_correct_length(self):
        code = _generate_short_code(6)
        assert len(code) == 6

    def test_returns_alphanumeric_only(self):
        code = _generate_short_code(10)
        assert code.isalnum()

    def test_different_codes_each_call(self):
        codes = {_generate_short_code(8) for _ in range(50)}
        assert len(codes) > 1

@pytest.mark.asyncio
class TestUrlShortenerServiceCreate:
    async def test_create_returns_dto_with_correct_url(self, db_session):
        svc = UrlShortenerService()
        dto = await svc.create(db_session, SAMPLE_URL)

        assert dto.url == SAMPLE_URL
        assert dto.id is not None
        assert len(dto.short_code) == 6
        assert dto.access_count == 0

    async def test_create_generates_unique_codes(self, db_session):
        svc = UrlShortenerService()
        dto1 = await svc.create(db_session, SAMPLE_URL)
        dto2 = await svc.create(db_session, SAMPLE_URL)

        assert dto1.short_code != dto2.short_code

    async def test_created_at_and_updated_at_are_set(self, db_session):
        svc = UrlShortenerService()
        dto = await svc.create(db_session, SAMPLE_URL)

        assert dto.created_at is not None
        assert dto.updated_at is not None


@pytest.mark.asyncio
class TestUrlShoortenerServiceGet:
    async def test_get_existing_code_increments_access_count(self, db_session):
        svc = UrlShortenerService()
        created = await svc.create(db_session, SAMPLE_URL)

        res1 = await svc.get_by_code(db_session, created.short_code)
        res2 = await svc.get_by_code(db_session, created.short_code)

        assert res1.access_count == 1
        assert res2.access_count == 2

    async def test_get_returns_correct_url(self, db_session):
        svc = UrlShortenerService()
        created = await svc.create(db_session, SAMPLE_URL)

        res = await svc.get_by_code(db_session, created.short_code)
        assert res.url == SAMPLE_URL

    async def test_get_unknown_code_raises_not_found(self, db_session):
        svc = UrlShortenerService()
        with pytest.raises(NotFoundError):
            await svc.get_by_code(db_session, "nonexistent")


@pytest.mark.asyncio
class TestUrlShortenerServiceUpdate:
    async def test_update_changes_url(self, db_session):
        svc = UrlShortenerService()
        created = await svc.create(db_session, SAMPLE_URL)

        updated = await svc.update(db_session, created.short_code, UPDATED_URL)

        assert updated.url == UPDATED_URL
        assert updated.short_code == created.short_code

    async def test_update_bumps_updated_at(self, db_session):
        svc = UrlShortenerService()
        created = await svc.create(db_session, SAMPLE_URL)
        original_updated_at = created.updated_at

        updated = await svc.update(db_session, created.short_code, UPDATED_URL)

        assert updated.updated_at >= original_updated_at

    async def test_update_unknown_code_raises_not_found(self, db_session):
        svc = UrlShortenerService()
        with pytest.raises(NotFoundError):
            await svc.update(db_session, "nonexistent", UPDATED_URL)


@pytest.mark.asyncio
class TestUrlShortenerServiceDelete:
    async def test_delete_removes_record(self, db_session):
        svc = UrlShortenerService()
        created = await svc.create(db_session, SAMPLE_URL)
        await svc.delete(db_session, created.short_code)

        with pytest.raises(NotFoundError):
            await svc.get_by_code(db_session, created.short_code)

    async def test_delete_unknown_code_raises_not_found(self, db_session):
        svc = UrlShortenerService()
        with pytest.raises(NotFoundError):
            await svc.delete(db_session, "ghost")


@pytest.mark.asyncio
class TestUrlShortenerServiceStats:
    async def test_stats_does_not_increment_counter(self, db_session):
        svc = UrlShortenerService()
        created = await svc.create(db_session, SAMPLE_URL)

        stats1 = await svc.get_stats(db_session, created.short_code)
        stats2 = await svc.get_stats(db_session, created.short_code)

        assert stats1.access_count == 0
        assert stats2.access_count == 0

    async def test_stats_unknown_code_raises_not_found(self, db_session):
        svc = UrlShortenerService()
        with pytest.raises(NotFoundError):
            await svc.get_stats(db_session, "nobody")





