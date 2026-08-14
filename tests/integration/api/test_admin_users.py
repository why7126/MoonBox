from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import text

ADMIN_PASSWORD = "example-test-password"


def _admin_headers(api_client: TestClient) -> dict[str, str]:
    response = api_client.post(
        "/api/v1/auth/login",
        json={"username": "superadmin", "password": ADMIN_PASSWORD, "remember_me": False},
    )
    assert response.status_code == 200, response.text
    token = response.json()["data"]["access_token"]
    return {"authorization": f"Bearer {token}"}


def _create_user(api_client: TestClient, username: str = "chenmo") -> dict:
    response = api_client.post(
        "/api/v1/admin/users",
        headers=_admin_headers(api_client),
        json={"username": username, "nickname": "陈默", "role": "前台用户"},
    )
    assert response.status_code == 201, response.text
    data = response.json()["data"]
    return data.get("user", data)


def _create_admin_user_with_password(api_client: TestClient, username: str) -> tuple[dict, str]:
    response = api_client.post(
        "/api/v1/admin/users",
        headers=_admin_headers(api_client),
        json={"username": username, "nickname": "测试管理员", "role": "后台管理员"},
    )
    assert response.status_code == 201, response.text
    data = response.json()["data"]
    assert data["temporary_password"].startswith("Mb-")
    return data["user"], data["temporary_password"]


