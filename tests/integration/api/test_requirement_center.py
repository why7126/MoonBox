from fastapi.testclient import TestClient
import pytest
from sqlalchemy import text

from app.db.session import get_session_factory


def _auth_headers(api_client: TestClient) -> dict[str, str]:
    response = api_client.post(
        "/api/v1/auth/login",
        json={"username": "superadmin", "password": "example-test-password", "remember_me": False},
    )
    assert response.status_code == 200
    token = response.json()["data"]["access_token"]
    return {"authorization": f"Bearer {token}"}


def _create_frontend_user(api_client: TestClient, username: str) -> tuple[dict, str]:
    response = api_client.post(
        "/api/v1/admin/users",
        headers=_auth_headers(api_client),
        json={"username": username, "nickname": username, "role": "前台用户"},
    )
    assert response.status_code == 201, response.text
    data = response.json()["data"]
    return data["user"], data["temporary_password"]


def _login(api_client: TestClient, username: str, password: str) -> dict[str, str]:
    response = api_client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password, "remember_me": False},
    )
    assert response.status_code == 200, response.text
    return {"authorization": f"Bearer {response.json()['data']['access_token']}"}


def _seed_space_facts(owner_id: str, member_id: str, outsider_id: str) -> None:
    db = get_session_factory()()
    now = "2026-08-15T00:00:00Z"
    try:
        spaces = [
            ("space_owned", "负责人空间", "owner-space", "ACTIVE", owner_id, 2),
            ("space_joined", "已加入空间", "joined-space", "ACTIVE", outsider_id, 2),
            ("space_frozen", "冻结空间", "frozen-space", "FROZEN", outsider_id, 2),
            ("space_recycle", "回收空间", "recycle-space", "RECYCLE", member_id, 1),
            ("space_hidden", "未加入空间", "hidden-space", "ACTIVE", outsider_id, 1),
        ]
        for space_id, name, code, status_value, space_owner_id, member_count in spaces:
            db.execute(
                text(
                    """
                    INSERT INTO admin_spaces (
                        id, name, code, description, owner_id, status, source, member_count,
                        member_quota, storage_used_gb, storage_quota_gb, ai_used_tokens, ai_quota_tokens,
                        expiry_type, expires_at, protected, deleted_at, deleted_by, delete_reason, purge_at,
                        created_at, updated_at
                    ) VALUES (
                        :id, :name, :code, :description, :owner_id, :status, '后台创建', :member_count,
                        20, 0, 100, 0, 1000000,
                        'long_term', NULL, 0, NULL, NULL, NULL, NULL,
                        :created_at, :updated_at
                    )
                    """
                ),
                {
                    "id": space_id,
                    "name": name,
                    "code": code,
                    "description": f"{name} 描述",
                    "owner_id": space_owner_id,
                    "status": status_value,
                    "member_count": member_count,
                    "created_at": now,
                    "updated_at": now,
                },
            )
            db.execute(
                text(
                    """
                    INSERT INTO admin_space_products (
                        id, space_id, product_id, product_name, immutable_binding, created_at, updated_at
                    ) VALUES (
                        :id, :space_id, :product_id, :product_name, 1, :created_at, :updated_at
                    )
                    """
                ),
                {
                    "id": f"product_{space_id}",
                    "space_id": space_id,
                    "product_id": code,
                    "product_name": name,
                    "created_at": now,
                    "updated_at": now,
                },
            )
        db.execute(
            text(
                """
                INSERT INTO admin_space_members (id, space_id, user_id, role, created_at, updated_at)
                VALUES
                    ('member_joined', 'space_joined', :member_id, '编辑者', :created_at, :updated_at),
                    ('member_frozen', 'space_frozen', :member_id, '观察者', :created_at, :updated_at)
                """
            ),
            {"member_id": member_id, "created_at": now, "updated_at": now},
        )
        db.commit()
    finally:
        db.close()


