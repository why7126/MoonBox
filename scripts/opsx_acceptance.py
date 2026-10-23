#!/usr/bin/env python3
"""Run scoped OpenSpec acceptance checks and retain a small, verifiable evidence package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import time
import tempfile
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/backend"))
from app.governance.acceptance_evidence import (
    acceptance_manifests, artifact_path, artifacts_match, change_path, effects, fingerprint, fingerprint_input, input_bytes, latest_manifest, ordered_checks, read_plan, readiness, sample_ready, visual_coverage_problems, within
)
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
AC_ID = re.compile(r"^AC-[A-Za-z0-9-]+$")
TERMINAL = {"completed", "failed", "stopped"}


def stamp() -> str:
    return datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")


def artifact_records(root: Path, check: dict) -> tuple[list[dict], list[str]]:
    records = []
    missing = []
    for relative in check.get("artifacts", []):
        path = artifact_path(root, relative)
        if not path.is_file():
            missing.append(f"artifact-missing:{relative}")
            continue
        if path.stat().st_size > 10 * 1024 * 1024:
            missing.append(f"artifact-too-large:{relative}")
            continue
        records.append({"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    return records, missing


def environment_problems(root: Path, check: dict, db_path: Path | None) -> list[str]:
    problems = visual_coverage_problems(check)
    if check["kind"] == "command":
        executable = check["argv"][0]
        if not shutil.which(executable):
            problems.append(f"command-unavailable:{Path(executable).name}")
    else:
        if db_path is None or not db_path.is_file():
            problems.append("product-db-unavailable")
        if not check.get("turn_id") or str(check["turn_id"]).startswith("pending-"):
            problems.append("turn-pending-collection")
    _, missing = artifact_records(root, check)
    problems.extend(p for p in missing if not (p.startswith("artifact-missing:") and p.split(":", 1)[1] in check.get("produces_artifacts", [])))
    return problems


def archived_manifest_artifacts_match(root: Path, archive_dir: Path, manifest: dict) -> bool:
    """Validate an immutable archive manifest plus narrowly scoped command supplements."""
    try:
        plan = read_plan(archive_dir)
        checks = {check["id"]: check for check in plan["checks"]}
        for row in manifest.get("checks", []):
            if artifacts_match(root, row, archive_dir=archive_dir):
                continue
            check_id = row.get("id")
            check = checks.get(check_id)
            if not check or check.get("kind") != "command" or row.get("status") != "passed":
                return False
            supplement_path = archive_dir / "evidence" / "acceptance" / "supplements" / f"{check_id}.json"
            supplement = json.loads(supplement_path.read_text(encoding="utf-8"))
            if not isinstance(supplement, dict) or not isinstance(supplement.get("artifacts"), list):
                return False
            expected = {
                "schema_version": 1,
                "change_id": plan["change_id"],
                "source_run_id": manifest["run_id"],
                "check_id": check_id,
                "input_fingerprint": fingerprint(root, check),
                "argv": check["argv"],
                "exit_code": 0,
            }
            if any(supplement.get(key) != value for key, value in expected.items()):
                return False
            overrides = {item["path"]: item for item in supplement.get("artifacts", [])}
            if len(overrides) != len(supplement["artifacts"]):
                return False
            used: set[str] = set()
            for item in row.get("artifacts", []):
                parts = Path(item["path"]).parts
                path = artifact_path(root, item["path"])
                if len(parts) >= 4 and parts[:3] == ("openspec", "changes", plan["change_id"]):
                    path = within(archive_dir, str(Path(*parts[3:])))
                if not path.is_file():
                    return False
                actual = hashlib.sha256(path.read_bytes()).hexdigest()
                if actual == item["sha256"]:
                    continue
                override = overrides.get(item["path"])
                if not override or override.get("previous_sha256") != item["sha256"] or override.get("current_sha256") != actual:
                    return False
                used.add(item["path"])
            if used != set(overrides):
                return False
        return True
    except (OSError, ValueError, KeyError, TypeError):
        return False


def reusable_checks(root: Path, change_dir: Path, plan: dict) -> dict[str, dict]:
    candidates: dict[str, dict] = {}
    planned = {check["id"]: check for check in plan["checks"]}
    observed: set[str] = set()
    current_fingerprints = {name: fingerprint(root, check) for name, check in planned.items()}
    for manifest in acceptance_manifests(change_dir):
        for row in manifest.get("checks", []):
            name = row.get("id")
            # A diagnostic preflight never ran this check. Keep looking for an
            # earlier matching pass instead of letting a missing artifact in a
            # different AC erase otherwise valid evidence.
            if name not in planned or name in observed or row.get("reason") in {"not-selected", "preflight-failed", "dependency-blocked", "pending-collection"}:
                continue
            check = planned[name]
            if row.get("fingerprint") != current_fingerprints[name]:
                continue
            observed.add(name)
            if row.get("status") == "passed" and sample_ready(check) and not effects(root, check) and not visual_coverage_problems(check) and artifacts_match(root, row):
                candidates[name] = row
    return candidates


def validate_report(manifest: dict, summary: str) -> None:
    if not summary.startswith("---\ntitle: ") or "\n---\n\n# " not in summary:
        raise ValueError("acceptance summary title/frontmatter missing")
    for row in manifest["checks"]:
        if f"| {row['id']} | {row['status']} |" not in summary:
            raise ValueError(f"acceptance summary missing {row['id']}")
        for kind in row.get("evidence_kinds", []):
            if kind not in summary:
                raise ValueError(f"acceptance summary missing evidence kind for {row['id']}")
        for artifact in row.get("artifacts", []):
            if artifact["path"] not in summary:
                raise ValueError(f"acceptance summary missing evidence path for {row['id']}")
    if f"结论：{manifest['status']}。" not in summary:
        raise ValueError("acceptance summary verdict mismatch")


def read_turn(db_path: Path, turn_id: str) -> dict:
    if not db_path.is_file():
        raise ValueError("product SQLite database unavailable")
    uri = f"file:{db_path.resolve()}?mode=ro"
    with sqlite3.connect(uri, uri=True, timeout=2) as db:
        db.row_factory = sqlite3.Row
        turn = db.execute("SELECT id, conversation_id, status, error_code FROM chat_turns WHERE id=?", (turn_id,)).fetchone()
        if turn is None:
            raise ValueError("product turn not found")
        event_rows = db.execute("SELECT sequence, event_type, payload FROM chat_events WHERE turn_id=? AND event_type='execution.tool' ORDER BY sequence", (turn_id,)).fetchall()
    commands = []
    for row in event_rows:
        try:
            payload = json.loads(row["payload"])
        except (ValueError, TypeError):
            continue
        if payload.get("type") != "commandExecution":
            continue
        commands.append({
            "sequence": row["sequence"],
            "phase": payload.get("phase"),
            "exit_code": payload.get("exit_code"),
            "command": (payload.get("arguments") or {}).get("command", ""),
            "acceptance_gate_blocked": "ACCEPTANCE_GATE_BLOCKED" in str(payload.get("result") or ""),
        })
    error_code = turn["error_code"]
    if error_code and not re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", error_code):
        error_code = "redacted"
    return {"turn_id": turn["id"], "conversation_id": turn["conversation_id"], "status": turn["status"], "error_code": error_code, "commands": commands}


def trusted_archive_proof(db_path: Path, turn_id: str, object_id: str) -> dict:
    """Read the direct archive path's durable result without inventing a tool event."""
    uri = f"file:{db_path.resolve()}?mode=ro"
    with sqlite3.connect(uri, uri=True, timeout=2) as db:
        db.row_factory = sqlite3.Row
        row = db.execute("""SELECT t.prompt, t.status, t.error_code, c.owner_id,
                          c.space_id, c.repository_id FROM chat_turns t
                          JOIN chat_conversations c ON c.id=t.conversation_id WHERE t.id=?""", (turn_id,)).fetchone()
        if row is None:
            raise ValueError("product turn not found")
        primary = db.execute("SELECT object_id FROM chat_relations WHERE conversation_id=(SELECT conversation_id FROM chat_turns WHERE id=?) AND role='primary'", (turn_id,)).fetchall()
        operations = db.execute("SELECT stage, actor_id FROM governance_archive_operations WHERE change_id=?", (object_id,)).fetchall()
        events = db.execute("SELECT source_id, event_type, payload FROM chat_events WHERE turn_id=? ORDER BY sequence", (turn_id,)).fetchall()
    observed = {}
    for event in events:
        if event["source_id"] not in {"archive:started", "archive:usage", "archive:terminal"}:
            continue
        try:
            payload = json.loads(event["payload"])
            if not isinstance(payload, dict):
                return {"verified": False, "reason": "archive-event-invalid"}
            observed[event["source_id"]] = (event["event_type"], payload)
        except (TypeError, ValueError):
            return {"verified": False, "reason": "archive-event-invalid"}
    started = observed.get("archive:started")
    usage = observed.get("archive:usage")
    terminal = observed.get("archive:terminal")
    verified = (row["prompt"] == f"/sprint-archive {object_id}"
                and row["status"] == "completed" and row["error_code"] is None
                and bool(row["space_id"] and row["repository_id"])
                and len(primary) == 1 and primary[0]["object_id"] == object_id
                and len(operations) == 1 and operations[0]["stage"] == "completed"
                and operations[0]["actor_id"] == row["owner_id"]
                and started == ("execution.state", {"status": "running", "executor": "trusted_archive"})
                and terminal == ("execution.state", {"status": "completed"})
                and usage is not None and usage[0] == "execution.usage"
                and usage[1].get("usage_scope") == "trusted_archive_v1"
                and usage[1].get("total_tokens") == 0
                and usage[1].get("usage_pending") is False)
    return {"verified": bool(verified), "reason": "same-turn-trusted-archive" if verified else "trusted-archive-proof-incomplete",
            "operation_stage": operations[0]["stage"] if len(operations) == 1 else None,
            "model_tokens": usage[1].get("total_tokens") if usage else None}


