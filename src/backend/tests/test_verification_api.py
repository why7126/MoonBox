import json
import hashlib
from pathlib import Path
import time
from sqlalchemy import update

from test_chat import chat
from app.api.v1.admin_auth import require_session_user
from app.main import app
from app.chat.schema import verification_tasks, task_traces
from sqlalchemy import select
from sqlalchemy.schema import CreateTable, CreateIndex
from sqlalchemy.dialects import mysql, sqlite
from app.chat.service import now
from app.verification.environment import inspect_environment
from app.verification.artifacts import publish_artifact


def test_verification_task_schema_compiles_for_sqlite_and_mysql():
    for dialect in (sqlite.dialect(), mysql.dialect()):
        ddl = str(CreateTable(verification_tasks).compile(dialect=dialect))
        assert "verification_tasks" in ddl and "uq_verification_request" in ddl
        assert all(str(CreateIndex(index).compile(dialect=dialect)) for index in verification_tasks.indexes)


def test_preflight_checks_space_permission_before_repository_binding(chat, monkeypatch):
    client, _ = chat
    called = []
    monkeypatch.setattr("app.verification.service.repository_binding", lambda *args: called.append(args))
    app.dependency_overrides[require_session_user] = lambda: {"id": "bob"}
    response = client.get("/api/v1/chat/verification-environments/preflight", params={"space_id": "space", "repository_id": "repo"})
    assert response.status_code == 403
    assert called == []


def test_preflight_reports_missing_platform_configuration_without_host_paths(chat, monkeypatch, tmp_path):
    client, _ = chat
    (tmp_path / "package.json").write_text(json.dumps({"packageManager": "pnpm@11.2.2", "devDependencies": {"@playwright/test": "^1.62.1"}}))
    (tmp_path / "pnpm-lock.yaml").write_text("lockfileVersion: '9.0'\nimporters:\n  .:\n    devDependencies:\n      '@playwright/test':\n        version: 1.62.1\n")
    monkeypatch.setattr("app.verification.service.repository_binding", lambda *args: {"source_root": str(tmp_path)})
    response = client.get("/api/v1/chat/verification-environments/preflight", params={"space_id": "space", "repository_id": "repo"})
    assert response.status_code == 200
    assert response.json()["data"]["reason_code"] == "node_version_unpinned"
    assert str(tmp_path) not in response.text


def test_verification_task_idempotency_and_revocation(chat, monkeypatch):
    client, factory = chat
    monkeypatch.setattr("app.verification.tasks.scope.authorize", lambda *args, **kwargs: object())
    monkeypatch.setattr("app.verification.tasks.inspect_authorized", lambda *args: {
        "status": "ready", "reason_code": None, "environment_key": "a" * 64, "checks": {}})
    monkeypatch.setattr("app.verification.tasks.repository_binding", lambda *args: {"source_root": "synthetic"})
    request = {"client_request_id": "same", "space_id": "space", "repository_id": "repo", "browser": "firefox"}
    first = client.post("/api/v1/chat/verification-tasks", json=request)
    assert first.status_code == 200
    task_id = first.json()["data"]["id"]
    assert client.post("/api/v1/chat/verification-tasks", json=request).json()["data"]["id"] == task_id
    with factory() as db:
        saved = db.execute(select(verification_tasks).where(verification_tasks.c.id == task_id)).mappings().one()
        assert saved["client_request_id"] == hashlib.sha256(b"same").hexdigest()
        trace = db.execute(select(task_traces).where(task_traces.c.turn_id == task_id)).mappings().one()
        assert trace["parent_request_id"]
    assert client.post("/api/v1/chat/verification-tasks", json={**request, "browser": "chromium"}).status_code == 409
    assert client.get(f"/api/v1/chat/verification-tasks/{task_id}").status_code == 200
    assert client.post(f"/api/v1/chat/verification-tasks/{task_id}/cancel").json()["data"]["status"] == "cancelled"
    monkeypatch.setattr("app.verification.tasks.repository_binding", lambda *args: None)
    assert client.get(f"/api/v1/chat/verification-tasks/{task_id}").status_code == 403
    app.dependency_overrides[require_session_user] = lambda: {"id": "bob"}
    assert client.get(f"/api/v1/chat/verification-tasks/{task_id}").status_code == 404