def test_admin_user_list_includes_protected_superadmin(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/admin/users", headers=_admin_headers(api_client))

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["total"] == 1
    superadmin = payload["items"][0]
    assert superadmin["username"] == "superadmin"
    assert superadmin["role"] == "后台管理员"
    assert superadmin["is_system_superadmin"] is True


def test_legacy_admin_avatar_urls_are_normalized_to_unified_auth_path(api_client: TestClient) -> None:
    from app.db.session import get_session_factory

    with get_session_factory()() as db:
        db.execute(
            text(
                """
                UPDATE admin_users
                SET avatar_url = '/api/v1/admin/users/avatar/legacy-avatar.webp'
                WHERE username = 'superadmin'
                """
            )
        )
        db.commit()

    login = api_client.post(
        "/api/v1/auth/login",
        json={"username": "superadmin", "password": ADMIN_PASSWORD, "remember_me": False},
    )
    assert login.status_code == 200, login.text
    token = login.json()["data"]["access_token"]
    headers = {"authorization": f"Bearer {token}"}
    expected = "/api/v1/auth/avatar/legacy-avatar.webp"

    assert login.json()["data"]["user"]["avatar_url"] == expected

    me = api_client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200, me.text
    assert me.json()["data"]["user"]["avatar_url"] == expected

    users = api_client.get("/api/v1/admin/users", headers=headers)
    assert users.status_code == 200, users.text
    assert users.json()["data"]["items"][0]["avatar_url"] == expected


def test_admin_user_create_filter_and_update(api_client: TestClient) -> None:
    created = _create_user(api_client)
    headers = _admin_headers(api_client)

    list_response = api_client.get(
        "/api/v1/admin/users",
        headers=headers,
        params={"q": "chen", "role": "前台用户", "status": "待激活"},
    )
    assert list_response.status_code == 200
    assert list_response.json()["data"]["total"] == 1

    update_response = api_client.put(
        f"/api/v1/admin/users/{created['id']}",
        headers=headers,
        json={"nickname": "陈默新", "role": "后台管理员", "avatar_url": "/avatar.png"},
    )
    assert update_response.status_code == 200
    updated = update_response.json()["data"]
    assert updated["username"] == "chenmo"
    assert updated["nickname"] == "陈默新"
    assert updated["role"] == "后台管理员"


def test_admin_user_list_hides_deleted_until_explicit_filter(api_client: TestClient) -> None:
    created = _create_user(api_client, "deleteduser")
    headers = _admin_headers(api_client)
    delete = api_client.request(
        "DELETE",
        f"/api/v1/admin/users/{created['id']}",
        headers=headers,
        json={"reason": "用户申请删除"},
    )
    assert delete.status_code == 200

    default_list = api_client.get("/api/v1/admin/users", headers=headers)
    assert default_list.status_code == 200
    default_payload = default_list.json()["data"]
    assert default_payload["total"] == 1
    assert all(item["status"] != "已删除" for item in default_payload["items"])

    deleted_list = api_client.get("/api/v1/admin/users", headers=headers, params={"status": "已删除"})
    assert deleted_list.status_code == 200
    deleted_payload = deleted_list.json()["data"]
    assert deleted_payload["total"] == 1
    assert deleted_payload["items"][0]["username"] == "deleteduser"
    assert deleted_payload["items"][0]["status"] == "已删除"


def test_admin_user_create_returns_temporary_password_that_can_login(api_client: TestClient) -> None:
    created, temporary_password = _create_admin_user_with_password(api_client, "newadmin")
    assert created["status"] == "待激活"
    login = api_client.post(
        "/api/v1/auth/login",
        json={"username": "newadmin", "password": temporary_password, "remember_me": False},
    )

    assert login.status_code == 200, login.text
    assert login.json()["data"]["access_token"]
    assert login.json()["data"]["user"]["status"] == "正常"


def test_admin_user_validates_username_and_role(api_client: TestClient) -> None:
    headers = _admin_headers(api_client)
    invalid = api_client.post(
        "/api/v1/admin/users",
        headers=headers,
        json={"username": "1bad", "nickname": "坏账号", "role": "前台用户"},
    )
    assert invalid.status_code == 422

    created = _create_user(api_client, "unique")
    duplicate = api_client.post(
        "/api/v1/admin/users",
        headers=headers,
        json={"username": created["username"], "nickname": "重复", "role": "前台用户"},
    )
    assert duplicate.status_code == 409


def test_admin_user_status_reset_and_superadmin_protection(api_client: TestClient) -> None:
    created, initial_password = _create_admin_user_with_password(api_client, "linyu")
    headers = _admin_headers(api_client)

    freeze = api_client.post(
        f"/api/v1/admin/users/{created['id']}/freeze",
        headers=headers,
        json={"reason": "安全异常处理"},
    )
    assert freeze.status_code == 200
    frozen = freeze.json()["data"]
    assert frozen["status"] == "已冻结"
    assert frozen["status_before_freeze"] == "待激活"
    assert frozen["session_invalidated_at"] is not None

    reset = api_client.post(
        f"/api/v1/admin/users/{created['id']}/reset-password",
        headers=headers,
        json={"reason": "用户申请人工重置"},
    )
    assert reset.status_code == 200
    new_password = reset.json()["data"]["temporary_password"]
    assert new_password.startswith("Mb-")
    old_login = api_client.post(
        "/api/v1/auth/login",
        json={"username": "linyu", "password": initial_password, "remember_me": False},
    )
    assert old_login.status_code == 401

    unfreeze = api_client.post(
        f"/api/v1/admin/users/{created['id']}/unfreeze",
        headers=headers,
        json={"reason": "恢复登录验证"},
    )
    assert unfreeze.status_code == 200
    assert unfreeze.json()["data"]["status"] == "待激活"
    assert unfreeze.json()["data"]["status_before_freeze"] is None
    new_login = api_client.post(
        "/api/v1/auth/login",
        json={"username": "linyu", "password": new_password, "remember_me": False},
    )
    assert new_login.status_code == 200, new_login.text

    superadmin = api_client.get("/api/v1/admin/users", headers=headers).json()["data"]["items"][0]
    blocked = api_client.post(
        f"/api/v1/admin/users/{superadmin['id']}/freeze",
        headers=headers,
        json={"reason": "误操作验证"},
    )
    assert blocked.status_code == 403


def test_admin_user_unfreeze_restores_previous_active_status(api_client: TestClient) -> None:
    created, temporary_password = _create_admin_user_with_password(api_client, "activeadmin")
    login = api_client.post(
        "/api/v1/auth/login",
        json={"username": "activeadmin", "password": temporary_password, "remember_me": False},
    )
    assert login.status_code == 200, login.text
    headers = _admin_headers(api_client)

    freeze = api_client.post(
        f"/api/v1/admin/users/{created['id']}/freeze",
        headers=headers,
        json={"reason": "临时安全管控"},
    )
    assert freeze.status_code == 200
    assert freeze.json()["data"]["status_before_freeze"] == "正常"

    repeat_freeze = api_client.post(
        f"/api/v1/admin/users/{created['id']}/freeze",
        headers=headers,
        json={"reason": "重复冻结验证"},
    )
    assert repeat_freeze.status_code == 200
    assert repeat_freeze.json()["data"]["status_before_freeze"] == "正常"

    unfreeze = api_client.post(
        f"/api/v1/admin/users/{created['id']}/unfreeze",
        headers=headers,
        json={"reason": "恢复访问"},
    )
    assert unfreeze.status_code == 200
    assert unfreeze.json()["data"]["status"] == "正常"
    assert unfreeze.json()["data"]["status_before_freeze"] is None


def test_admin_user_cannot_freeze_or_delete_self(api_client: TestClient) -> None:
    created, temporary_password = _create_admin_user_with_password(api_client, "selfguard")
    login = api_client.post(
        "/api/v1/auth/login",
        json={"username": "selfguard", "password": temporary_password, "remember_me": False},
    )
    assert login.status_code == 200, login.text
    token = login.json()["data"]["access_token"]
    headers = {"authorization": f"Bearer {token}"}

    freeze = api_client.post(
        f"/api/v1/admin/users/{created['id']}/freeze",
        headers=headers,
        json={"reason": "误操作验证"},
    )
    assert freeze.status_code == 403

    after_freeze_me = api_client.get("/api/v1/auth/me", headers=headers)
    assert after_freeze_me.status_code == 200, after_freeze_me.text
    assert after_freeze_me.json()["data"]["user"]["status"] == "正常"

    delete = api_client.request(
        "DELETE",
        f"/api/v1/admin/users/{created['id']}",
        headers=headers,
        json={"reason": "误操作验证"},
    )
    assert delete.status_code == 403

    after_delete_me = api_client.get("/api/v1/auth/me", headers=headers)
    assert after_delete_me.status_code == 200, after_delete_me.text
    user = after_delete_me.json()["data"]["user"]
    assert user["status"] == "正常"
    assert user["deleted_at"] is None


def test_frontend_user_can_login_and_remains_blocked_from_admin_apis(api_client: TestClient) -> None:
    response = api_client.post(
        "/api/v1/admin/users",
        headers=_admin_headers(api_client),
        json={"username": "frontuser", "nickname": "前台用户", "role": "前台用户"},
    )
    assert response.status_code == 201, response.text
    data = response.json()["data"]

    login = api_client.post(
        "/api/v1/auth/login",
        json={"username": "frontuser", "password": data["temporary_password"], "remember_me": False},
    )
    assert login.status_code == 200, login.text
    token = login.json()["data"]["access_token"]
    assert login.json()["data"]["user"]["role"] == "前台用户"
    assert login.json()["data"]["user"]["status"] == "正常"

    context = api_client.get("/api/v1/requirement-center/context", headers={"authorization": f"Bearer {token}"})
    assert context.status_code == 200, context.text
    assert context.json()["data"]["current_user"]["can_access_admin"] is False

    me = api_client.get("/api/v1/auth/me", headers={"authorization": f"Bearer {token}"})
    assert me.status_code == 200, me.text
    assert me.json()["data"]["user"]["username"] == "frontuser"

    profile = api_client.patch(
        "/api/v1/auth/me",
        headers={"authorization": f"Bearer {token}"},
        json={"nickname": "  前台昵称  ", "avatar_url": "/api/v1/auth/avatar/front.png"},
    )
    assert profile.status_code == 200, profile.text
    assert profile.json()["data"]["user"]["nickname"] == "前台昵称"
    assert profile.json()["data"]["user"]["avatar_url"] == "/api/v1/auth/avatar/front.png"

    forbidden = api_client.get("/api/v1/admin/users", headers={"authorization": f"Bearer {token}"})
    assert forbidden.status_code == 403

    changed = api_client.post(
        "/api/v1/auth/change-password",
        headers={"authorization": f"Bearer {token}"},
        json={
            "current_password": data["temporary_password"],
            "new_password": "Mb-FrontSecure2026!",
            "confirm_password": "Mb-FrontSecure2026!",
        },
    )
    assert changed.status_code == 200, changed.text
    assert changed.json()["data"] == {"status": "done", "message": "密码已更新，请重新登录。"}

    reused_frontend_session = api_client.get("/api/v1/requirement-center/context", headers={"authorization": f"Bearer {token}"})
    assert reused_frontend_session.status_code == 401

    new_login = api_client.post(
        "/api/v1/auth/login",
        json={"username": "frontuser", "password": "Mb-FrontSecure2026!", "remember_me": False},
    )
    assert new_login.status_code == 200, new_login.text
    new_token = new_login.json()["data"]["access_token"]

    still_forbidden = api_client.get("/api/v1/admin/users", headers={"authorization": f"Bearer {new_token}"})
    assert still_forbidden.status_code == 403


def test_admin_avatar_upload_and_read(api_client: TestClient) -> None:
    from app.core.object_storage import StoredObject, get_object_storage
    from app.main import app

    class FakeAvatarStorage:
        def __init__(self) -> None:
            self.objects: dict[str, tuple[bytes, str]] = {}

        def put(self, key: str, content: bytes, content_type: str) -> None:
            self.objects[key] = (content, content_type)

        def get(self, key: str) -> StoredObject:
            content, content_type = self.objects[key]
            return StoredObject(key=key, content_type=content_type, data=content)

    fake_storage = FakeAvatarStorage()
    app.dependency_overrides[get_object_storage] = lambda: fake_storage
    headers = _admin_headers(api_client)
    try:
        upload = api_client.post(
            "/api/v1/auth/avatar",
            headers=headers,
            files={"file": ("avatar.png", b"avatar-bytes", "image/png")},
        )
        assert upload.status_code == 200
        url = upload.json()["data"]["url"]
        assert upload.json()["data"]["status"] == "done"
        assert list(fake_storage.objects) == [f"images/avatars/{url.rsplit('/', maxsplit=1)[-1]}"]

        media = api_client.get(url, headers=headers)
        assert media.status_code == 200
        assert media.content == b"avatar-bytes"
        assert media.headers["content-type"] == "image/png"

        anonymous = api_client.get(url)
        assert anonymous.status_code == 401
    finally:
        app.dependency_overrides.pop(get_object_storage, None)


def test_old_admin_auth_and_avatar_paths_are_not_registered(api_client: TestClient) -> None:
    headers = _admin_headers(api_client)
    old_auth_prefix = "/api/v1/admin" + "/auth"
    old_avatar_prefix = "/api/v1/admin/users" + "/avatar"

    assert api_client.post(f"{old_auth_prefix}/login", json={"username": "superadmin", "password": ADMIN_PASSWORD}).status_code == 404
    assert api_client.post(f"{old_auth_prefix}/logout", headers=headers).status_code == 404
    assert api_client.get(f"{old_auth_prefix}/me", headers=headers).status_code == 404
    assert api_client.patch(f"{old_auth_prefix}/me", headers=headers, json={"nickname": "旧路径"}).status_code == 404
    assert api_client.post(
        f"{old_auth_prefix}/change-password",
        headers=headers,
        json={"current_password": ADMIN_PASSWORD, "new_password": "Mb-NewSecure2026!", "confirm_password": "Mb-NewSecure2026!"},
    ).status_code == 404
    assert api_client.post(
        old_avatar_prefix,
        headers=headers,
        files={"file": ("avatar.png", b"avatar-bytes", "image/png")},
    ).status_code in {404, 405}
    assert api_client.get(f"{old_avatar_prefix}/avatar.png", headers=headers).status_code in {404, 405}


def test_admin_auth_rejects_login_failure_expired_token_and_non_admin_session(api_client: TestClient) -> None:
    failed_login = api_client.post(
        "/api/v1/auth/login",
        json={"username": "superadmin", "password": "wrong-password", "remember_me": False},
    )
    assert failed_login.status_code == 401

    headers = _admin_headers(api_client)
    from app.db.session import get_session_factory

    expired_at = (datetime.now(UTC) - timedelta(minutes=1)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    db = get_session_factory()()
    try:
        db.execute(text("UPDATE admin_sessions SET expires_at = :expires_at"), {"expires_at": expired_at})
        db.commit()
    finally:
        db.close()
    expired = api_client.get("/api/v1/admin/users", headers=headers)
    assert expired.status_code == 401

    headers = _admin_headers(api_client)
    db = get_session_factory()()
    try:
        db.execute(text("UPDATE admin_users SET role = '前台用户' WHERE username = 'superadmin'"))
        db.commit()
    finally:
        db.close()
    forbidden = api_client.get("/api/v1/admin/users", headers=headers)
    assert forbidden.status_code == 403


def test_admin_auth_logout_and_header_placeholder_rejected(api_client: TestClient) -> None:
    headers = _admin_headers(api_client)
    assert api_client.get("/api/v1/admin/users", headers=headers).status_code == 200

    placeholder = api_client.get("/api/v1/admin/users", headers={"x-admin-role": "admin"})
    assert placeholder.status_code == 401

    logout = api_client.post("/api/v1/auth/logout", headers=headers)
    assert logout.status_code == 200

    reused = api_client.get("/api/v1/admin/users", headers=headers)
    assert reused.status_code == 401


def test_admin_auth_change_own_password_revokes_existing_sessions(api_client: TestClient) -> None:
    headers = _admin_headers(api_client)
    second_headers = _admin_headers(api_client)

    weak = api_client.post(
        "/api/v1/auth/change-password",
        headers=headers,
        json={
            "current_password": ADMIN_PASSWORD,
            "new_password": "password",
            "confirm_password": "password",
        },
    )
    assert weak.status_code == 400

    same = api_client.post(
        "/api/v1/auth/change-password",
        headers=headers,
        json={
            "current_password": ADMIN_PASSWORD,
            "new_password": ADMIN_PASSWORD,
            "confirm_password": ADMIN_PASSWORD,
        },
    )
    assert same.status_code == 400

    wrong_current = api_client.post(
        "/api/v1/auth/change-password",
        headers=headers,
        json={
            "current_password": "wrong-current-password",
            "new_password": "Mb-NewSecure2026!",
            "confirm_password": "Mb-NewSecure2026!",
        },
    )
    assert wrong_current.status_code == 401

    mismatch = api_client.post(
        "/api/v1/auth/change-password",
        headers=headers,
        json={
            "current_password": ADMIN_PASSWORD,
            "new_password": "Mb-NewSecure2026!",
            "confirm_password": "Mb-OtherSecure2026!",
        },
    )
    assert mismatch.status_code == 400

    changed = api_client.post(
        "/api/v1/auth/change-password",
        headers=headers,
        json={
            "current_password": ADMIN_PASSWORD,
            "new_password": "Mb-NewSecure2026!",
            "confirm_password": "Mb-NewSecure2026!",
        },
    )
    assert changed.status_code == 200, changed.text
    assert changed.json()["data"] == {"status": "done", "message": "密码已更新，请重新登录。"}

    reused_current = api_client.get("/api/v1/admin/users", headers=headers)
    assert reused_current.status_code == 401
    reused_second = api_client.get("/api/v1/admin/users", headers=second_headers)
    assert reused_second.status_code == 401

    old_login = api_client.post(
        "/api/v1/auth/login",
        json={"username": "superadmin", "password": ADMIN_PASSWORD, "remember_me": False},
    )
    assert old_login.status_code == 401
    new_login = api_client.post(
        "/api/v1/auth/login",
        json={"username": "superadmin", "password": "Mb-NewSecure2026!", "remember_me": False},
    )
    assert new_login.status_code == 200, new_login.text


def test_admin_auth_update_own_profile(api_client: TestClient) -> None:
    headers = _admin_headers(api_client)

    updated = api_client.patch(
        "/api/v1/auth/me",
        headers=headers,
        json={"nickname": "  月盒管理员  ", "avatar_url": "/api/v1/auth/avatar/avatar.png"},
    )
    assert updated.status_code == 200, updated.text
    user = updated.json()["data"]["user"]
    assert user["username"] == "superadmin"
    assert user["nickname"] == "月盒管理员"
    assert user["avatar_url"] == "/api/v1/auth/avatar/avatar.png"

    me = api_client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["data"]["user"]["nickname"] == "月盒管理员"

    cleared = api_client.patch("/api/v1/auth/me", headers=headers, json={"nickname": "", "avatar_url": None})
    assert cleared.status_code == 200
    assert cleared.json()["data"]["user"]["nickname"] is None
    assert cleared.json()["data"]["user"]["avatar_url"] is None


def test_admin_auth_update_own_profile_rejects_invalid_payloads(api_client: TestClient) -> None:
    headers = _admin_headers(api_client)

    anonymous = api_client.patch("/api/v1/auth/me", json={"nickname": "访客"})
    assert anonymous.status_code == 401

    blob_avatar = api_client.patch("/api/v1/auth/me", headers=headers, json={"avatar_url": "blob:avatar-preview"})
    assert blob_avatar.status_code == 400

    too_long = api_client.patch("/api/v1/auth/me", headers=headers, json={"nickname": "名" * 129})
    assert too_long.status_code == 422

    extra_fields = api_client.patch(
        "/api/v1/auth/me",
        headers=headers,
        json={"nickname": "只改昵称", "role": "前台用户", "status": "已冻结", "username": "changed"},
    )
    assert extra_fields.status_code == 200
    assert extra_fields.json()["data"]["user"]["nickname"] == "只改昵称"
    assert extra_fields.json()["data"]["user"]["role"] == "后台管理员"
    assert extra_fields.json()["data"]["user"]["status"] == "正常"
    assert extra_fields.json()["data"]["user"]["username"] == "superadmin"


def test_admin_auth_cors_preflight_allows_web_origin(api_client: TestClient) -> None:
    response = api_client.options(
        "/api/v1/auth/login",
        headers={
            "origin": "http://localhost:18102",
            "access-control-request-method": "POST",
            "access-control-request-headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:18102"
    assert "POST" in response.headers["access-control-allow-methods"]
    assert "content-type" in response.headers["access-control-allow-headers"].lower()


def test_production_rejects_weak_admin_initial_password() -> None:
    from app.core.config import ConfigurationError, Settings

    settings = Settings(app_env="production", admin_initial_password="change-me-on-first-run")

    try:
        settings.validate_admin_initial_password()
    except ConfigurationError as exc:
        assert "生产环境禁止" in str(exc)
    else:
        raise AssertionError("weak production admin password should be rejected")
