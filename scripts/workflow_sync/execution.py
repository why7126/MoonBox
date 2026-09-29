"""Execution facts are written before replayable Issue/Sprint projections."""
from __future__ import annotations

import contextlib
import fcntl
import hashlib
import os
import re
import sys
import tempfile
from pathlib import Path

from .shared import change_state, execution_metadata

from .collect import parse_frontmatter_yaml, read_text
from .timefmt import now_shanghai

EVENTS = {"opsx.start", "opsx.progress", "opsx.apply"}


@contextlib.contextmanager
def sync_lock(root: Path):
    directory = Path(tempfile.gettempdir()) / f"moonbox-workflow-{os.getuid()}"
    directory.mkdir(mode=0o700, exist_ok=True)
    path = directory / (hashlib.sha256(str(root.resolve()).encode()).hexdigest() + ".lock")
    with path.open("a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def atomic_write(path: Path, text: str, original: str) -> None:
    """Detect external edits; cooperative writers additionally hold sync_lock."""
    if path.is_symlink():
        raise ValueError("Refusing symlink write")
    if (path.read_text(encoding="utf-8") if path.exists() else "") != original:
        raise ValueError("Concurrent modification; retry workflow sync")
    fd, name = tempfile.mkstemp(prefix=".workflow-", dir=path.parent)
    try:
        os.fchmod(fd, path.stat().st_mode & 0o777 if path.exists() else 0o644)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        if (path.read_text(encoding="utf-8") if path.exists() else "") != original:
            raise ValueError("Concurrent modification; retry workflow sync")
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def transition(root: Path, record, event: str, *, write: bool) -> dict:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", record.change_id):
        raise ValueError("Invalid Change ID")
    path = root / "openspec/changes" / record.change_id / "trace.md"
    if record.location != "active" or path.resolve().parent != (root / "openspec/changes" / record.change_id).absolute():
        raise ValueError("Execution requires a local active Change")
    original = read_text(path)
    trace = parse_frontmatter_yaml(original)
    trace.update(execution_metadata(original))
    state = change_state(trace, record.tasks.done, record.tasks.total)
    execution = trace.get("execution")
    # Legacy completion stays legacy. Do not fabricate historical start times.
    if event == "opsx.apply" and execution is None:
        if record.tasks.total <= 0 or record.tasks.done != record.tasks.total:
            raise ValueError("Completion requires all tasks checked")
        return trace
    if state in {"applied", "archived"}:
        return trace
    if event != "opsx.start" and not (execution or {}).get("started_at"):
        raise ValueError("Run opsx.start before progress/completion")
    execution = dict(execution or {})
    if not execution.get("schema_version"):
        execution["schema_version"] = 1
    if not execution.get("started_at"):
        execution["started_at"] = now_shanghai()
    if "completed_at" not in execution:
        execution["completed_at"] = None
    if event == "opsx.apply":
        if record.tasks.total <= 0 or record.tasks.done != record.tasks.total:
            raise ValueError("Completion requires all tasks checked")
        execution["completed_at"] = now_shanghai()
    # Duplicate start never erases the last meaningful progress event.
    if event != "opsx.start" or "last_event" not in execution:
        execution["last_event"] = event
    trace["execution"] = execution
    trace["status"] = change_state(trace, record.tasks.done, record.tasks.total)
    match = re.match(r"^---\n(.*?)\n---", original, re.S)
    if not match:
        raise ValueError("Change trace frontmatter missing")
    block = re.sub(r"^execution:\n(?:[ \t]+[^\n]*\n|\n)*", "", match.group(1) + "\n", flags=re.M)
    block = re.sub(r"^status:.*$", "status: " + trace["status"], block, flags=re.M)
    if not re.search(r"^status:", block, re.M):
        block += "status: " + trace["status"] + "\n"
    block += "execution:\n" + "".join(f"  {key}: {value if value is not None else 'null'}\n" for key, value in execution.items())
    updated = original[:match.start(1)] + block.rstrip("\n") + original[match.end(1):]
    if updated != original and write:
        updated = re.sub(r"^updated_at:.*$", "updated_at: " + now_shanghai(), updated, count=1, flags=re.M)
        atomic_write(path, updated, original)
    return trace
