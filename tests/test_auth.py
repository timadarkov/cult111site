from datetime import datetime, timedelta, timezone

from app.auth import utils
from app.auth.utils import decode_jwt, encode_jwt
from app.core.config import settings


async def test_inactive_user_access_token(
    client, db_session, user_factory
):
    admin = await user_factory(
        username="test_admin",
        is_active=True,
        is_admin=True,
    )

    access_token = utils.create_token(
        user_id=admin.id,
        token_type="access",
        token_expire_minutes=30,
    )

    admin.is_active = False
    await db_session.flush()

    response = await client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "User not found or inactive"


async def test_inactive_user_login(client, user_factory):

    await user_factory(
        username="blocked_admin",
        password="Test12345!",
        is_active=False,
        is_admin=True,
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "blocked_admin",
            "password": "Test12345!",
        },
    )

    assert response.status_code == 401
    assert "access_token" not in response.json()
    assert "refresh_token" not in response.json()
    assert response.json()["detail"] == "Invalid username or password"


async def test_inactive_user_refresh(client, db_session, user_factory):

    admin = await user_factory(
        username="refresh_admin",
        is_active=True,
        is_admin=True,
    )

    refresh_token = utils.create_token(
        user_id=admin.id,
        token_type="refresh",
        token_expire_minutes=60,
    )

    admin.is_active = False
    await db_session.flush()

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 401
    assert "access_token" not in response.json()
    assert "refresh_token" not in response.json()
    assert response.json()["detail"] == "Invalid or expired refresh token"


async def test_access_token_without_sub(client):

    token = encode_jwt(
        payload={
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
            "iat": datetime.now(timezone.utc),
        }
    )

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired access token"


async def test_admin_deactivates_another_user(client, db_session, user_factory):

    admin = await user_factory(
        username="main_admin",
        is_active=True,
        is_admin=True,
    )

    target = await user_factory(
        username="target_admin",
        is_active=True,
        is_admin=True,
    )

    access_token = utils.create_token(
        user_id=admin.id,
        token_type="access",
        token_expire_minutes=30,
    )

    response = await client.patch(
        f"/api/v1/admin/users/{target.id}/activity",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200

    await db_session.refresh(target)
    assert target.is_active is False


async def test_admin_cannot_deactivate_self(client, db_session, user_factory):

    admin = await user_factory(
        username="self_admin",
        is_active=True,
        is_admin=True,
    )

    access_token = utils.create_token(
        user_id=admin.id,
        token_type="access",
        token_expire_minutes=30,
    )

    response = await client.patch(
        f"/api/v1/admin/users/{admin.id}/activity",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 403

    await db_session.refresh(admin)
    assert admin.is_active is True


async def test_active_admin_access(client, user_factory):

    admin = await user_factory(
        username="active_admin",
        is_active=True,
        is_admin=True,
    )

    access_token = utils.create_token(
        user_id=admin.id,
        token_type="access",
        token_expire_minutes=30,
    )

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == admin.id


async def test_regular_user_cannot_deactivate(client, db_session, user_factory):

    regular_user = await user_factory(
        username="regular_user",
        is_active=True,
        is_admin=False,
    )

    target = await user_factory(
        username="target_user",
        is_active=True,
        is_admin=False,
    )

    access_token = utils.create_token(
        user_id=regular_user.id,
        token_type="access",
        token_expire_minutes=30,
    )

    response = await client.patch(
        f"/api/v1/admin/users/{target.id}/activity",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 403

    await db_session.refresh(target)
    assert target.is_active is True


async def test_deactivate_nonexistent_user(client, user_factory):

    admin = await user_factory(
        username="admin_not_found",
        is_active=True,
        is_admin=True,
    )

    access_token = utils.create_token(
        user_id=admin.id,
        token_type="access",
        token_expire_minutes=30,
    )

    response = await client.patch(
        "/api/v1/admin/users/99999999/activity",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


async def test_refresh_token_without_sub(client):

    token = utils.encode_jwt(
        payload={
            "type": "refresh",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
            "iat": datetime.now(timezone.utc),
        }
    )

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": token},
    )

    assert response.status_code == 401


async def test_login_success(client, regular_user):
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": regular_user.username,
            "password": "Test12345!",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert "password" not in data
    assert "password_hash" not in data
    assert data["token_type"] == "bearer"

    payload = decode_jwt(
        data["access_token"],
        expected_type="access",
    )

    assert payload["sub"] == str(regular_user.id)


async def test_login_wrong_password(client, regular_user):
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": regular_user.username,
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


async def test_login_nonexistent_user(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "wrongusername",
            "password": "WrongPassword1232!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


async def test_me_without_token(client):
    response = await client.get(
        "/api/v1/auth/me",
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


async def test_me_invalid_token(client):

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer random_access_token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired access token"


async def test_me_expired_token(client, regular_user):
    access_token = utils.create_token(
        user_id=regular_user.id,
        token_type="access",
        token_expire_minutes=-1,
    )

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired access token"


async def test_regular_user_cannot_access_admin(client, regular_user_headers):
    response = await client.get(
        "/api/v1/admin/users",
        headers=regular_user_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


async def test_admin_can_access_admin(client, admin_headers):

    response = await client.get(
        "/api/v1/admin/users",
        headers=admin_headers,
    )

    assert response.status_code == 200


async def test_refresh_success(client, regular_user):
    refresh_token = utils.create_token(
        user_id=regular_user.id,
        token_type="refresh",
        token_expire_minutes=settings.auth_jwt.refresh_token_expire_minutes,
    )

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_refresh_with_access_token(client, regular_user):
    access_token = utils.create_token(
        user_id=regular_user.id,
        token_type="access",
        token_expire_minutes=settings.auth_jwt.access_token_expire_minutes,
    )

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": access_token},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired refresh token"
