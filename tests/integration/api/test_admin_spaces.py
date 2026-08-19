from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.config import settings
from app.db.seed import seed_demo_space_applications
from app.db.session import get_session_factory

ADMIN_PASSWORD = "example-test-password"


def _admin_headers(api_client: TestClient) -> dict[str, str]:
    response = api_client.post(
        "/api/v1/auth/login",
        json={"username": "superadmin", "password": ADMIN_PASSWORD, "remember_me": False},
    )
    assert response.status_code == 200, response.text
    token = response.json()["data"]["access_token"]
    return {"authorization": f"Bearer {token}"}


def _create_owner(api_client: TestClient, username: str = "spaceowner") -> dict:
    response = api_client.post(
        "/api/v1/admin/users",
        headers=_admin_headers(api_client),
        json={"username": username, "nickname": "空间负责人", "role": "前台用户"},
    )
    assert response.status_code == 201, response.text
    return response.json()["data"]["user"]


def _create_frontend_user(api_client: TestClient, username: str) -> tuple[dict, str]:
    response = api_client.post(
        "/api/v1/admin/users",
        headers=_admin_headers(api_client),
        json={"username": username, "nickname": username, "role": "前台用户"},
    )
    assert response.status_code == 201, response.text
    payload = response.json()["data"]
    _activate_user(payload["user"]["id"])
    return payload["user"], payload["temporary_password"]


def _user_headers(api_client: TestClient, username: str, password: str) -> dict[str, str]:
    response = api_client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password, "remember_me": False},
    )
    assert response.status_code == 200, response.text
    return {"authorization": f"Bearer {response.json()['data']['access_token']}"}


def _activate_user(user_id: str) -> None:
    db = get_session_factory()()
    try:
        db.execute(text("UPDATE admin_users SET status = '正常' WHERE id = :id"), {"id": user_id})
        db.commit()
    finally:
        db.close()


def _set_avatar_url(user_id: str, avatar_url: str) -> None:
    db = get_session_factory()()
    try:
        db.execute(text("UPDATE admin_users SET avatar_url = :avatar_url WHERE id = :id"), {"id": user_id, "avatar_url": avatar_url})
        db.commit()
    finally:
        db.close()