def run_command(check: dict, root: Path) -> dict:
    timeout = min(max(int(check.get("timeout_seconds", 120)), 1), 900)
    attempts = min(max(int(check.get("safe_retries", 0)), 0), 2) + 1
    result = {"status": "blocked", "reason": "not-run", "attempts": 0}
    for attempt in range(attempts):
        result["attempts"] = attempt + 1
        try:
            done = subprocess.run(check["argv"], cwd=root, text=True, capture_output=True, timeout=timeout, check=False)
            result = {"status": "passed" if done.returncode == 0 else "failed", "reason": "exit-code", "exit_code": done.returncode, "attempts": attempt + 1}
            if done.returncode == 0:
                break
        except (OSError, subprocess.TimeoutExpired) as exc:
            result = {"status": "blocked", "reason": "timeout" if isinstance(exc, subprocess.TimeoutExpired) else "unavailable", "attempts": attempt + 1}
        if attempt + 1 < attempts:
            time.sleep(min(2 ** attempt, 2))
    return result


def run_product_turn(check: dict, db_path: Path) -> dict:
    timeout = min(max(int(check.get("timeout_seconds", 180)), 1), 900)
    deadline = time.monotonic() + timeout
    while True:
        try:
            turn = read_turn(db_path, check["turn_id"])
        except (sqlite3.Error, ValueError) as exc:
            return {"status": "blocked", "reason": type(exc).__name__, "turn_id": check["turn_id"]}
        if turn["status"] in TERMINAL or time.monotonic() >= deadline:
            break
        time.sleep(2)
    if check.get("execution_proof") == "trusted_archive_v1":
        try:
            proof = trusted_archive_proof(db_path, check["turn_id"], check["trusted_archive_object_id"])
        except (sqlite3.Error, ValueError) as exc:
            return {"status": "blocked", "reason": type(exc).__name__, "turn_id": check["turn_id"]}
        status = "passed" if proof["verified"] else "failed" if turn["status"] in TERMINAL else "blocked"
        return {"status": status, "reason": proof["reason"], "turn_id": turn["turn_id"],
                "conversation_id": turn["conversation_id"], "turn_status": turn["status"],
                "error_code": turn["error_code"], "operation_stage": proof.get("operation_stage"),
                "model_tokens": proof.get("model_tokens")}
    matching = [c for c in turn["commands"] if check["command_contains"] in c["command"] and c["phase"] == "completed"]
    expected_exit = check.get("expected_exit_code", 0)
    successful = [c for c in matching if c["exit_code"] == expected_exit and
                  (not check.get("require_acceptance_gate_blocked", False) or c["acceptance_gate_blocked"])]
    status = "passed" if turn["status"] == "completed" and successful else "failed" if turn["status"] in TERMINAL else "blocked"
    return {
        "status": status,
        "reason": "same-turn-complete" if status == "passed" else "turn-or-command-incomplete",
        "turn_id": turn["turn_id"], "conversation_id": turn["conversation_id"],
        "turn_status": turn["status"], "error_code": turn["error_code"],
        "command_sequence": successful[-1]["sequence"] if successful else None,
        "command_exit_code": successful[-1]["exit_code"] if successful else None,
    }


