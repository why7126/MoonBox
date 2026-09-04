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


def test_requirement_center_context_disables_pre_sprint_actions_when_required_documents_are_empty(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services import requirement_center

    req_capture_dir = tmp_path / "issues" / "requirements" / "review" / "REQ-9200-empty-capture"
    bug_capture_dir = tmp_path / "issues" / "bugs" / "review" / "BUG-9200-empty-capture"
    req_planning_dir = tmp_path / "issues" / "requirements" / "review" / "REQ-9201-empty-requirement"
    bug_planning_dir = tmp_path / "issues" / "bugs" / "review" / "BUG-9201-empty-bug"
    req_review_dir = tmp_path / "issues" / "requirements" / "review" / "REQ-9202-empty-business-flow"
    bug_review_dir = tmp_path / "issues" / "bugs" / "review" / "BUG-9202-empty-root-cause"
    req_approved_dir = tmp_path / "issues" / "requirements" / "review" / "REQ-9203-empty-review"
    bug_approved_dir = tmp_path / "issues" / "bugs" / "review" / "BUG-9203-empty-review"
    for directory in (
        req_capture_dir,
        bug_capture_dir,
        req_planning_dir,
        bug_planning_dir,
        req_review_dir,
        bug_review_dir,
        req_approved_dir,
        bug_approved_dir,
    ):
        directory.mkdir(parents=True)
    (tmp_path / "openspec").mkdir()
    (tmp_path / "issues" / "requirements" / "_registry.yaml").write_text(
        """
entries:
  - id: REQ-9200-empty-capture
    title: 空采集需求
    status: captured
    path: issues/requirements/review/REQ-9200-empty-capture
  - id: REQ-9201-empty-requirement
    title: 空需求文档
    status: draft
    path: issues/requirements/review/REQ-9201-empty-requirement
  - id: REQ-9202-empty-business-flow
    title: 空业务流程
    status: pending_review
    path: issues/requirements/review/REQ-9202-empty-business-flow
  - id: REQ-9203-empty-review
    title: 空评审记录
    status: approved
    path: issues/requirements/review/REQ-9203-empty-review
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / "issues" / "bugs" / "_registry.yaml").write_text(
        """
entries:
  - id: BUG-9200-empty-capture
    title: 空采集缺陷
    status: captured
    path: issues/bugs/review/BUG-9200-empty-capture
  - id: BUG-9201-empty-bug
    title: 空缺陷文档
    status: draft
    path: issues/bugs/review/BUG-9201-empty-bug
  - id: BUG-9202-empty-root-cause
    title: 空根因文档
    status: pending_review
    path: issues/bugs/review/BUG-9202-empty-root-cause
  - id: BUG-9203-empty-review
    title: 空缺陷评审
    status: approved
    path: issues/bugs/review/BUG-9203-empty-review
""".strip(),
        encoding="utf-8",
    )
    (req_capture_dir / "trace.md").write_text("---\nstatus: captured\n---\n", encoding="utf-8")
    (req_capture_dir / "capture.md").write_text("   \n", encoding="utf-8")
    (bug_capture_dir / "trace.md").write_text("---\nstatus: captured\n---\n", encoding="utf-8")
    (bug_capture_dir / "capture.md").write_text("", encoding="utf-8")
    (req_planning_dir / "trace.md").write_text("---\nstatus: draft\n---\n", encoding="utf-8")
    (req_planning_dir / "capture.md").write_text("# capture\n", encoding="utf-8")
    (req_planning_dir / "requirement.md").write_text("\n", encoding="utf-8")
    (bug_planning_dir / "trace.md").write_text("---\nstatus: draft\n---\n", encoding="utf-8")
    (bug_planning_dir / "capture.md").write_text("# capture\n", encoding="utf-8")
    (bug_planning_dir / "bug.md").write_text("   ", encoding="utf-8")
    for directory in (req_review_dir, req_approved_dir):
        (directory / "trace.md").write_text("---\nstatus: pending_review\n---\n", encoding="utf-8")
        (directory / "capture.md").write_text("# capture\n", encoding="utf-8")
        (directory / "requirement.md").write_text("# requirement\n", encoding="utf-8")
        (directory / "acceptance.md").write_text("# acceptance\n", encoding="utf-8")
        (directory / "business-flow.md").write_text("# business flow\n", encoding="utf-8")
        (directory / "user-stories.md").write_text("# user stories\n", encoding="utf-8")
    (req_review_dir / "business-flow.md").write_text("\n", encoding="utf-8")
    (req_approved_dir / "trace.md").write_text("---\nstatus: approved\n---\n", encoding="utf-8")
    (req_approved_dir / "review.md").write_text(" ", encoding="utf-8")
    for directory in (bug_review_dir, bug_approved_dir):
        (directory / "trace.md").write_text("---\nstatus: pending_review\n---\n", encoding="utf-8")
        (directory / "capture.md").write_text("# capture\n", encoding="utf-8")
        (directory / "bug.md").write_text("# bug\n", encoding="utf-8")
        (directory / "root-cause.md").write_text("# root cause\n", encoding="utf-8")
        (directory / "workaround.md").write_text("# workaround\n", encoding="utf-8")
        (directory / "acceptance.md").write_text("# acceptance\n", encoding="utf-8")
    (bug_review_dir / "root-cause.md").write_text("", encoding="utf-8")
    (bug_approved_dir / "trace.md").write_text("---\nstatus: approved\n---\n", encoding="utf-8")
    (bug_approved_dir / "review.md").write_text("\n", encoding="utf-8")
    monkeypatch.setattr(requirement_center, "GOVERNANCE_ROOT", tmp_path)

    issues = {issue.id: issue for issue in requirement_center.build_requirement_center_context().issues}

    assert issues["REQ-9200"].stage == "capture"
    assert issues["REQ-9200"].action.disabled_reason == "文档内容为空：capture.md"
    assert issues["BUG-9200"].stage == "capture"
    assert issues["BUG-9200"].action.disabled_reason == "文档内容为空：capture.md"
    assert issues["REQ-9201"].stage == "planning"
    assert issues["REQ-9201"].action.disabled_reason == "文档内容为空：requirement.md"
    assert issues["BUG-9201"].stage == "planning"
    assert issues["BUG-9201"].action.disabled_reason == "文档内容为空：bug.md"
    assert issues["REQ-9202"].stage == "review-ready"
    assert issues["REQ-9202"].action.disabled_reason == "文档内容为空：business-flow.md"
    assert issues["BUG-9202"].stage == "review-ready"
    assert issues["BUG-9202"].action.disabled_reason == "文档内容为空：root-cause.md"
    assert issues["REQ-9203"].stage == "approved"
    assert issues["REQ-9203"].action.disabled_reason == "文档内容为空：review.md"
    assert issues["BUG-9203"].stage == "approved"
    assert issues["BUG-9203"].action.disabled_reason == "文档内容为空：review.md"


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


def test_requirement_center_document_capability_matrix_for_issue_stages(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services import requirement_center

    req_review_dir = tmp_path / "issues" / "requirements" / "review" / "REQ-9300-review-ready"
    bug_review_dir = tmp_path / "issues" / "bugs" / "review" / "BUG-9300-review-ready"
    req_approved_dir = tmp_path / "issues" / "requirements" / "review" / "REQ-9301-approved"
    for directory in (req_review_dir, bug_review_dir, req_approved_dir):
        directory.mkdir(parents=True)
    (tmp_path / "openspec").mkdir()
    (tmp_path / "issues" / "requirements" / "_registry.yaml").write_text(
        """
entries:
  - id: REQ-9300-review-ready
    title: 待评审需求
    status: pending_review
    path: issues/requirements/review/REQ-9300-review-ready
  - id: REQ-9301-approved
    title: 已评审需求
    status: approved
    path: issues/requirements/review/REQ-9301-approved
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / "issues" / "bugs" / "_registry.yaml").write_text(
        """
entries:
  - id: BUG-9300-review-ready
    title: 待评审缺陷
    status: pending_review
    path: issues/bugs/review/BUG-9300-review-ready
""".strip(),
        encoding="utf-8",
    )
    for directory in (req_review_dir, req_approved_dir):
        for name in ("trace.md", "capture.md", "requirement.md", "acceptance.md", "business-flow.md", "user-stories.md", "review.md"):
            (directory / name).write_text(f"# {name}\n", encoding="utf-8")
    (req_review_dir / "trace.md").write_text("---\nstatus: pending_review\n---\n# trace\n", encoding="utf-8")
    (req_approved_dir / "trace.md").write_text("---\nstatus: approved\n---\n# trace\n", encoding="utf-8")
    for name in ("trace.md", "capture.md", "bug.md", "root-cause.md", "workaround.md", "acceptance.md"):
        (bug_review_dir / name).write_text(f"# {name}\n", encoding="utf-8")
    (bug_review_dir / "trace.md").write_text("---\nstatus: pending_review\n---\n# trace\n", encoding="utf-8")
    monkeypatch.setattr(requirement_center, "GOVERNANCE_ROOT", tmp_path)

    issues = {issue.id: issue for issue in requirement_center.build_requirement_center_context().issues}
    req_docs = {doc.name: doc for doc in issues["REQ-9300"].document_entries}
    bug_docs = {doc.name: doc for doc in issues["BUG-9300"].document_entries}
    approved_docs = {doc.name: doc for doc in issues["REQ-9301"].document_entries}

    assert req_docs["requirement.md"].capability.human_editable is True
    assert req_docs["business-flow.md"].capability.human_editable is True
    assert req_docs["trace.md"].capability.human_editable is False
    assert req_docs["trace.md"].capability.ai_mutable is True
    assert "bug.md" not in req_docs
    assert bug_docs["bug.md"].capability.human_editable is True
    assert bug_docs["root-cause.md"].capability.human_editable is True
    assert bug_docs["trace.md"].capability.human_editable is False
    assert approved_docs["review.md"].capability.human_editable is True
    effective_spec = requirement_center.compute_document_capability(
        issue_type="requirement",
        stage="done",
        document_name="spec.md",
        path_category="effective_spec",
        exists=True,
    )
    assert effective_spec.human_editable is False
    assert "archive" in effective_spec.reason


def test_requirement_center_change_documents_are_capability_driven_and_save_multiple_specs(
    api_client: TestClient,
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services import requirement_center

    req_dir = tmp_path / "issues" / "requirements" / "review" / "REQ-9302-change-docs"
    change_dir = tmp_path / "openspec" / "changes" / "update-change-docs"
    req_dir.mkdir(parents=True)
    (tmp_path / "issues" / "bugs").mkdir(parents=True)
    (change_dir / "specs" / "alpha").mkdir(parents=True)
    (change_dir / "specs" / "beta").mkdir(parents=True)
    (tmp_path / "issues" / "requirements" / "_registry.yaml").write_text(
        """
entries:
  - id: REQ-9302-change-docs
    title: Change 文档
    status: in_sprint
    path: issues/requirements/review/REQ-9302-change-docs
    related_change: update-change-docs
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / "issues" / "bugs" / "_registry.yaml").write_text("entries: []\n", encoding="utf-8")
    (req_dir / "trace.md").write_text(
        """
---
status: in_sprint
iteration: sprint-999
openspec_changes:
  - change_id: update-change-docs
    status: proposed
---
""".strip(),
        encoding="utf-8",
    )
    (change_dir / "trace.md").write_text("---\nstatus: proposed\nrequirement: REQ-9302-change-docs\n---\n# trace\n", encoding="utf-8")
    (change_dir / "proposal.md").write_text("# proposal\n", encoding="utf-8")
    (change_dir / "design.md").write_text("# design\n", encoding="utf-8")
    (change_dir / "tasks.md").write_text("- [ ] task\n", encoding="utf-8")
    (change_dir / "specs" / "alpha" / "spec.md").write_text("## ADDED Requirements\n\n### Requirement: A\n", encoding="utf-8")
    (change_dir / "specs" / "beta" / "spec.md").write_text("## ADDED Requirements\n\n### Requirement: B\n", encoding="utf-8")
    monkeypatch.setattr(requirement_center, "GOVERNANCE_ROOT", tmp_path)
    headers = _auth_headers(api_client)

    context = api_client.get("/api/v1/requirement-center/context", headers=headers)
    docs = {
        doc["name"]: doc
        for issue in context.json()["data"]["issues"]
        if issue["id"] == "REQ-9302"
        for doc in issue["document_entries"]
    }
    assert docs["proposal.md"]["capability"]["human_editable"] is True
    assert docs["spec.md"]["capability"]["human_editable"] is True
    assert docs["trace.md"]["capability"]["human_editable"] is False

    spec = api_client.get("/api/v1/requirement-center/changes/update-change-docs/documents/spec.md", headers=headers)
    assert spec.status_code == 200
    content = spec.json()["data"]["content"]
    assert "<!-- source: alpha/spec.md -->" in content
    saved = api_client.put(
        "/api/v1/requirement-center/changes/update-change-docs/documents/spec.md",
        headers=headers,
        json={"content": content.replace("Requirement: A", "Requirement: A2")},
    )
    trace_denied = api_client.put(
        "/api/v1/requirement-center/changes/update-change-docs/documents/trace.md",
        headers=headers,
        json={"content": "# hacked"},
    )

    assert saved.status_code == 200, saved.text
    assert "Requirement: A2" in (change_dir / "specs" / "alpha" / "spec.md").read_text(encoding="utf-8")
    assert trace_denied.status_code == 403
    assert "trace.md" in trace_denied.text


def test_requirement_center_acceptance_tasks_are_toggle_only(
    api_client: TestClient,
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services import requirement_center

    req_dir = tmp_path / "issues" / "requirements" / "review" / "REQ-9303-toggle"
    change_dir = tmp_path / "openspec" / "changes" / "update-toggle"
    req_dir.mkdir(parents=True)
    change_dir.mkdir(parents=True)
    (tmp_path / "issues" / "bugs").mkdir(parents=True)
    (tmp_path / "issues" / "requirements" / "_registry.yaml").write_text(
        """
entries:
  - id: REQ-9303-toggle
    title: 验收勾选
    status: in_sprint
    path: issues/requirements/review/REQ-9303-toggle
    related_change: update-toggle
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / "issues" / "bugs" / "_registry.yaml").write_text("entries: []\n", encoding="utf-8")
    (req_dir / "trace.md").write_text("---\nstatus: in_sprint\niteration: sprint-999\n---\n", encoding="utf-8")
    (change_dir / "trace.md").write_text("---\nstatus: applied\nrequirement: REQ-9303-toggle\n---\n# trace\n", encoding="utf-8")
    (change_dir / "tasks.md").write_text("# Tasks\n\n- [ ] 第一项\n- [x] 第二项\n", encoding="utf-8")
    monkeypatch.setattr(requirement_center, "GOVERNANCE_ROOT", tmp_path)
    headers = _auth_headers(api_client)

    context = api_client.get("/api/v1/requirement-center/context", headers=headers)
    docs = {
        doc["name"]: doc
        for issue in context.json()["data"]["issues"]
        if issue["id"] == "REQ-9303"
        for doc in issue["document_entries"]
    }
    assert docs["tasks.md"]["capability"]["task_toggle_only"] is True
    assert docs["tasks.md"]["capability"]["human_editable"] is False

    toggled = "# Tasks\n\n- [x] 第一项\n- [x] 第二项\n"
    saved = api_client.put(
        "/api/v1/requirement-center/changes/update-toggle/documents/tasks.md/tasks",
        headers=headers,
        json={"content": toggled},
    )
    text_denied = api_client.put(
        "/api/v1/requirement-center/changes/update-toggle/documents/tasks.md/tasks",
        headers=headers,
        json={"content": "# Tasks\n\n- [x] 第一项已改\n- [x] 第二项\n"},
    )
    full_denied = api_client.put(
        "/api/v1/requirement-center/changes/update-toggle/documents/tasks.md",
        headers=headers,
        json={"content": toggled},
    )

    assert saved.status_code == 200, saved.text
    assert (change_dir / "tasks.md").read_text(encoding="utf-8") == toggled
    assert text_denied.status_code == 403
    assert full_denied.status_code == 403


def test_requirement_center_capture_save_reports_sanitized_readonly_filesystem(
    api_client: TestClient,
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from pathlib import Path

    from app.services import requirement_center

    capture_dir = tmp_path / "issues" / "requirements" / "plan" / "REQ-9102-readonly-save"
    capture_dir.mkdir(parents=True)
    (tmp_path / "issues" / "requirements" / "_registry.yaml").write_text(
        """
entries:
  - id: REQ-9102-readonly-save
    status: captured
    path: issues/requirements/plan/REQ-9102-readonly-save/
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / "issues" / "bugs" / "_registry.yaml").parent.mkdir(parents=True)
    (tmp_path / "issues" / "bugs" / "_registry.yaml").write_text("entries: []\n", encoding="utf-8")
    (capture_dir / "trace.md").write_text("---\nstatus: captured\n---\n", encoding="utf-8")
    (capture_dir / "capture.md").write_text("# old capture", encoding="utf-8")
    monkeypatch.setattr(requirement_center, "GOVERNANCE_ROOT", tmp_path)

    original_write_text = Path.write_text

    def readonly_write_text(self: Path, *args, **kwargs):
        if self.name == "capture.md":
            raise OSError(30, "Read-only file system")
        return original_write_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", readonly_write_text)

    response = api_client.put(
        "/api/v1/requirement-center/issues/REQ-9102-readonly-save/documents/capture.md",
        headers=_auth_headers(api_client),
        json={"content": "# new capture"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "文档保存失败，治理目录暂不可写"
    assert str(tmp_path) not in response.text


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
