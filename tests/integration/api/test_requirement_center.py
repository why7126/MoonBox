from fastapi.testclient import TestClient
import pytest


def _auth_headers(api_client: TestClient) -> dict[str, str]:
    response = api_client.post(
        "/api/v1/auth/login",
        json={"username": "superadmin", "password": "example-test-password", "remember_me": False},
    )
    assert response.status_code == 200
    token = response.json()["data"]["access_token"]
    return {"authorization": f"Bearer {token}"}


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
    assert payload["workspaces"][0]["workspace_id"] == "moonbox"
    assert payload["workspaces"][0]["name"] == "MoonBox"
    assert payload["workspaces"][0]["member_count"] >= 1
    assert {workspace["workspace_id"] for workspace in payload["workspaces"]}.isdisjoint({"moonbox-growth", "demo-founder"})
    assert payload["current_user"]["can_access_admin"] is True


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


def test_requirement_center_context_maps_stage_and_drift(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/requirement-center/context", headers=_auth_headers(api_client))

    assert response.status_code == 200
    issues = {issue["id"]: issue for issue in response.json()["data"]["issues"]}
    assert issues["REQ-0013"]["stage"] == "acceptance"
    assert issues["REQ-0013"]["task_progress"][1] > 0
    assert isinstance(issues["REQ-0013"]["drift_warnings"], list)
    assert response.json()["data"]["stats"]["drift"] >= 0


def test_requirement_center_context_sanitizes_paths(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/requirement-center/context", headers=_auth_headers(api_client))

    assert response.status_code == 200
    serialized = response.text
    assert "/Users/" not in serialized
    assert "CodeSpaces/Projects" not in serialized


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