def test_requirement_center_context_returns_real_governance_data(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/requirement-center/context", headers=_auth_headers(api_client))

    assert response.status_code == 200
    payload = response.json()["data"]
    issue_ids = {issue["id"] for issue in payload["issues"]}
    assert "REQ-0013" in issue_ids
    assert "BUG-0001" in issue_ids
    assert payload["stats"]["total"] == len(payload["issues"])
    assert payload["stats"]["requirements"] >= 1
    assert payload["stats"]["bugs"] >= 1
    assert payload["workspaces"] == []
    assert payload["current_user"]["can_access_admin"] is True


def test_requirement_center_context_returns_joined_spaces_with_frontend_whitelist(api_client: TestClient) -> None:
    owner, owner_password = _create_frontend_user(api_client, "spaceowner")
    member, member_password = _create_frontend_user(api_client, "spacemember")
    outsider, _ = _create_frontend_user(api_client, "spaceoutsider")
    _seed_space_facts(owner["id"], member["id"], outsider["id"])

    owner_payload = api_client.get("/api/v1/requirement-center/context", headers=_login(api_client, "spaceowner", owner_password)).json()["data"]
    assert [workspace["workspace_id"] for workspace in owner_payload["workspaces"]] == ["space_owned"]
    assert owner_payload["workspaces"][0]["role"] == "拥有者"

    response = api_client.get("/api/v1/requirement-center/context", headers=_login(api_client, "spacemember", member_password))

    assert response.status_code == 200, response.text
    payload = response.json()["data"]
    workspaces = {workspace["workspace_id"]: workspace for workspace in payload["workspaces"]}
    assert set(workspaces) == {"space_joined", "space_frozen"}
    assert workspaces["space_joined"]["readonly"] is False
    assert workspaces["space_frozen"]["status"] == "FROZEN"
    assert workspaces["space_frozen"]["readonly"] is True
    assert "space_recycle" not in workspaces
    assert "space_hidden" not in workspaces
    assert payload["selected_workspace_id"] in workspaces
    serialized = response.text
    assert "member_quota" not in serialized
    assert "storage_quota_gb" not in serialized
    assert "delete_reason" not in serialized
    assert "allowed_actions" not in serialized


def test_requirement_center_context_user_display_prefers_nickname_and_falls_back_to_username() -> None:
    from app.services.requirement_center import build_requirement_center_context

    with_nickname = build_requirement_center_context(
        current_user={
            "username": "admin",
            "nickname": "平台管理员",
            "avatar_url": "/api/v1/auth/avatar/admin.png",
            "role": "后台管理员",
            "is_system_superadmin": True,
        }
    )
    without_nickname = build_requirement_center_context(
        current_user={
            "username": "admin",
            "nickname": None,
            "role": "后台管理员",
            "is_system_superadmin": True,
        }
    )

    assert with_nickname.current_user.name == "平台管理员"
    assert with_nickname.current_user.avatar_url == "/api/v1/auth/avatar/admin.png"
    assert without_nickname.current_user.name == "admin"


def test_requirement_center_context_derives_workspace_from_project_metadata(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services import requirement_center

    (tmp_path / "issues" / "requirements").mkdir(parents=True)
    (tmp_path / "issues" / "bugs").mkdir(parents=True)
    (tmp_path / "openspec").mkdir()
    (tmp_path / "project.yaml").write_text(
        """
project:
  name: Real Space
  code: Real Space
  owner: Real Team
  description: 来自项目事实源的空间
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / "issues" / "requirements" / "_registry.yaml").write_text("entries: []\n", encoding="utf-8")
    (tmp_path / "issues" / "bugs" / "_registry.yaml").write_text("entries: []\n", encoding="utf-8")
    monkeypatch.setattr(requirement_center, "GOVERNANCE_ROOT", tmp_path)

    context = requirement_center.build_requirement_center_context(
        current_user={"username": "owner", "role": "后台管理员", "is_system_superadmin": True}
    )

    assert len(context.workspaces) == 1
    assert context.workspaces[0].workspace_id == "real-space"
    assert context.workspaces[0].name == "Real Space"
    assert context.workspaces[0].organization_name == "Real Team"
    assert context.workspaces[0].description == "来自项目事实源的空间"
    assert context.workspaces[0].role == "拥有者"


def test_requirement_center_hides_sprint_before_sprint_planning(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services import requirement_center

    issue_dir = tmp_path / "issues" / "requirements" / "review" / "REQ-9001-approved"
    issue_dir.mkdir(parents=True)
    (tmp_path / "issues" / "bugs").mkdir(parents=True)
    (tmp_path / "openspec").mkdir()
    (tmp_path / "iterations" / "change" / "sprint-099").mkdir(parents=True)
    (tmp_path / "iterations" / "change" / "sprint-099" / "sprint.yaml").write_text(
        "requirements:\n  - REQ-9001-approved\n",
        encoding="utf-8",
    )
    (issue_dir / "review.md").write_text("# Review\n", encoding="utf-8")
    (issue_dir / "trace.md").write_text(
        "---\nstatus: approved\niteration: sprint-099\nupdated_at: 2026-08-18 10:30:00\n---\n",
        encoding="utf-8",
    )
    (tmp_path / "issues" / "requirements" / "_registry.yaml").write_text(
        """
entries:
  - id: REQ-9001-approved
    title: 已评审但未入迭代
    status: approved
    target_iteration: sprint-099
    path: issues/requirements/review/REQ-9001-approved
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / "issues" / "bugs" / "_registry.yaml").write_text("entries: []\n", encoding="utf-8")
    monkeypatch.setattr(requirement_center, "GOVERNANCE_ROOT", tmp_path)

    context = requirement_center.build_requirement_center_context()

    assert context.issues[0].stage == "approved"
    assert context.issues[0].sprint_id is None


def test_requirement_center_context_maps_stage_and_drift(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/requirement-center/context", headers=_auth_headers(api_client))

    assert response.status_code == 200
    issues = {issue["id"]: issue for issue in response.json()["data"]["issues"]}
    assert issues["REQ-0013"]["stage"] in {"ready-dev", "development", "acceptance"}
    if issues["REQ-0013"]["task_progress"] is not None:
        assert issues["REQ-0013"]["task_progress"][1] > 0
    assert isinstance(issues["REQ-0013"]["drift_warnings"], list)
    assert response.json()["data"]["stats"]["drift"] >= 0


def test_requirement_center_context_sanitizes_paths(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/requirement-center/context", headers=_auth_headers(api_client))

    assert response.status_code == 200
    serialized = response.text
    assert "/Users/" not in serialized
    assert "CodeSpaces/Projects" not in serialized


def test_requirement_center_document_endpoints_are_sanitized(
    api_client: TestClient,
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services import requirement_center

    issue_dir = tmp_path / "issues" / "requirements" / "review" / "REQ-9000-documents"
    issue_dir.mkdir(parents=True)
    (tmp_path / "issues" / "bugs").mkdir(parents=True)
    (tmp_path / "openspec").mkdir()
    (tmp_path / "issues" / "requirements" / "_registry.yaml").write_text(
        """
entries:
  - id: REQ-9000-documents
    title: 文档读取
    status: approved
    path: issues/requirements/review/REQ-9000-documents
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / "issues" / "bugs" / "_registry.yaml").write_text("entries: []\n", encoding="utf-8")
    (issue_dir / "requirement.md").write_text("# PRD\n正文", encoding="utf-8")
    (issue_dir / "prototype.html").write_text("<main>Preview</main>", encoding="utf-8")
    (issue_dir / "secret.txt").write_text("secret", encoding="utf-8")
    monkeypatch.setattr(requirement_center, "GOVERNANCE_ROOT", tmp_path)
    headers = _auth_headers(api_client)

    markdown = api_client.get(
        "/api/v1/requirement-center/issues/REQ-9000-documents/documents/requirement.md",
        headers=headers,
    )
    html = api_client.get(
        "/api/v1/requirement-center/issues/REQ-9000-documents/documents/prototype.html/preview",
        headers=headers,
    )
    illegal = api_client.get(
        "/api/v1/requirement-center/issues/REQ-9000-documents/documents/secret.txt",
        headers=headers,
    )

    assert markdown.status_code == 200
    assert markdown.json()["data"]["content"] == "# PRD\n正文"
    assert html.status_code == 200
    assert "Preview" in html.text
    assert illegal.status_code == 400
    assert str(tmp_path) not in illegal.text


def test_requirement_center_capture_document_update_is_stage_and_file_limited(
    api_client: TestClient,
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services import requirement_center

    capture_dir = tmp_path / "issues" / "requirements" / "review" / "REQ-9100-capture-edit"
    approved_dir = tmp_path / "issues" / "requirements" / "review" / "REQ-9101-approved-edit"
    capture_dir.mkdir(parents=True)
    approved_dir.mkdir(parents=True)
    (tmp_path / "issues" / "bugs").mkdir(parents=True)
    (tmp_path / "openspec").mkdir()
    (tmp_path / "issues" / "requirements" / "_registry.yaml").write_text(
        """
entries:
  - id: REQ-9100-capture-edit
    title: 采集池编辑
    status: captured
    path: issues/requirements/review/REQ-9100-capture-edit
  - id: REQ-9101-approved-edit
    title: 已评审只读
    status: approved
    path: issues/requirements/review/REQ-9101-approved-edit
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / "issues" / "bugs" / "_registry.yaml").write_text("entries: []\n", encoding="utf-8")
    (capture_dir / "trace.md").write_text("---\nstatus: captured\n---\n", encoding="utf-8")
    (capture_dir / "capture.md").write_text("# old capture", encoding="utf-8")
    (capture_dir / "trace.md").write_text("---\nstatus: captured\n---\n", encoding="utf-8")
    (approved_dir / "trace.md").write_text("---\nstatus: approved\n---\n", encoding="utf-8")
    (approved_dir / "capture.md").write_text("# approved capture", encoding="utf-8")
    monkeypatch.setattr(requirement_center, "GOVERNANCE_ROOT", tmp_path)
    headers = _auth_headers(api_client)

    editable_context = api_client.get("/api/v1/requirement-center/context", headers=headers)
    docs = {
        doc["name"]: doc
        for issue in editable_context.json()["data"]["issues"]
        if issue["id"] == "REQ-9100"
        for doc in issue["document_entries"]
    }
    assert docs["capture.md"]["editable"] is True
    assert docs["trace.md"]["editable"] is False

    saved = api_client.put(
        "/api/v1/requirement-center/issues/REQ-9100-capture-edit/documents/capture.md",
        headers=headers,
        json={"content": "# new capture"},
    )
    trace_denied = api_client.put(
        "/api/v1/requirement-center/issues/REQ-9100-capture-edit/documents/trace.md",
        headers=headers,
        json={"content": "# trace"},
    )
    stage_denied = api_client.put(
        "/api/v1/requirement-center/issues/REQ-9101-approved-edit/documents/capture.md",
        headers=headers,
        json={"content": "# approved"},
    )

    assert saved.status_code == 200, saved.text
    assert saved.json()["data"]["content"] == "# new capture"
    assert (capture_dir / "capture.md").read_text(encoding="utf-8") == "# new capture"
    assert trace_denied.status_code == 403
    assert stage_denied.status_code == 403
    assert str(tmp_path) not in trace_denied.text


def test_requirement_center_context_requires_login(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/requirement-center/context")

    assert response.status_code == 401


def test_requirement_center_context_reports_sanitized_missing_governance_root(
    api_client: TestClient,
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services import requirement_center

    monkeypatch.setattr(requirement_center, "GOVERNANCE_ROOT", tmp_path)

    response = api_client.get("/api/v1/requirement-center/context", headers=_auth_headers(api_client))

    assert response.status_code == 503
    assert response.json()["detail"] == "需求中心数据源暂不可用"
    assert str(tmp_path) not in response.text
