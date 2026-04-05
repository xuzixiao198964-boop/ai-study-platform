"""集成测试：对部署环境 HTTP 冒烟（需设置 INTEGRATION_BASE_URL）。"""
import os

import httpx
import pytest

INTEGRATION_BASE_URL = os.getenv("INTEGRATION_BASE_URL", "").rstrip("/")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_remote_health():
    if not INTEGRATION_BASE_URL:
        pytest.skip("INTEGRATION_BASE_URL 未设置")

    async with httpx.AsyncClient(timeout=20.0, verify=False) as client:
        # 测试后端直接端口（8001）或通过API路径
        r = await client.get(f"{INTEGRATION_BASE_URL}/api/v1/health")
        if r.status_code == 404:
            # 如果API路径不存在，尝试直接访问根路径（可能是8001端口）
            base_url = INTEGRATION_BASE_URL.replace(":8000", ":8001").replace("https://", "http://")
            r = await client.get(f"{base_url}/health")
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") == "ok"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_remote_admin_login():
    if not INTEGRATION_BASE_URL:
        pytest.skip("INTEGRATION_BASE_URL 未设置")

    user = os.getenv("INTEGRATION_ADMIN_USER", "wsxzx")
    pwd = os.getenv("INTEGRATION_ADMIN_PASSWORD", "")
    if not pwd:
        pytest.skip("INTEGRATION_ADMIN_PASSWORD 未设置")

    async with httpx.AsyncClient(timeout=20.0, verify=False) as client:
        r = await client.post(
            f"{INTEGRATION_BASE_URL}/api/v1/admin/login",
            json={"username": user, "password": pwd},
        )
        assert r.status_code == 200
        assert "access_token" in r.json()
