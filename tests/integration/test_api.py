import pytest
from httpx import AsyncClient

BASE = "/api/v1/shorten"
SAMPLE_URL = "https://www.example.com/some/long/url"
UPDATED_URL = "https://www.example.com/some/updated/url"


async def _create_url(client: AsyncClient, url: str = SAMPLE_URL) -> dict:
    resp = await client.post(BASE, json={"url": url})
    assert resp.status_code == 201
    return resp.json()

@pytest.mark.asyncio
class TestCreateShortUrl:
    async def test_returns_201_with_body(self, client):
        resp = await client.post(BASE, json={"url": SAMPLE_URL})

        assert resp.status_code == 201
        data = resp.json()
        assert data["url"] == SAMPLE_URL
        assert "shortCode" in data
        assert "id" in data
        assert "createdAt" in data
        assert "updatedAt" in data

    async def test_short_code_is_6_chars(self, client):
        data = await _create_url(client)
        assert len(data["shortCode"]) == 6

    async def test_two_requests_yield_different_codes(self, client):
        d1 = await _create_url(client)
        d2 = await _create_url(client)
        assert d1["shortCode"] != d2["shortCode"]

    async def test_missing_url_returns_422(self, client):
        resp = await client.post(BASE, json={})
        assert resp.status_code == 422

    async def test_invalid_url_returns_422(self, client):
        resp = await client.post(BASE, json={"url": "not-a-url"})
        assert resp.status_code == 422

    async def test_empty_string_url_returns_422(self, client):
        resp = await client.post(BASE, json={"url": ""})
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestGetShortUrl:
    async def test_returns_200_with_correct_data(self, client):
        created = await _create_url(client)
        resp = await client.get(f"{BASE}/{created['shortCode']}")

        assert resp.status_code == 200
        data = resp.json()
        assert data["url"] == SAMPLE_URL
        assert data["shortCode"] == created["shortCode"]

    async def test_increments_access_count_on_each_call(self, client):
        created = await _create_url(client)
        code = created["shortCode"]

        await client.get(f"{BASE}/{code}")
        await client.get(f"{BASE}/{code}")
        stats = await client.get(f"{BASE}/{code}/stats")

        assert stats.json()["accessCount"] == 2

    async def test_unknown_code_returns_404(self, client):
        resp = await client.get(f"{BASE}/xxxxxx")
        assert resp.status_code == 404

    async def test_response_contains_all_fields(self, client):
        created = await _create_url(client)
        resp = await client.get(f"{BASE}/{created['shortCode']}")
        data = resp.json()

        for field in ("id", "url", "shortCode", "createdAt", "updatedAt"):
            assert field in data, f"Missing field: {field}"


@pytest.mark.asyncio
class TestUpdateShortUrl:
    async def test_returns_200_with_updated_url(self, client):
        created = await _create_url(client)
        resp = await client.put(
            f"{BASE}/{created['shortCode']}",
            json={"url": UPDATED_URL},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["url"] == UPDATED_URL
        assert data["shortCode"] == created["shortCode"]

    async def test_updated_at_changes(self, client):
        created = await _create_url(client)
        resp = await client.put(
            f"{BASE}/{created['shortCode']}",
            json={"url": UPDATED_URL},
        )
        assert resp.json()["updatedAt"] >= created["updatedAt"]

    async def test_unknown_code_returns_404(self, client):
        resp = await client.put(f"{BASE}/xxxxxx", json={"url": UPDATED_URL})
        assert resp.status_code == 404

    async def test_invalid_url_returns_422(self, client):
        created = await _create_url(client)
        resp = await client.put(
            f"{BASE}/{created['shortCode']}",
            json={"url": "bad-url"},
        )
        assert resp.status_code == 422

    async def test_missing_body_returns_422(self, client):
        created = await _create_url(client)
        resp = await client.put(f"{BASE}/{created['shortCode']}", json={})
        assert resp.status_code == 422


# ── DELETE /shorten/{short_code} ──────────────────────────────────────────────

@pytest.mark.asyncio
class TestDeleteShortUrl:
    async def test_returns_204_on_success(self, client):
        created = await _create_url(client)
        resp = await client.delete(f"{BASE}/{created['shortCode']}")
        assert resp.status_code == 204
        assert resp.content == b""

    async def test_deleted_url_is_not_retrievable(self, client):
        created = await _create_url(client)
        await client.delete(f"{BASE}/{created['shortCode']}")

        resp = await client.get(f"{BASE}/{created['shortCode']}")
        assert resp.status_code == 404

    async def test_unknown_code_returns_404(self, client):
        resp = await client.delete(f"{BASE}/xxxxxx")
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestGetShortUrlStats:
    async def test_returns_200_with_access_count_field(self, client):
        created = await _create_url(client)
        resp = await client.get(f"{BASE}/{created['shortCode']}/stats")

        assert resp.status_code == 200
        assert "accessCount" in resp.json()

    async def test_initial_access_count_is_zero(self, client):
        created = await _create_url(client)
        resp = await client.get(f"{BASE}/{created['shortCode']}/stats")

        assert resp.json()["accessCount"] == 0

    async def test_access_count_reflects_get_calls(self, client):
        created = await _create_url(client)
        code = created["shortCode"]

        for _ in range(5):
            await client.get(f"{BASE}/{code}")

        resp = await client.get(f"{BASE}/{code}/stats")
        assert resp.json()["accessCount"] == 5

    async def test_stats_does_not_increment_counter(self, client):
        created = await _create_url(client)
        code = created["shortCode"]

        await client.get(f"{BASE}/{code}/stats")
        await client.get(f"{BASE}/{code}/stats")
        resp = await client.get(f"{BASE}/{code}/stats")

        assert resp.json()["accessCount"] == 0

    async def test_unknown_code_returns_404(self, client):
        resp = await client.get(f"{BASE}/xxxxxx/stats")
        assert resp.status_code == 404

    async def test_response_contains_all_expected_fields(self, client):
        created = await _create_url(client)
        resp = await client.get(f"{BASE}/{created['shortCode']}/stats")
        data = resp.json()

        for field in ("id", "url", "shortCode", "createdAt", "updatedAt", "accessCount"):
            assert field in data, f"Missing field: {field}"


