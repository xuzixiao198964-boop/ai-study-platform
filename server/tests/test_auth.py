"""TC-AUTH-xxx: 认证接口"""
import pytest


@pytest.mark.asyncio
async def test_auth_register_login_me(client, unique_username):
    reg = await client.post(
        "/api/v1/auth/register",
        json={"username": unique_username, "password": "secret12", "nickname": "n1"},
    )
    assert reg.status_code == 200, reg.text
    token = reg.json()["access_token"]

    dup = await client.post(
        "/api/v1/auth/register",
        json={"username": unique_username, "password": "secret12"},
    )
    assert dup.status_code == 400

    bad_login = await client.post(
        "/api/v1/auth/login",
        json={
            "username": unique_username,
            "password": "wrongpass",
            "device_type": "student_ipad",
        },
    )
    assert bad_login.status_code == 401

    ok = await client.post(
        "/api/v1/auth/login",
        json={
            "username": unique_username,
            "password": "secret12",
            "device_type": "student_ipad",
            "device_name": "pytest",
        },
    )
    assert ok.status_code == 200
    token2 = ok.json()["access_token"]

    me = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert me.status_code == 200
    assert me.json()["username"] == unique_username


@pytest.mark.asyncio
async def test_auth_register_password_too_short(client, unique_username):
    r = await client.post(
        "/api/v1/auth/register",
        json={"username": unique_username, "password": "12345"},
    )
    assert r.status_code == 422