def _create_space(api_client: TestClient, owner_id: str, code: str = "demo-space") -> dict:
    response = api_client.post(
        "/api/v1/admin/spaces",
        headers=_admin_headers(api_client),
        json={
            "name": "Demo 空间",
            "code": code,
            "description": "用于集成测试",
            "owner_id": owner_id,
            "product_id": "moonbox-platform",
            "product_name": "MoonBox Platform",
            "member_quota": 20,
            "storage_quota_gb": 100,
            "ai_quota_tokens": 1000000,
            "expiry_type": "fixed_date",
            "expires_at": "2027-12-31T23:59:59Z",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["data"]


def test_admin_space_create_list_detail_and_update(api_client: TestClient) -> None:
    owner = _create_owner(api_client)
    created = _create_space(api_client, owner["id"])
    headers = _admin_headers(api_client)

    assert created["status"] == "ACTIVE"
    assert created["source"] == "后台创建"
    assert created["allowed_actions"]

    listing = api_client.get(
        "/api/v1/admin/spaces",
        headers=headers,
        params={"q": "demo", "status": "ACTIVE", "source": "后台创建"},
    )
    assert listing.status_code == 200, listing.text
    assert listing.json()["data"]["total"] == 1

    detail = api_client.get(f"/api/v1/admin/spaces/{created['id']}", headers=headers)
    assert detail.status_code == 200, detail.text
    assert detail.json()["data"]["product_name"] == "MoonBox Platform"

    updated = api_client.put(
        f"/api/v1/admin/spaces/{created['id']}",
        headers=headers,
        json={
            "name": "Demo 空间新版",
            "description": "更新后的描述",
            "expiry_type": "long_term",
            "expires_at": None,
        },
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["data"]["name"] == "Demo 空间新版"
    assert updated.json()["data"]["expiry_type"] == "long_term"

    expired = api_client.put(
        f"/api/v1/admin/spaces/{created['id']}",
        headers=headers,
        json={
            "name": "Demo 空间新版",
            "description": "更新后的描述",
            "expiry_type": "fixed_date",
            "expires_at": "2020-01-01T00:00:00Z",
        },
    )
    assert expired.status_code == 422, expired.text


def test_admin_space_status_quota_recycle_and_purge(api_client: TestClient) -> None:
    owner = _create_owner(api_client, "ownerflow")
    space = _create_space(api_client, owner["id"], "flow-space")
    headers = _admin_headers(api_client)

    quota = api_client.post(
        f"/api/v1/admin/spaces/{space['id']}/quota",
        headers=headers,
        json={"member_quota": 30, "storage_quota_gb": 200, "ai_quota_tokens": 2000000, "reason": "业务增长调整"},
    )
    assert quota.status_code == 200, quota.text
    assert quota.json()["data"]["member_quota"] == 30

    freeze = api_client.post(
        f"/api/v1/admin/spaces/{space['id']}/freeze",
        headers=headers,
        json={"reason": "安全巡检冻结"},
    )
    assert freeze.status_code == 200, freeze.text
    assert freeze.json()["data"]["status"] == "FROZEN"
    assert "RESTORE" in freeze.json()["data"]["allowed_actions"]

    restore = api_client.post(
        f"/api/v1/admin/spaces/{space['id']}/restore",
        headers=headers,
        json={"reason": "安全巡检恢复"},
    )
    assert restore.status_code == 200, restore.text
    assert restore.json()["data"]["status"] == "ACTIVE"

    recycle = api_client.request(
        "DELETE",
        f"/api/v1/admin/spaces/{space['id']}",
        headers=headers,
        json={"reason": "空间生命周期结束"},
    )
    assert recycle.status_code == 200, recycle.text
    assert recycle.json()["data"]["status"] == "RECYCLE"
    assert recycle.json()["data"]["purge_at"] is not None

    default_list = api_client.get("/api/v1/admin/spaces", headers=headers)
    assert default_list.status_code == 200
    assert default_list.json()["data"]["total"] == 0

    recycle_list = api_client.get("/api/v1/admin/spaces", headers=headers, params={"status": "RECYCLE"})
    assert recycle_list.status_code == 200
    assert recycle_list.json()["data"]["total"] == 1
    recycled_item = recycle_list.json()["data"]["items"][0]
    assert recycled_item["deleted_by"] is not None
    assert recycled_item["deleted_by_name"] is not None
    assert recycled_item["delete_reason"] == "空间生命周期结束"

    purge = api_client.request(
        "DELETE",
        f"/api/v1/admin/spaces/{space['id']}/purge",
        headers=headers,
        json={"reason": "超过保留期清理"},
    )
    assert purge.status_code == 200, purge.text
    missing = api_client.get(f"/api/v1/admin/spaces/{space['id']}", headers=headers)
    assert missing.status_code == 404


def test_admin_space_members_api_excludes_owner_and_sorts_by_role(api_client: TestClient) -> None:
    owner = _create_owner(api_client, "memberowner")
    admin = _create_owner(api_client, "memberadmin")
    viewer = _create_owner(api_client, "memberviewer")
    editor = _create_owner(api_client, "membereditor")
    for user in (admin, viewer, editor):
        _activate_user(user["id"])
    _set_avatar_url(owner["id"], "/api/v1/admin/users/avatar/owner-legacy.webp")
    _set_avatar_url(admin["id"], "/api/v1/admin/users/avatar/admin-legacy.webp")
    _set_avatar_url(viewer["id"], "/api/v1/admin/users/avatar/viewer-legacy.webp")
    space = _create_space(api_client, owner["id"], "member-space")
    headers = _admin_headers(api_client)

    owner_add = api_client.post(
        f"/api/v1/admin/spaces/{space['id']}/members",
        headers=headers,
        json={"user_id": owner["id"], "role": "管理员"},
    )
    assert owner_add.status_code == 403, owner_add.text

    viewer_add = api_client.post(
        f"/api/v1/admin/spaces/{space['id']}/members",
        headers=headers,
        json={"user_id": viewer["id"], "role": "查看者"},
    )
    assert viewer_add.status_code == 201, viewer_add.text
    assert viewer_add.json()["data"]["avatar_url"] == "/api/v1/auth/avatar/viewer-legacy.webp"
    admin_add = api_client.post(
        f"/api/v1/admin/spaces/{space['id']}/members",
        headers=headers,
        json={"user_id": admin["id"], "role": "管理员"},
    )
    assert admin_add.status_code == 201, admin_add.text
    assert admin_add.json()["data"]["avatar_url"] == "/api/v1/auth/avatar/admin-legacy.webp"
    editor_add = api_client.post(
        f"/api/v1/admin/spaces/{space['id']}/members",
        headers=headers,
        json={"user_id": editor["id"], "role": "编辑者"},
    )
    assert editor_add.status_code == 201, editor_add.text

    listing = api_client.get(f"/api/v1/admin/spaces/{space['id']}/members", headers=headers)
    assert listing.status_code == 200, listing.text
    members = listing.json()["data"]
    assert [item["role"] for item in members] == ["管理员", "编辑者", "查看者"]
    assert owner["id"] not in [item["user_id"] for item in members]
    assert members[0]["avatar_url"] == "/api/v1/auth/avatar/admin-legacy.webp"
    assert members[2]["avatar_url"] == "/api/v1/auth/avatar/viewer-legacy.webp"
    assert all(not (item["avatar_url"] or "").startswith("/api/v1/admin/users/avatar/") for item in members)

    detail = api_client.get(f"/api/v1/admin/spaces/{space['id']}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["data"]["member_count"] == 4
    assert detail.json()["data"]["owner_avatar_url"] == "/api/v1/auth/avatar/owner-legacy.webp"

    updated = api_client.put(
        f"/api/v1/admin/spaces/{space['id']}/members/{viewer_add.json()['data']['id']}",
        headers=headers,
        json={"role": "编辑者"},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["data"]["role"] == "编辑者"
    assert updated.json()["data"]["avatar_url"] == "/api/v1/auth/avatar/viewer-legacy.webp"

    removed = api_client.request(
        "DELETE",
        f"/api/v1/admin/spaces/{space['id']}/members/{admin_add.json()['data']['id']}",
        headers=headers,
        json={"reason": "成员离开项目"},
    )
    assert removed.status_code == 200, removed.text
    assert removed.json()["data"]["user_id"] == admin["id"]
    assert removed.json()["data"]["avatar_url"] == "/api/v1/auth/avatar/admin-legacy.webp"
    after_remove = api_client.get(f"/api/v1/admin/spaces/{space['id']}", headers=headers)
    assert after_remove.json()["data"]["member_count"] == 3

    audit_response = api_client.get(f"/api/v1/admin/spaces/{space['id']}/audit-events", headers=headers)
    assert audit_response.status_code == 200, audit_response.text
    audit_payload = audit_response.json()["data"]
    assert audit_payload["total"] >= 3
    assert audit_payload["page"] == 1
    audit_events = audit_payload["items"]
    actions = [event["action"] for event in audit_events]
    assert "add_member" in actions
    assert "update_member_role" in actions
    assert "remove_member" in actions
    role_event = next(event for event in audit_events if event["action"] == "update_member_role")
    assert role_event["reason"] == "后台编辑空间成员角色"
    assert role_event["actor_display_name"]
    assert role_event["actor_display_name"] != role_event["actor"]
    assert role_event["before_value"] is not None
    assert role_event["after_value"] is not None


def test_admin_space_application_approval_creates_space(api_client: TestClient) -> None:
    owner = _create_owner(api_client, "applyowner")
    headers = _admin_headers(api_client)

    create_application = api_client.post(
        "/api/v1/admin/space-applications",
        headers=headers,
        json={
            "name": "申请空间",
            "code": "apply-space",
            "applicant_id": owner["id"],
            "proposed_owner_id": owner["id"],
            "product_id": "moonbox-platform",
            "product_name": "MoonBox Platform",
            "purpose": "业务团队申请开通空间",
            "expected_members": 12,
            "requested_storage_gb": 88,
            "requested_ai_tokens": 900000,
            "expires_at": None,
        },
    )
    assert create_application.status_code == 201, create_application.text
    application = create_application.json()["data"]

    approve = api_client.post(
        f"/api/v1/admin/space-applications/{application['id']}/approve",
        headers=headers,
        json={"reason": "资料完整准予开通"},
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["data"]["status"] == "已通过"

    listing = api_client.get("/api/v1/admin/spaces", headers=headers, params={"q": "apply-space"})
    assert listing.status_code == 200
    payload = listing.json()["data"]
    assert payload["total"] == 1
    assert payload["items"][0]["source"] == "申请审批"

    created_space = payload["items"][0]
    audit_response = api_client.get(f"/api/v1/admin/spaces/{created_space['id']}/audit-events", headers=headers)
    assert audit_response.status_code == 200, audit_response.text
    audit_payload = audit_response.json()["data"]
    assert audit_payload["total"] >= 2
    audit_events = audit_payload["items"]
    actions = [event["action"] for event in audit_events]
    assert "create_space" in actions
    assert "application_approved_create_space" in actions
    approval_event = next(event for event in audit_events if event["action"] == "application_approved_create_space")
    assert approval_event["reason"] == "资料完整准予开通"
    assert approval_event["result"] == "success"
    assert approval_event["actor_display_name"]


def test_catalog_create_space_submits_pending_application(api_client: TestClient) -> None:
    applicant, password = _create_frontend_user(api_client, "createuser")
    headers = _user_headers(api_client, applicant["username"], password)

    created = api_client.post(
        "/api/v1/catalog/workspace-applications/create",
        headers=headers,
        json={
            "name": "用户创建空间",
            "code": "user-space",
            "description": "前台直接创建空间",
            "member_quota": 20,
            "storage_quota_gb": 100,
            "ai_quota_tokens": 1000000,
            "expiry_type": "fixed_date",
            "expires_at": "2027-12-31T23:59:59Z",
        },
    )
    assert created.status_code == 201, created.text
    payload = created.json()["data"]
    assert payload["application"]["applicant_id"] == applicant["id"]
    assert payload["application"]["proposed_owner_id"] == applicant["id"]
    assert payload["application"]["code"] == "user-space"
    assert payload["application"]["expected_members"] == 20
    assert payload["application"]["requested_storage_gb"] == 100
    assert payload["application"]["requested_ai_tokens"] == 1000000
    assert payload["application"]["status"] == "待审批"

    listing = api_client.get("/api/v1/admin/spaces", headers=_admin_headers(api_client), params={"q": "user-space"})
    assert listing.status_code == 200, listing.text
    assert listing.json()["data"]["total"] == 0

    applications = api_client.get("/api/v1/admin/space-applications", headers=_admin_headers(api_client), params={"q": "user-space"})
    assert applications.status_code == 200, applications.text
    assert applications.json()["data"]["total"] == 1


def test_catalog_create_space_rejects_join_and_out_of_range_quota(api_client: TestClient) -> None:
    applicant, password = _create_frontend_user(api_client, "rangeuser")
    headers = _user_headers(api_client, applicant["username"], password)

    join = api_client.post("/api/v1/catalog/workspace-applications/join", headers=headers, json={"workspace_id": "space_x", "reason": "申请加入"})
    assert join.status_code == 404

    invalid = api_client.post(
        "/api/v1/catalog/workspace-applications/create",
        headers=headers,
        json={
            "name": "超额空间",
            "code": "over-space",
            "description": "成员超额",
            "member_quota": 0,
            "storage_quota_gb": 0,
            "ai_quota_tokens": -1,
            "expiry_type": "long_term",
        },
    )
    assert invalid.status_code == 422


def test_demo_space_application_seed_uses_real_approval_flow(api_client: TestClient) -> None:
    db = get_session_factory()()
    old_app_env = settings.app_env
    old_demo_seed = settings.admin_space_application_demo_seed
    try:
        settings.app_env = "production"
        settings.admin_space_application_demo_seed = True
        assert seed_demo_space_applications(db) == 0
        settings.app_env = old_app_env
        settings.admin_space_application_demo_seed = old_demo_seed
        assert seed_demo_space_applications(db, force=True) == 3
        assert seed_demo_space_applications(db, force=True) == 0
    finally:
        settings.app_env = old_app_env
        settings.admin_space_application_demo_seed = old_demo_seed
        db.close()

    headers = _admin_headers(api_client)
    applications_response = api_client.get("/api/v1/admin/space-applications", headers=headers)
    assert applications_response.status_code == 200, applications_response.text
    applications_payload = applications_response.json()["data"]
    assert applications_payload["total"] == 3
    applications_by_code = {item["code"]: item for item in applications_payload["items"]}
    assert applications_by_code["ai-factory-demo"]["status"] == "待审批"
    assert applications_by_code["ai-factory-demo"]["applicant_name"] == "演示申请人"
    assert applications_by_code["ai-factory-demo"]["proposed_owner_name"] == "演示负责人"

    approve_response = api_client.post(
        f"/api/v1/admin/space-applications/{applications_by_code['ai-factory-demo']['id']}/approve",
        headers=headers,
        json={"reason": "演示审批通过"},
    )
    assert approve_response.status_code == 200, approve_response.text

    pending_response = api_client.get("/api/v1/admin/space-applications", headers=headers)
    assert pending_response.status_code == 200, pending_response.text
    pending_payload = pending_response.json()["data"]
    assert pending_payload["total"] == 2
    assert {item["code"] for item in pending_payload["items"]} == {"growth-lab-demo", "delivery-space-demo"}

    space_response = api_client.get("/api/v1/admin/spaces", headers=headers, params={"q": "ai-factory-demo"})
    assert space_response.status_code == 200, space_response.text
    space_payload = space_response.json()["data"]
    assert space_payload["total"] == 1
    seeded_space = space_payload["items"][0]
    assert seeded_space["source"] == "申请审批"
    assert seeded_space["product_id"] == "ai-factory-demo"

    audit_response = api_client.get(f"/api/v1/admin/spaces/{seeded_space['id']}/audit-events", headers=headers)
    assert audit_response.status_code == 200, audit_response.text
    audit_events = audit_response.json()["data"]["items"]
    actions = [event["action"] for event in audit_events]
    assert "application_approved_create_space" in actions
    approval_event = next(event for event in audit_events if event["action"] == "application_approved_create_space")
    assert approval_event["actor_display_name"] != approval_event["actor"]
    assert approval_event["before_value"] is not None
    assert approval_event["after_value"] is not None