def test_evidence_read_rechecks_authorization_and_result_reference(chat, monkeypatch, tmp_path):
    client, factory = chat
    monkeypatch.setattr("app.verification.tasks.scope.authorize", lambda *args, **kwargs: object())
    monkeypatch.setattr("app.verification.tasks.inspect_authorized", lambda *args: {
        "status": "ready", "environment_key": "a" * 64})
    monkeypatch.setattr("app.verification.tasks.repository_binding", lambda *args: {"source_root": "synthetic"})
    monkeypatch.setenv("MOONBOX_VERIFICATION_EVIDENCE_ROOT", str(tmp_path))
    created = client.post("/api/v1/chat/verification-tasks", json={
        "client_request_id": "evidence", "space_id": "space", "repository_id": "repo", "browser": "chromium"}).json()["data"]
    task_id = created["id"]
    folder = tmp_path / hashlib.sha256(b"space\0repo").hexdigest() / task_id
    folder.mkdir(parents=True)
    (folder / "chromium-1440x900.png").write_bytes(b"\x89PNGfixture")
    with factory() as db:
        db.execute(update(verification_tasks).where(verification_tasks.c.id == task_id).values(
            status="passed", result=json.dumps({"viewports": [{"screenshot": "chromium-1440x900.png"}]}), completed_at=now()))
        db.commit()
    assert client.get(f"/api/v1/chat/verification-tasks/{task_id}/evidence/chromium-1440x900.png").content == b"\x89PNGfixture"
    assert client.get(f"/api/v1/chat/verification-tasks/{task_id}/evidence/firefox-1440x900.png").status_code == 404
    app.dependency_overrides[require_session_user] = lambda: {"id": "bob"}
    assert client.get(f"/api/v1/chat/verification-tasks/{task_id}/evidence/chromium-1440x900.png").status_code == 404


def test_preflight_ready_requires_matching_worker_and_verified_artifact(chat, monkeypatch, tmp_path):
    client, _ = chat
    source = tmp_path / "source"
    source.mkdir()
    (source / "package.json").write_text(json.dumps({"packageManager": "pnpm@11.2.2",
        "devDependencies": {"@playwright/test": "^1.62.1"}}))
    (source / "pnpm-lock.yaml").write_text("lockfileVersion: '9.0'\nimporters:\n  .:\n    devDependencies:\n      '@playwright/test':\n        version: 1.62.1\n")
    state, root = tmp_path / "state", tmp_path / "artifacts"
    state.mkdir(); root.mkdir()
    image = "sha256:" + "a" * 64
    for key, value in {"MOONBOX_VERIFICATION_NODE_VERSION": "24.18.1",
        "MOONBOX_VERIFICATION_PNPM_VERSION": "11.2.2", "MOONBOX_VERIFICATION_ARCH": "arm64",
        "MOONBOX_VERIFICATION_IMAGE_ID": image,
        "MOONBOX_VERIFICATION_STATE_ROOT": str(state),
        "MOONBOX_VERIFICATION_ARTIFACT_ROOT": str(root)}.items():
        monkeypatch.setenv(key, value)
    (state / "worker-ready.json").write_text(json.dumps({"time": time.time(), "image_digest": image,
        "node_version": "24.18.1", "pnpm_version": "11.2.2", "architecture": "arm64",
        "browsers": {"firefox": "153", "chromium": "151"}}))
    item = inspect_environment(source, node_version="24.18.1", os_name="linux", architecture="arm64", image_digest=image)
    stage = root / "preparing-test"
    (stage / "node_modules" / "@playwright" / "test").mkdir(parents=True)
    (stage / "node_modules" / "@playwright" / "test" / "package.json").write_text('{"version":"1.62.1"}')
    publish_artifact(stage, root, item)
    monkeypatch.setattr("app.verification.service.repository_binding", lambda *args: {"source_root": str(source)})
    monkeypatch.setattr("app.verification.service._target_ready", lambda *args: True)
    response = client.get("/api/v1/chat/verification-environments/preflight", params={"space_id": "space", "repository_id": "repo"})
    assert response.json()["data"]["status"] == "ready"
    monkeypatch.setenv("MOONBOX_VERIFICATION_PNPM_VERSION", "10.0.0")
    assert client.get("/api/v1/chat/verification-environments/preflight", params={"space_id": "space", "repository_id": "repo"}).json()["data"]["status"] == "unavailable"
