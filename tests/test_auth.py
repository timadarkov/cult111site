from app.auth import utils
import jwt
from datetime import datetime, timedelta, timezone
from app.auth.utils import encode_jwt
from app.core.config import settings
from app.auth.utils import decode_jwt


def test_inactive_user_access_token(client, db_session, user_factory):
    admin = user_factory(
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
    db_session.flush()

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    assert response.status_code == 401


def test_inactive_user_login(client, user_factory):

    user_factory(
        username="blocked_admin",
        password="Test12345!",
        is_active=False,
        is_admin=True,
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "blocked_admin",
            "password": "Test12345!",
        },
    )

    assert response.status_code == 401
    assert "access_token" not in response.json()
    assert "refresh_token" not in response.json()


def test_inactive_user_refresh(client, db_session, user_factory):

    admin = user_factory(
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
    db_session.flush()

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 401
    assert "access_token" not in response.json()
    assert "refresh_token" not in response.json()


def test_access_token_without_sub(client):

    token = encode_jwt(
        payload={
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
            "iat": datetime.now(timezone.utc),
        }
    )

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_admin_deactivates_another_user(client, db_session, user_factory):

    admin = user_factory(
        username="main_admin",
        is_active=True,
        is_admin=True,
    )

    target = user_factory(
        username="target_admin",
        is_active=True,
        is_admin=True,
    )

    access_token = utils.create_token(
        user_id=admin.id,
        token_type="access",
        token_expire_minutes=30,
    )

    response = client.patch(
        f"/api/v1/admin/users/{target.id}/activity",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200

    db_session.refresh(target)
    assert target.is_active is False


def test_admin_cannot_deactivate_self(client, db_session, user_factory):

    admin = user_factory(
        username="self_admin",
        is_active=True,
        is_admin=True,
    )

    access_token = utils.create_token(
        user_id=admin.id,
        token_type="access",
        token_expire_minutes=30,
    )

    response = client.patch(
        f"/api/v1/admin/users/{admin.id}/activity",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 403

    db_session.refresh(admin)
    assert admin.is_active is True


def test_active_admin_access(client, user_factory):

    admin = user_factory(
        username="active_admin",
        is_active=True,
        is_admin=True,
    )

    access_token = utils.create_token(
        user_id=admin.id,
        token_type="access",
        token_expire_minutes=30,
    )

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == admin.id


def test_regular_user_cannot_deactivate(client, db_session, user_factory):

    regular_user = user_factory(
        username="regular_user",
        is_active=True,
        is_admin=False,
    )

    target = user_factory(
        username="target_user",
        is_active=True,
        is_admin=False,
    )

    access_token = utils.create_token(
        user_id=regular_user.id,
        token_type="access",
        token_expire_minutes=30,
    )

    response = client.patch(
        f"/api/v1/admin/users/{target.id}/activity",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 403

    db_session.refresh(target)
    assert target.is_active is True


def test_deactivate_nonexistent_user(client, user_factory):

    admin = user_factory(
        username="admin_not_found",
        is_active=True,
        is_admin=True,
    )

    access_token = utils.create_token(
        user_id=admin.id,
        token_type="access",
        token_expire_minutes=30,
    )

    response = client.patch(
        "/api/v1/admin/users/99999999/activity",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_refresh_token_without_sub(client):

    token = utils.encode_jwt(
        payload={
            "type": "refresh",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
            "iat": datetime.now(timezone.utc),
        }
    )

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": token},
    )

    assert response.status_code == 401


def test_login_success(client, regular_user):
    response = client.post(
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


def test_login_wrong_password(client, regular_user):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": regular_user.username,
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_login_nonexistent_user(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "wrongusername",
            "password": "WrongPassword1232!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_login_inactive_user(client, inactive_user):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": inactive_user.username,
            "password": "Test12345!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_inactive_user_token(client, inactive_user_headers):
    response = client.get(
        "/api/v1/auth/me",
        headers=inactive_user_headers,
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "User not found or inactive"


def test_me_without_token(client):
    response = client.get(
        "/api/v1/auth/me",
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_me_invalid_token(client):

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer random_access_token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired access token"


def test_me_expired_token(client, regular_user):
    access_token = utils.create_token(
        user_id=regular_user.id,
        token_type="access",
        token_expire_minutes=-1,
    )

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired access token"


def test_me_token_without_sub(client):
    payload = {
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }

    token = utils.encode_jwt(payload)

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired access token"


def test_regular_user_cannot_access_admin(client, regular_user_headers):
    response = client.get(
        "/api/v1/admin/users",
        headers=regular_user_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_admin_can_access_admin(client, admin_headers):

    response = client.get(
        "/api/v1/admin/users",
        headers=admin_headers,
    )

    assert response.status_code == 200


def test_refresh_success(client, regular_user):
    refresh_token = utils.create_token(
        user_id=regular_user.id,
        token_type="refresh",
        token_expire_minutes=settings.auth_jwt.refresh_token_expire_minutes,
    )

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_inactive_user(client, inactive_user):
    refresh_token = utils.create_token(
        user_id=inactive_user.id,
        token_type="refresh",
        token_expire_minutes=settings.auth_jwt.refresh_token_expire_minutes,
    )

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired refresh token"


def test_refresh_with_access_token(client, regular_user):
    access_token = utils.create_token(
        user_id=regular_user.id,
        token_type="access",
        token_expire_minutes=settings.auth_jwt.access_token_expire_minutes,
    )

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": access_token},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired refresh token"