def run_acceptance(root: Path, change: str, db_path: Path | None, selected: set[str] | None = None,
                   db_aliases: dict[str, Path] | None = None, activity: dict | None = None) -> dict:
    change_dir = change_path(root, change)
    plan = read_plan(change_dir)
    started_run = time.monotonic()
    previous_checks = reusable_checks(root, change_dir, plan)
    run_id = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y%m%d%H%M%S%f") + "-" + uuid4().hex[:8]
    rows: list[dict] = []
    results = {}
    preflight_results = []
    for argv in plan.get("preflight", []):
        if not isinstance(argv, list) or not argv or any(not isinstance(arg, str) for arg in argv):
            raise ValueError("preflight must be argv lists")
        result = run_command({"argv": argv, "timeout_seconds": 30}, root)
        preflight_results.append(result)
        if result["status"] != "passed":
            break
    common_ok = all(r["status"] == "passed" for r in preflight_results)
    cache = {}
    metrics = {"command_executions": 0, "deduplicated": 0, "reused": 0,
               "preflight_ms": round((time.monotonic() - started_run) * 1000)}
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=False)
    source_revision = head.stdout.strip() if re.fullmatch(r"[0-9a-f]{40}", head.stdout.strip()) else None

    def execute(check: dict, current_fingerprint: str, product_db: Path | None) -> dict:
        started = time.monotonic()
        deduplicated = False
        if check["kind"] == "command":
            key = hashlib.sha256(json.dumps({
                "argv": check["argv"], "timeout": check.get("timeout_seconds", 120),
                "retries": check.get("safe_retries", 0), "environment": plan.get("environment"),
                "contract": plan.get("environment_contract"), "preflight": check.get("preflight"),
                "inputs": [(p, hashlib.sha256(input_bytes(root, check, p)).hexdigest()) for p in check["inputs"]],
            }, sort_keys=True).encode()).hexdigest()
            if check.get("deduplicate") and key in cache:
                result = dict(cache[key])
                deduplicated = True
                metrics["deduplicated"] += 1
            else:
                result = run_command(check, root)
                metrics["command_executions"] += 1
                if check.get("deduplicate") and result["status"] == "passed":
                    cache[key] = dict(result)
        else:
            result = run_product_turn(check, product_db)
        artifact_list, missing_artifacts = artifact_records(root, check)
        problems = effects(root, check) + missing_artifacts
        if result["status"] == "passed" and problems:
            result.update(status="failed", reason="effect-missing")
        if result["status"] == "passed" and not sample_ready(check):
            result.update(status="blocked", reason="sample-incomplete")
        if fingerprint(root, check) != current_fingerprint:
            result.update(status="blocked", reason="inputs-changed-during-check")
        return {"id": check["id"], "fingerprint": current_fingerprint, "reused": False,
                "deduplicated": deduplicated, **result, "effect_problems": problems,
                "artifacts": artifact_list, "duration_ms": round((time.monotonic() - started) * 1000)}

    for check in ordered_checks(plan["checks"]):
        name = check["id"]
        current_fingerprint = fingerprint(root, check)
        old = previous_checks.get(name)
        reusable = bool(old and old.get("fingerprint") == current_fingerprint and not effects(root, check) and artifacts_match(root, old))
        product_db = (db_aliases or {}).get(check.get("product_db", "default"), db_path)
        problems = environment_problems(root, check, product_db)
        if "visual" in check.get("evidence_kinds", []) and not (plan.get("preflight") or check.get("preflight")):
            problems.append("visual-preflight-missing")
        dependencies = [d for d in check.get("depends_on", []) if results.get(d, {}).get("status") != "passed"]
        row = {"id": name, "fingerprint": current_fingerprint, "status": "blocked", "reused": False}
        if selected and name not in selected and not reusable:
            row.update(reason="not-selected")
        elif dependencies:
            row.update(reason="dependency-blocked", effect_problems=["dependency:" + d for d in dependencies])
        elif reusable:
            row = {**old, "reused": True, "duration_ms": 0, "deduplicated": False}
            metrics["reused"] += 1
        elif not common_ok:
            row.update(reason="preflight-failed", effect_problems=["common-preflight-failed"])
        elif check.get("collection", {}).get("state") == "blocked":
            row.update(reason="collection-blocked", effect_problems=problems)
        elif check.get("collection", {}).get("state", "collected") != "collected":
            row.update(reason="pending-collection", effect_problems=problems)
        elif problems:
            collecting = all(p.startswith(("artifact-missing:", "turn-pending-collection")) for p in problems)
            row.update(reason="pending-collection" if collecting else "preflight-failed", effect_problems=problems)
        else:
            local = []
            for argv in check.get("preflight", []):
                if not isinstance(argv, list) or not argv or any(not isinstance(a, str) for a in argv):
                    raise ValueError("AC preflight must be argv lists")
                local.append(run_command({"argv": argv, "timeout_seconds": 30}, root))
                if local[-1]["status"] != "passed":
                    break
            if any(r["status"] != "passed" for r in local):
                row.update(reason="preflight-failed", effect_problems=["local-preflight-failed"])
            else:
                row = execute(check, current_fingerprint, product_db)
        row["evidence_kinds"] = check.get("evidence_kinds") or [check["kind"]]
        row["collection_state"] = ("passed" if row["status"] == "passed" else "failed" if row["status"] == "failed"
                                   else "pending_collection" if row["reason"] == "pending-collection" else "blocked")
        rows.append(row)
        results[name] = row
        # A validated diagnostic checkpoint preserves completed work after interruption.
        checkpoint = {"schema_version": 1, "change_id": change, "run_id": run_id + "-checkpoint-" + name,
                      "created_at": stamp(), "scope": "diagnostic", "status": "blocked", "checks": [row]}
        checkpoint_summary = "---\ntitle: 验收续接检查点\n---\n\n# 验收续接检查点\n\n结论：blocked。\n" + "\n".join(
            f"| {r['id']} | {r['status']} | {','.join(r['evidence_kinds'])} | " +
            ','.join(a['path'] for a in r.get('artifacts', [])) + " |" for r in [row])
        validate_report(checkpoint, checkpoint_summary)
        checkpoint_dir = change_dir / "evidence/acceptance/checkpoints" / (run_id + "-checkpoint-" + name)
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        (checkpoint_dir / "summary.md").write_text(checkpoint_summary)
        temp = checkpoint_dir / "manifest.tmp"
        temp.write_text(json.dumps(checkpoint, ensure_ascii=False))
        os.replace(temp, checkpoint_dir / "manifest.json")
    rows.sort(key=lambda row: next(i for i, c in enumerate(plan["checks"]) if c["id"] == row["id"]))
    verdict = "passed" if all(r["status"] == "passed" for r in rows) else "failed" if any(r["status"] == "failed" for r in rows) else "blocked"
    if not common_ok and verdict == "passed":
        verdict = "blocked"
    diagnostic = not common_ok or any(r.get("reason") in {"not-selected", "preflight-failed", "pending-collection", "dependency-blocked", "collection-blocked"} for r in rows)
    scope = "diagnostic" if diagnostic else "complete"
    metrics.update(duration_ms=round((time.monotonic() - started_run) * 1000),
                   blocked=sum(r["status"] == "blocked" for r in rows),
                   failed=sum(r["status"] == "failed" for r in rows))
    manifest = {"schema_version": 1, "change_id": change, "run_id": run_id, "created_at": stamp(),
                "source_revision": source_revision, "environment": plan.get("environment", "unspecified"),
                "scope": scope, "status": verdict, "preflight": preflight_results, "checks": rows, "metrics": metrics,
                "activity": activity or {"status": "unavailable"}}
    dest = change_dir / "evidence" / "acceptance" / run_id
    dest.parent.mkdir(parents=True, exist_ok=True)
    trace_text = (change_dir / "trace.md").read_text(encoding="utf-8") if (change_dir / "trace.md").is_file() else ""
    title_match = re.search(r"^title:\s*(.+)$", trace_text, re.MULTILINE)
    change_title = title_match.group(1).strip(" '\"") if title_match else change
    summary_title = f"{change_title}自动验收报告（{run_id}）"
    summary = ["---", f"title: {json.dumps(summary_title, ensure_ascii=False)}", f"created_at: {manifest['created_at']}", f"updated_at: {manifest['created_at']}", "---", "", f"# {summary_title}", "", f"结论：{verdict}。范围：{scope}。", "", "| AC | 结论 | 检查来源 | 证据类型 | 证据入口与缺口 |", "|---|---|---|---|---|"]
    for check, row in zip(plan["checks"], rows):
        kinds = ", ".join(row["evidence_kinds"])
        paths = [item["path"] for item in row.get("artifacts", [])]
        details = paths + row.get("effect_problems", [])
        source = row.get("turn_id") or row.get("reason", "command")
        summary.append(f"| {row['id']} | {row['status']} | {source} | {kinds} | {'<br>'.join(details) or '无'} |")
    summary_text = "\n".join(summary) + "\n"
    validate_report(manifest, summary_text)
    staging = Path(tempfile.mkdtemp(prefix=".staging-", dir=dest.parent))
    try:
        (staging / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (staging / "summary.md").write_text(summary_text, encoding="utf-8")
        if json.loads((staging / "manifest.json").read_text(encoding="utf-8")) != manifest:
            raise ValueError("acceptance manifest round-trip mismatch")
        validate_report(manifest, (staging / "summary.md").read_text(encoding="utf-8"))
        os.replace(staging, dest)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    from app.governance.archive_admission import change_acceptance
    archive = change_acceptance(root, change)
    return {"status": verdict, "scope": scope, "run_id": run_id, "path": str(dest.relative_to(root)), "checks": len(rows), "metrics": metrics, "pending_collection": [r["id"] for r in rows if r.get("collection_state") == "pending_collection"],
            "archive_admission": archive, "archive_ready": verdict == "passed" and archive["ready"],
            "final_admission_required": True}


def acceptance_queue(root: Path, change: str, db_path: Path | None, aliases: dict | None = None) -> dict:
    """Read-only handoff to the Agent; never creates samples or grants permission."""
    directory = change_path(root, change)
    plan = read_plan(directory)
    reusable = reusable_checks(root, directory, plan)
    queue = []
    for check in ordered_checks(plan["checks"]):
        name = check["id"]
        problems = environment_problems(root, check, (aliases or {}).get(check.get("product_db", "default"), db_path))
        dependencies = [d for d in check.get("depends_on", []) if d not in reusable]
        if name in reusable and not dependencies:
            state, action = "passed", "reuse"
        elif dependencies:
            state, action = "blocked", "complete-dependencies"
        elif any(p.startswith(("product-db-unavailable", "command-unavailable")) for p in problems):
            state, action = "blocked", "restore-environment"
        elif check.get("collection", {}).get("state") == "blocked":
            state, action = "blocked", "resolve-recorded-blocker"
        elif problems or not sample_ready(check) or check.get("collection", {}).get("state") in {"pending", "collecting", "blocked"}:
            state, action = "pending_collection", "collect-with-existing-authorization"
        else:
            state, action = "ready", "execute-check"
        queue.append({"id": name, "state": state, "action": action, "dependencies": dependencies, "gaps": problems})
    return {"status": "queue-ready", "change_id": change, "queue": queue,
            "executable": [r["id"] for r in queue if r["state"] == "ready"],
            "pending_collection": [r["id"] for r in queue if r["state"] == "pending_collection"]}


def activity_summary(path: Path | None) -> dict:
    if path is None:
        return {"status": "unavailable"}
    events = json.loads(path.read_text())
    phases = {"environment", "collection", "testing", "repair", "waiting", "archive"}
    if not isinstance(events, list):
        raise ValueError("activity must be a list of phase/duration_ms events")
    totals = {phase: 0 for phase in sorted(phases)}
    interventions = 0
    for event in events:
        if (not isinstance(event, dict) or set(event) - {"phase", "duration_ms", "human_intervention"}
                or event.get("phase") not in phases or type(event.get("duration_ms")) is not int
                or event["duration_ms"] < 0 or type(event.get("human_intervention", False)) is not bool):
            raise ValueError("invalid activity event; raw text/identity is not accepted")
        totals[event["phase"]] += event["duration_ms"]
        interventions += int(event.get("human_intervention", False))
    return {"status": "reported", "phase_ms": totals, "human_interventions": interventions,
            "event_count": len(events)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--change", required=True)
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--db", type=Path, help="Authorized local product SQLite path; read only")
    parser.add_argument("--db-alias", action="append", default=[], metavar="NAME=PATH",
                        help="Additional authorized read-only product SQLite for checks declaring product_db")
    parser.add_argument("--only", action="append", help="Run selected AC; reuse valid others")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--readiness", action="store_true", help="Check current evidence without executing")
    mode.add_argument("--archive-readiness", action="store_true", help="Check final shared product/CLI admission after all acceptance hooks")
    parser.add_argument("--activity-file", type=Path, help="Optional sanitized phase duration events; distinct from measured check timing")
    mode.add_argument("--queue", action="store_true", help="Read-only per-AC next actions for Agent collection and resume")
    args = parser.parse_args()
    try:
        aliases = {}
        for item in args.db_alias:
            name, sep, path = item.partition("=")
            if not sep or not re.fullmatch(r"[a-z][a-z0-9_-]*", name) or not path:
                raise ValueError("invalid --db-alias; expected NAME=PATH")
            aliases[name] = Path(path)
        if args.archive_readiness:
            from app.governance.archive_admission import change_acceptance
            admission = change_acceptance(args.root, args.change)
            result = {**admission, "status": "ready" if admission["ready"] else "blocked"}
        else:
            result = acceptance_queue(args.root, args.change, args.db, aliases) if args.queue else readiness(args.root, args.change) if args.readiness else run_acceptance(args.root, args.change, args.db, set(args.only) if args.only else None, aliases, activity_summary(args.activity_file))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = {"status": "blocked", "reason": str(exc)}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] in {"passed", "ready", "queue-ready"} else 1


if __name__ == "__main__":
    sys.exit(main())
