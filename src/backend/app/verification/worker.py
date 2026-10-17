"""独立验证 worker：领取、准备、运行、取消与重启恢复。"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import threading
import time
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select, update

from app.chat import service as chat_service
from app.chat.schema import verification_tasks
from app.chat.settings import repository_binding
from app.chat.workspace import prepare_workspace, trusted_directory, WorkspaceError
from app.db.session import get_session_factory, init_database
from app.governance import scope
from app.verification.artifacts import verified_artifact, ArtifactError
from app.verification.environment import inspect_environment, EnvironmentError
from app.verification.preparation import prepare_node_artifact, PreparationError
from app.verification.runner import probe_browser_image, run_browser_acceptance, RunnerUnavailable
from app.verification.tasks import _trace


def recover_interrupted(db) -> int:
    rows = db.execute(select(verification_tasks).where(
        verification_tasks.c.status.in_(("preparing", "running", "cancelling")))).mappings().all()
    for row in rows:
        target = "cancelled" if row["status"] == "cancelling" else "blocked"
        error = "cancelled" if target == "cancelled" else "worker_restart"
        db.execute(update(verification_tasks).where(verification_tasks.c.id == row["id"]).values(
            status=target, error_code=error, completed_at=chat_service.now(), updated_at=chat_service.now()))
        _trace(db, dict(row), target, error)
    db.commit()
    return len(rows)


def claim(db) -> dict | None:
    candidate = db.execute(select(verification_tasks).where(verification_tasks.c.status == "queued")
        .order_by(verification_tasks.c.created_at, verification_tasks.c.id).limit(1)).mappings().first()
    if not candidate:
        return None
    won = db.execute(update(verification_tasks).where(verification_tasks.c.id == candidate["id"],
        verification_tasks.c.status == "queued").values(status="preparing", started_at=chat_service.now(),
        updated_at=chat_service.now())).rowcount
    if won != 1:
        db.rollback()
        return None
    _trace(db, dict(candidate), "preparing")
    db.commit()
    return dict(candidate)


def _current(factory, task_id: str) -> dict:
    with factory() as db:
        return dict(db.execute(select(verification_tasks).where(verification_tasks.c.id == task_id)).mappings().one())


def _finish(factory, row: dict, status: str, *, error: str | None = None,
            result: dict | None = None, image_digest: str | None = None) -> None:
    with factory() as db:
        current = db.execute(select(verification_tasks).where(verification_tasks.c.id == row["id"])).mappings().one()
        if current["status"] == "cancelling":
            status, error, result = "cancelled", "cancelled", None
        if current["status"] not in ("preparing", "running", "cancelling"):
            return
        db.execute(update(verification_tasks).where(verification_tasks.c.id == row["id"]).values(
            status=status, error_code=error, result=json.dumps(result or {}, sort_keys=True),
            image_digest=image_digest, completed_at=chat_service.now(), updated_at=chat_service.now()))
        _trace(db, dict(current), status, error)
        db.commit()


def _cancel_watch(factory, task_id: str, stop: threading.Event) -> None:
    docker = shutil.which("docker")
    if not docker:
        return
    while not stop.wait(0.5):
        try:
            if _current(factory, task_id)["status"] == "cancelling":
                subprocess.run([docker, "rm", "--force", "moonbox-verification-" + task_id],
                               capture_output=True, timeout=10, check=False)
                return
        except Exception:
            continue


def prune_evidence(factory, evidence_root: Path) -> int:
    """Delete only terminal task screenshots older than the seven-day access window."""
    root = trusted_directory(evidence_root)
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    with factory() as db:
        rows = db.execute(select(verification_tasks.c.id, verification_tasks.c.space_id,
            verification_tasks.c.repository_id, verification_tasks.c.completed_at).where(
            verification_tasks.c.status.in_(("passed", "failed", "blocked", "cancelled", "timed_out")),
            verification_tasks.c.completed_at.is_not(None))).all()
    deleted = 0
    for row in rows:
        try:
            task_id = str(UUID(row.id))
            completed = datetime.fromisoformat(row.completed_at.replace("Z", "+00:00"))
            if completed.tzinfo is None:
                completed = completed.replace(tzinfo=timezone.utc)
            if completed > cutoff:
                continue
            key = hashlib.sha256(f"{row.space_id}\0{row.repository_id}".encode()).hexdigest()
            parent = trusted_directory(root / key)
            folder = parent / task_id
            if folder.is_symlink() or not folder.is_dir():
                continue
            shutil.rmtree(folder)
            deleted += 1
        except (ValueError, TypeError, OSError, WorkspaceError):
            continue
    return deleted


def execute(factory, row: dict) -> None:
    stop = threading.Event()
    watcher = threading.Thread(target=_cancel_watch, args=(factory, row["id"], stop), daemon=True)
    watcher.start()
    workspace = None
    try:
        with factory() as db:
            scope.authorize(db, row["actor_id"], row["space_id"], row["repository_id"], write=True)
        binding = repository_binding(row["repository_id"], row["space_id"])
        if not binding:
            raise PreparationError("repository_binding_revoked")
        source = trusted_directory(binding["source_root"])
        workspace_root = trusted_directory(os.environ["MOONBOX_VERIFICATION_WORKSPACE_ROOT"])
        copied = prepare_workspace(source, workspace_root, row["id"])
        workspace = copied["path"]
        relative = binding.get("verification_project_subdir", ".")
        from app.verification.service import _project_root
        project = _project_root({"source_root": str(workspace), "verification_project_subdir": relative})
        image = os.environ["MOONBOX_VERIFICATION_IMAGE_ID"]
        identity = inspect_environment(project, node_version=os.environ["MOONBOX_VERIFICATION_NODE_VERSION"],
            os_name=os.environ.get("MOONBOX_VERIFICATION_OS", "linux"),
            architecture=os.environ["MOONBOX_VERIFICATION_ARCH"], image_digest=image)
        if identity.key != row["environment_key"]:
            raise PreparationError("project_revision_changed")
        if identity.manager != "pnpm" or identity.manager_version != os.environ["MOONBOX_VERIFICATION_PNPM_VERSION"]:
            raise PreparationError("package_manager_image_mismatch")
        if _current(factory, row["id"])["status"] == "cancelling":
            _finish(factory, row, "cancelled", error="cancelled")
            return
        root = trusted_directory(os.environ["MOONBOX_VERIFICATION_ARTIFACT_ROOT"])
        artifact = verified_artifact(root, identity)
        if artifact is None:
            artifact = prepare_node_artifact(project, root, identity,
                registry_url=os.environ.get("MOONBOX_VERIFICATION_REGISTRY_URL", ""),
                network=os.environ.get("MOONBOX_VERIFICATION_PREPARE_NETWORK", ""))
        if _current(factory, row["id"])["status"] == "cancelling":
            _finish(factory, row, "cancelled", error="cancelled")
            return
        with factory() as db:
            db.execute(update(verification_tasks).where(verification_tasks.c.id == row["id"],
                verification_tasks.c.status == "preparing").values(status="running", image_digest=image,
                environment_key=identity.key, updated_at=chat_service.now()))
            _trace(db, dict(row, environment_key=identity.key), "running")
            db.commit()
        selectors = binding.get("verification_selectors", ["body"])
        if not isinstance(selectors, list) or any(not isinstance(item, str) for item in selectors):
            raise PreparationError("verification_plan_invalid")
        steps = binding.get("verification_steps", [])
        result = run_browser_acceptance(image, network=os.environ["MOONBOX_VERIFICATION_BROWSER_NETWORK"],
            target_url=binding["verification_target_url"], browser=row["browser"],
            viewports=[{"width": 1440, "height": 900}, {"width": 390, "height": 844}],
            selectors=selectors, steps=steps, artifact_path=artifact,
            evidence_root=Path(os.environ["MOONBOX_VERIFICATION_EVIDENCE_ROOT"]),
            space_id=row["space_id"], repository_id=row["repository_id"], task_id=row["id"])
        _finish(factory, row, "passed", result=result, image_digest=image)
    except RunnerUnavailable as exc:
        status = "timed_out" if exc.code == "browser_acceptance_timed_out" else (
            "failed" if exc.code in ("selector_missing", "target_response_failed", "step_failed") else "blocked")
        _finish(factory, row, status, error=exc.code)
    except (chat_service.ChatError, PreparationError, ArtifactError, EnvironmentError,
            WorkspaceError, KeyError, ValueError, OSError) as exc:
        code = getattr(exc, "code", "verification_environment_failed")
        if not isinstance(code, str):
            code = "verification_authorization_revoked"
        _finish(factory, row, "blocked", error=code)
    finally:
        stop.set()
        watcher.join(timeout=2)
        if workspace is not None and workspace.is_dir():
            shutil.rmtree(workspace, ignore_errors=True)


def main() -> None:
    init_database()
    state = trusted_directory(os.environ["MOONBOX_VERIFICATION_STATE_ROOT"])
    lock = (state / "worker.lock").open("w")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    factory = get_session_factory()
    with factory() as db:
        interrupted = list(db.scalars(select(verification_tasks.c.id).where(
            verification_tasks.c.status.in_(("preparing", "running", "cancelling")))))
        recover_interrupted(db)
    docker = shutil.which("docker")
    if docker:
        for task_id in interrupted:
            subprocess.run([docker, "rm", "--force", "moonbox-verification-" + task_id],
                           capture_output=True, timeout=10, check=False)
    image = os.environ["MOONBOX_VERIFICATION_IMAGE_ID"]
    probe = probe_browser_image(image)
    if (probe["node_version"] != os.environ["MOONBOX_VERIFICATION_NODE_VERSION"] or
        probe["pnpm_version"] != os.environ["MOONBOX_VERIFICATION_PNPM_VERSION"]):
        raise RuntimeError("verification_toolchain_mismatch")
    heartbeat_stop = threading.Event()
    def heartbeat():
        marker = state / "worker-ready.json"
        while not heartbeat_stop.is_set():
            temp = state / "worker-ready.tmp"
            temp.write_text(json.dumps({"time": time.time(), "image_digest": image,
                "node_version": os.environ["MOONBOX_VERIFICATION_NODE_VERSION"],
                "pnpm_version": os.environ["MOONBOX_VERIFICATION_PNPM_VERSION"],
                "architecture": os.environ["MOONBOX_VERIFICATION_ARCH"],
                "browsers": probe["versions"]}, sort_keys=True))
            temp.chmod(0o600)
            os.replace(temp, marker)
            heartbeat_stop.wait(1)
    heartbeat_thread = threading.Thread(target=heartbeat, daemon=True)
    heartbeat_thread.start()
    running = True
    def stop(*_):
        nonlocal running
        running = False
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        maintenance_at = 0.0
        with ThreadPoolExecutor(max_workers=2, thread_name_prefix="verification") as pool:
            active = {}
            while running:
                for future, row in list(active.items()):
                    if not future.done():
                        continue
                    try:
                        future.result()
                    except Exception:
                        _finish(factory, row, "blocked", error="worker_unhandled_error")
                    del active[future]
                if time.monotonic() >= maintenance_at:
                    try:
                        prune_evidence(factory, Path(os.environ["MOONBOX_VERIFICATION_EVIDENCE_ROOT"]))
                    except (KeyError, WorkspaceError):
                        pass
                    maintenance_at = time.monotonic() + 3600
                if len(active) < 2:
                    with factory() as db:
                        row = claim(db)
                    if row:
                        active[pool.submit(execute, factory, row)] = row
                        continue
                time.sleep(0.5)
    finally:
        heartbeat_stop.set()
        heartbeat_thread.join(timeout=2)
        (state / "worker-ready.json").unlink(missing_ok=True)


if __name__ == "__main__":
    main()
