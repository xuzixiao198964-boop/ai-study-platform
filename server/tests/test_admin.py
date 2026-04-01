"""TC-ADMIN-xxx: 管理后台 API"""
import os

import pytest

ADMIN_USER = os.environ.get("ADMIN_USERNAME", "wsxzx")
ADMIN_PASS = os.environ.get("ADMIN_PASSWORD", "Xuzi-xiao198964")


@pytest.mark.asyncio
async def test_admin_login_and_stats(client, unique_username):
    bad = await client.post(
        "/api/v1/admin/login",
        json={"username": ADMIN_USER, "password": "wrong"},
    )
    assert bad.status_code == 401

    ok = await client.post(
        "/api/v1/admin/login",
        json={"username": ADMIN_USER, "password": ADMIN_PASS},
    )
    assert ok.status_code == 200
    admin_token = ok.json()["access_token"]
    ah = {"Authorization": f"Bearer {admin_token}"}

    await client.post(
        "/api/v1/auth/register",
        json={"username": unique_username, "password": "secret12"},
    )

    stats = await client.get("/api/v1/admin/stats", headers=ah)
    assert stats.status_code == 200
    s = stats.json()
    assert s["total_users"] >= 1
