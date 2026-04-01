"""TC-REGION-xxx: 省市区三级联动 API"""
import pytest


@pytest.mark.asyncio
async def test_provinces_list(client):
    r = await client.get("/api/v1/regions/provinces")
    assert r.status_code == 200
    provinces = r.json()
    assert isinstance(provinces, list)
    assert len(provinces) >= 31
    assert "北京市" in provinces
    assert "广东省" in provinces
    assert "新疆维吾尔自治区" in provinces


@pytest.mark.asyncio
async def test_cities_by_province(client):
    r = await client.get("/api/v1/regions/cities", params={"province": "广东省"})
    assert r.status_code == 200
    cities = r.json()
    assert "广州市" in cities
    assert "深圳市" in cities


@pytest.mark.asyncio
async def test_cities_unknown_province(client):
    r = await client.get("/api/v1/regions/cities", params={"province": "不存在省"})
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_districts_by_city(client):
    r = await client.get(
        "/api/v1/regions/districts",
        params={"province": "北京市", "city": "北京市"},
    )
    assert r.status_code == 200
    districts = r.json()
    assert "海淀区" in districts
    assert "朝阳区" in districts


@pytest.mark.asyncio
async def test_districts_unknown_city(client):
    r = await client.get(
        "/api/v1/regions/districts",
        params={"province": "北京市", "city": "不存在市"},
    )
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_init_setup_with_region_fields(client, unique_username, monkeypatch):
    async def fake_chat_json(*_a, **_k):
        return {"subjects": []}
    monkeypatch.setattr(
        "app.api.endpoints.initialization.ai_service._chat_json",
        fake_chat_json,
    )

    reg = await client.post(
        "/api/v1/auth/register",
        json={"username": unique_username, "password": "secret12"},
    )
    assert reg.status_code == 200
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    setup = await client.post(
        "/api/v1/init/setup",
        headers=headers,
        json={
            "grade": 3,
            "province": "广东省",
            "city": "深圳市",
            "district": "南山区",
        },
    )
    assert setup.status_code == 200, setup.text
    data = setup.json()
    assert data["province"] == "广东省"
    assert data["city"] == "深圳市"
    assert data["district"] == "南山区"
    assert data["region"] == "广东省 深圳市 南山区"

    profile = await client.get("/api/v1/init/profile", headers=headers)
    assert profile.status_code == 200
    p = profile.json()
    assert p["province"] == "广东省"
    assert p["city"] == "深圳市"
    assert p["district"] == "南山区"
