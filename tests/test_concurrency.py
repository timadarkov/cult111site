import asyncio
import threading

from app.auth import utils


async def test_login_does_not_block_event_loop(
    client,
    regular_user,
    monkeypatch,
):
    started = threading.Event()
    finished = threading.Event()
    release = threading.Event()

    original_verify = utils.verify_password

    def slow_verify(password, hashed_password):
        started.set()

        try:
            release.wait(timeout=5)
            return original_verify(password, hashed_password)
        finally:
            finished.set()

    monkeypatch.setattr(
        utils,
        "verify_password",
        slow_verify,
    )

    login_task = asyncio.create_task(
        client.post(
            "/api/v1/auth/login",
            json={
                "username": regular_user.username,
                "password": "Test12345!",
            },
        )
    )

    try:
        assert await asyncio.to_thread(started.wait, 5)

        response = await client.get("/health")

        assert response.status_code == 200
        assert not finished.is_set()

    finally:
        release.set()
        login_response = await login_task

    assert login_response.status_code == 200


async def test_r2_does_not_block_event_loop(
    client,
    admin_headers,
    r2_mock,
):
    started = threading.Event()
    finished = threading.Event()
    release = threading.Event()

    def slow_head_object(**kwargs):
        started.set()

        try:
            release.wait(timeout=5)

            return {
                "ContentType": "text/plain",
                "ContentLength": 100,
            }
        finally:
            finished.set()

    r2_mock.head_object.side_effect = slow_head_object

    register_task = asyncio.create_task(
        client.post(
            "/api/v1/admin/products/1/images",
            headers=admin_headers,
            json={"key": "products/test.png"},
        )
    )

    try:
        assert await asyncio.to_thread(started.wait, 5)

        response = await client.get("/health")

        assert response.status_code == 200
        assert not finished.is_set()

    finally:
        release.set()
        register_response = await register_task

    assert register_response.status_code == 422
    r2_mock.head_object.assert_called_once()
