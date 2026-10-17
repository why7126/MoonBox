from test_chat import chat
from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib
from sqlalchemy import update

from app.verification import tasks, worker
from app.chat.schema import verification_tasks


def test_worker_claim_and_restart_never_fabricate_pass(chat, monkeypatch):
    _, factory = chat
    monkeypatch.setattr("app.verification.tasks.scope.authorize", lambda *args, **kwargs: object())
    monkeypatch.setattr("app.verification.tasks.inspect_authorized", lambda *args: {
        "status": "ready", "environment_key": "a" * 64})
    with factory() as db:
        created = tasks.create_task(db, "alice", "space", "repo", "idempotent", "chromium")
    with factory() as db:
        claimed = worker.claim(db)
        assert claimed["id"] == created["id"]
        assert worker.claim(db) is None
    with factory() as db:
        assert worker.recover_interrupted(db) == 1
    monkeypatch.setattr("app.verification.tasks.repository_binding", lambda *args: {"source_root": "synthetic"})
    with factory() as db:
        recovered = tasks.get_task(db, "alice", created["id"])
    assert recovered["status"] == "blocked"
    assert recovered["error_code"] == "worker_restart"


def test_prune_deletes_only_expired_terminal_evidence(chat, monkeypatch, tmp_path):
    _, factory = chat
    monkeypatch.setattr("app.verification.tasks.scope.authorize", lambda *args, **kwargs: object())
    monkeypatch.setattr("app.verification.tasks.inspect_authorized", lambda *args: {
        "status": "ready", "environment_key": "a" * 64})
    with factory() as db:
        old = tasks.create_task(db, "alice", "space", "repo", "old", "chromium")
        active = tasks.create_task(db, "alice", "space", "repo", "active", "firefox")
        timestamp = (datetime.now(timezone.utc) - timedelta(days=8)).isoformat(timespec="seconds")
        db.execute(update(verification_tasks).where(verification_tasks.c.id == old["id"]).values(
            status="passed", completed_at=timestamp))
        db.execute(update(verification_tasks).where(verification_tasks.c.id == active["id"]).values(
            status="running", completed_at=timestamp))
        db.commit()
    parent = tmp_path / hashlib.sha256(b"space\0repo").hexdigest()
    for item in (old, active):
        folder = parent / item["id"]
        folder.mkdir(parents=True)
        (folder / "screenshot.png").write_bytes(b"fixture")
    assert worker.prune_evidence(factory, tmp_path) == 1
    assert not (parent / old["id"]).exists()
    assert (parent / active["id"]).exists()
