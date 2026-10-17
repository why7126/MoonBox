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
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
AC_ID = re.compile(r"^AC-[A-Za-z0-9-]+$")
TERMINAL = {"completed", "failed", "stopped"}


def stamp() -> str:
    return datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")


def within(base: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or not relative.strip():
        raise ValueError(f"unsafe relative path: {relative!r}")
    resolved = (base / path).resolve()
    if not resolved.is_relative_to(base.resolve()):
        raise ValueError(f"path escapes project: {relative!r}")
    return resolved


def change_path(root: Path, change: str) -> Path:
    if not ID.fullmatch(change):
        raise ValueError("invalid Change ID")
    path = root / "openspec" / "changes" / change
    if not path.is_dir():
        raise ValueError(f"active Change missing: {change}")
    return path


def read_plan(change_dir: Path) -> dict:
    path = change_dir / "acceptance-plan.json"
    plan = json.loads(path.read_text(encoding="utf-8"))
    plan_change = plan.get("change_id")
    archive_name = bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}-" + re.escape(str(plan_change)), change_dir.name))
    if plan.get("schema_version") != 1 or not isinstance(plan_change, str) or (plan_change != change_dir.name and not archive_name):
        raise ValueError("acceptance plan identity/schema mismatch")
    if not ID.fullmatch(str(plan.get("environment", "unspecified"))):
        raise ValueError("invalid environment label")
    checks = plan.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ValueError("acceptance plan needs checks")
    seen: set[str] = set()
    for check in checks:
        name = check.get("id")
        if not isinstance(name, str) or not AC_ID.fullmatch(name) or name in seen:
            raise ValueError("invalid or repeated AC ID")
        seen.add(name)
        if check.get("kind") not in {"command", "product_turn"}:
            raise ValueError(f"{name}: invalid kind")
        inputs = check.get("inputs")
        if not isinstance(inputs, list) or not inputs or any(not isinstance(p, str) for p in inputs):
            raise ValueError(f"{name}: explicit input files required")
        evidence_kinds = check.get("evidence_kinds", [])
        if not isinstance(evidence_kinds, list) or any(kind not in {"command", "product_turn", "visual", "file_state"} for kind in evidence_kinds):
            raise ValueError(f"{name}: invalid evidence kinds")
        sample = check.get("required_sample")
        allowed_sample_statuses = {"passed", "partial", "pending"}
        if archive_name and change_dir.parent.name == "archive":
            allowed_sample_statuses.add("completed-source-archive")
        if sample is not None and (not isinstance(sample, dict)
                                   or sample.get("status") not in allowed_sample_statuses):
            raise ValueError(f"{name}: invalid required sample status")
        if "visual" in evidence_kinds:
            coverage = check.get("coverage")
            if not check.get("artifacts") or not isinstance(coverage, dict) or any(not isinstance(coverage.get(key), list) or not coverage[key] or any(not isinstance(value, str) or not value.strip() for value in coverage[key]) for key in ("stages", "viewports")):
                raise ValueError(f"{name}: visual evidence requires artifacts, stages and viewports")
        if check["kind"] == "command":
            argv = check.get("argv")
            if not isinstance(argv, list) or not argv or any(not isinstance(a, str) or not a for a in argv):
                raise ValueError(f"{name}: argv list required")
        else:
            if not ID.fullmatch(str(check.get("turn_id", ""))) or not isinstance(check.get("command_contains"), str) or not check["command_contains"]:
                raise ValueError(f"{name}: turn_id and command_contains required")
            if not isinstance(check.get("expected_exit_code", 0), int) or check.get("expected_exit_code", 0) < 0:
                raise ValueError(f"{name}: invalid expected_exit_code")
            if not isinstance(check.get("require_acceptance_gate_blocked", False), bool):
                raise ValueError(f"{name}: invalid require_acceptance_gate_blocked")
            if check.get("require_acceptance_gate_blocked") and (check.get("expected_exit_code") != 1 or not check.get("effects")):
                raise ValueError(f"{name}: negative acceptance gate requires exit code 1 and a state effect")
        for effect in check.get("effects", []):
            if effect.get("kind") not in {"exists", "absent", "contains"} or not isinstance(effect.get("path"), str):
                raise ValueError(f"{name}: invalid file effect")
            if effect["kind"] == "contains" and not isinstance(effect.get("text"), str):
                raise ValueError(f"{name}: contains effect needs text")
        artifacts = check.get("artifacts", [])
        if not isinstance(artifacts, list) or any(not isinstance(item, str) for item in artifacts):
            raise ValueError(f"{name}: artifacts must be relative paths")
        for artifact in artifacts:
            path = within(change_dir.parents[2], artifact)
            relative = path.relative_to(change_dir.parents[2])
            if relative.parts[0] in {"data", "logs", "tmp"} or path.name.startswith(".env"):
                raise ValueError(f"{name}: raw or temporary artifacts cannot be retained")
    issue_id = plan.get("issue_id")
    if issue_id:
        if not isinstance(issue_id, str) or not ID.fullmatch(issue_id) or not issue_id.startswith(("REQ-", "BUG-")):
            raise ValueError("invalid Issue ID")
        root = change_dir.parents[2]
        domain = "requirements" if issue_id.startswith("REQ-") else "bugs"
        matches = [root / "issues" / domain / stage / issue_id / "acceptance.md" for stage in ("plan", "review", "archive")]
        matches = [path for path in matches if path.is_file()]
        if len(matches) != 1:
            raise ValueError("linked Issue acceptance document missing or ambiguous")
        text = matches[0].read_text(encoding="utf-8")
        issue_ac = set(re.findall(r"^(?:- \[[ xX]\] |\|\s*)(AC-[A-Za-z0-9-]+)(?:\b|\s*\|)", text, re.MULTILINE))
        if issue_ac != seen:
            raise ValueError("acceptance plan AC set differs from linked Issue")
    return plan


def fingerprint(root: Path, check: dict) -> str:
    digest = hashlib.sha256(json.dumps(check, ensure_ascii=False, sort_keys=True).encode())
    for relative in check["inputs"]:
        path = within(root, relative)
        digest.update(relative.encode())
        digest.update(fingerprint_input(path, relative) if path.is_file() else b"<missing>")
    return digest.hexdigest()


def sample_ready(check: dict) -> bool:
    sample = check.get('required_sample')
    return not isinstance(sample, dict) or sample.get('status') == 'passed'


def fingerprint_input(path: Path, relative: str) -> bytes:
    """Hash Issue acceptance criteria without Workflow Sync's generated projection."""
    content = path.read_bytes()
    parts = Path(relative).parts
    if not (len(parts) == 5 and parts[0] == "issues"
            and parts[1] in {"bugs", "requirements"}
            and parts[2] in {"plan", "review", "archive"}
            and parts[4] == "acceptance.md"):
        return content
    text = content.decode("utf-8")
    if text.startswith("---\n"):
        _, front, body = text.split("---", 2)
        front = "".join(line for line in front.splitlines(keepends=True)
                        if not re.match(r"^(?:updated_at|acceptance_status):", line))
        text = "---" + front + "---" + body
    text = re.sub(r"(?ms)^## 验收结果回填[ \t]*\n.*?(?=^## |\Z)", "", text)
    return text.encode("utf-8")


def effects(root: Path, check: dict) -> list[str]:
    problems: list[str] = []
    for effect in check.get("effects", []):
        path = within(root, effect["path"])
        kind = effect["kind"]
        if kind == "exists" and not path.exists():
            problems.append(f"missing:{effect['path']}")
        elif kind == "absent" and path.exists():
            problems.append(f"present:{effect['path']}")
        elif kind == "contains" and (not path.is_file() or effect["text"] not in path.read_text(encoding="utf-8", errors="replace")):
            problems.append(f"text-missing:{effect['path']}")
    return problems


def artifact_records(root: Path, check: dict) -> tuple[list[dict], list[str]]:
    records = []
    missing = []
    for relative in check.get("artifacts", []):
        path = within(root, relative)
        if not path.is_file():
            missing.append(f"artifact-missing:{relative}")
            continue
        if path.stat().st_size > 10 * 1024 * 1024:
            missing.append(f"artifact-too-large:{relative}")
            continue
        records.append({"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    return records, missing


def visual_coverage_problems(check: dict) -> list[str]:
    if "visual" not in check.get("evidence_kinds", []):
        return []
    coverage = check["coverage"]
    samples = coverage.get("samples")
    if not isinstance(samples, list) or not samples:
        return ["legacy-coverage-unmapped"]
    planned = {(stage, viewport) for stage in coverage["stages"] for viewport in coverage["viewports"]}
    seen: set[tuple[str, str]] = set()
    problems: list[str] = []
    declared = set(check.get("artifacts", []))
    applicable = 0
    for sample in samples:
        if not isinstance(sample, dict):
            problems.append("coverage-invalid-sample")
            continue
        key = (sample.get("stage"), sample.get("viewport"))
        if not all(isinstance(value, str) and value.strip() for value in key):
            problems.append("coverage-invalid-sample")
            continue
        if key not in planned or key in seen:
            problems.append(f"coverage-invalid-or-duplicate:{key[0]}@{key[1]}")
            continue
        seen.add(key)
        if sample.get("not_applicable") is True:
            if not isinstance(sample.get("reason"), str) or not sample["reason"].strip():
                problems.append(f"coverage-reason-missing:{key[0]}@{key[1]}")
            continue
        paths = sample.get("artifacts")
        if not isinstance(paths, list) or not paths or any(not isinstance(path, str) or path not in declared for path in paths):
            problems.append(f"coverage-artifact-unmapped:{key[0]}@{key[1]}")
        else:
            applicable += 1
    problems.extend(f"coverage-missing:{stage}@{viewport}" for stage, viewport in sorted(planned - seen))
    if not applicable:
        problems.append("coverage-no-applicable-sample")
    return problems


def environment_problems(root: Path, check: dict, db_path: Path | None) -> list[str]:
    problems = visual_coverage_problems(check)
    if check["kind"] == "command":
        executable = check["argv"][0]
        if not shutil.which(executable):
            problems.append(f"command-unavailable:{Path(executable).name}")
    elif db_path is None or not db_path.is_file():
        problems.append("product-db-unavailable")
    _, missing = artifact_records(root, check)
    problems.extend(missing)
    return problems


def artifacts_match(root: Path, row: dict, *, archive_dir: Path | None = None) -> bool:
    for item in row.get("artifacts", []):
        path = within(root, item["path"])
        if archive_dir:
            parts = Path(item["path"]).parts
            if len(parts) >= 4 and parts[:3] == ("openspec", "changes", archive_dir.name[11:]):
                path = within(archive_dir, str(Path(*parts[3:])))
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            return False
    return True


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
                path = within(root, item["path"])
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


def acceptance_manifests(change_dir: Path) -> list[dict]:
    base = change_dir / "evidence" / "acceptance"
    manifests = []
    for path in sorted(base.glob("*/manifest.json"), key=lambda item: item.stat().st_mtime_ns, reverse=True):
        if path.parent.name.startswith("."):
            continue
        try:
            manifests.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            continue
    return manifests


def latest_manifest(change_dir: Path) -> dict | None:
    for manifest in acceptance_manifests(change_dir):
        if manifest.get("scope", "complete") == "complete" and not any(row.get("reason") == "not-selected" for row in manifest.get("checks", [])):
            return manifest
    return None


def reusable_checks(root: Path, change_dir: Path, plan: dict) -> dict[str, dict]:
    candidates: dict[str, dict] = {}
    planned = {check["id"]: check for check in plan["checks"]}
    observed: set[str] = set()
    for manifest in acceptance_manifests(change_dir):
        for row in manifest.get("checks", []):
            name = row.get("id")
            # A diagnostic preflight never ran this check. Keep looking for an
            # earlier matching pass instead of letting a missing artifact in a
            # different AC erase otherwise valid evidence.
            if name not in planned or name in observed or row.get("reason") in {"not-selected", "preflight-failed"}:
                continue
            check = planned[name]
            if row.get("fingerprint") != fingerprint(root, check):
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
                   db_aliases: dict[str, Path] | None = None) -> dict:
    change_dir = change_path(root, change)
    plan = read_plan(change_dir)
    previous_checks = reusable_checks(root, change_dir, plan)
    run_id = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y%m%d%H%M%S%f") + "-" + uuid4().hex[:8]
    rows: list[dict] = []
    preflight = plan.get("preflight", [])
    for argv in preflight:
        if not isinstance(argv, list) or not argv or any(not isinstance(arg, str) for arg in argv):
            raise ValueError("preflight must be argv lists")
    required = [check for check in plan["checks"] if (not selected or check["id"] in selected) and check["id"] not in previous_checks]
    preflight_problems = {check["id"]: environment_problems(root, check, db_path) for check in required}
    if any("visual" in check.get("evidence_kinds", []) for check in required) and not preflight:
        for check in required:
            if "visual" in check.get("evidence_kinds", []):
                preflight_problems[check["id"]].append("visual-preflight-missing")
    preflight_results = []
    if not any(preflight_problems.values()):
        for argv in preflight:
            result = run_command({"argv": argv, "timeout_seconds": 30}, root)
            preflight_results.append(result)
            if result["status"] != "passed":
                break
    if preflight_results and preflight_results[-1]["status"] != "passed":
        result = preflight_results[-1]
        detail = f"plan-preflight-{result['reason']}"
        if "exit_code" in result:
            detail += f"-{result['exit_code']}"
        for check in required:
            preflight_problems[check["id"]].append(detail)
    healthy = not any(preflight_problems.values()) and all(result["status"] == "passed" for result in preflight_results)
    def execute(check: dict, current_fingerprint: str) -> dict:
        started = time.monotonic()
        product_db = (db_aliases or {}).get(check.get("product_db", "default"), db_path)
        result = run_command(check, root) if check["kind"] == "command" else run_product_turn(check, product_db) if product_db else {"status": "blocked", "reason": "product-db-required"}
        artifact_list, missing_artifacts = artifact_records(root, check)
        problems = effects(root, check) + missing_artifacts
        if result["status"] == "passed" and problems:
            result.update(status="failed", reason="effect-missing")
        if result["status"] == "passed" and not sample_ready(check):
            result.update(status="blocked", reason="sample-incomplete")
        return {"id": check["id"], "fingerprint": current_fingerprint, "reused": False, **result, "effect_problems": problems, "artifacts": artifact_list, "duration_ms": round((time.monotonic() - started) * 1000)}

    pending: list[tuple[dict, str]] = []
    for check in plan["checks"]:
        name = check["id"]
        current_fingerprint = fingerprint(root, check)
        old = previous_checks.get(name)
        reusable = bool(old and old.get("status") == "passed" and sample_ready(check) and old.get("fingerprint") == current_fingerprint and not effects(root, check) and not visual_coverage_problems(check) and artifacts_match(root, old))
        if selected and name not in selected and not reusable:
            row = {"id": name, "status": "blocked", "reason": "not-selected", "fingerprint": current_fingerprint}
        elif reusable:
            row = {**old, "reused": True}
        elif not healthy:
            row = {"id": name, "status": "blocked", "reason": "preflight-failed", "fingerprint": current_fingerprint,
                   "effect_problems": preflight_problems.get(name, [])}
        elif check["kind"] == "command" and check.get("parallel_safe") is True:
            pending.append((check, current_fingerprint))
            continue
        else:
            row = execute(check, current_fingerprint)
        rows.append(row)
    if pending:
        with ThreadPoolExecutor(max_workers=min(3, len(pending))) as pool:
            futures = [pool.submit(execute, check, fp) for check, fp in pending]
            rows.extend(future.result() for future in futures)
    rows.sort(key=lambda row: next(index for index, check in enumerate(plan["checks"]) if check["id"] == row["id"]))
    for check, row in zip(plan["checks"], rows):
        row["evidence_kinds"] = check.get("evidence_kinds") or [check["kind"]]
    verdict = "passed" if all(row["status"] == "passed" for row in rows) else "failed" if any(row["status"] == "failed" for row in rows) else "blocked"
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=False)
    source_revision = head.stdout.strip() if head.returncode == 0 and re.fullmatch(r"[0-9a-f]{40}", head.stdout.strip()) else None
    scope = "diagnostic" if not healthy or (selected and any(row.get("reason") == "not-selected" for row in rows)) else "complete"
    manifest = {"schema_version": 1, "change_id": change, "run_id": run_id, "created_at": stamp(), "source_revision": source_revision, "environment": plan.get("environment", "unspecified"), "scope": scope, "status": verdict, "preflight": preflight_results, "checks": rows}
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
    return {"status": verdict, "scope": scope, "run_id": run_id, "path": str(dest.relative_to(root)), "checks": len(rows)}


def readiness(root: Path, change: str) -> dict:
    change_dir = change_path(root, change)
    plan = read_plan(change_dir)
    manifest = latest_manifest(change_dir)
    if not manifest:
        return {"status": "blocked", "reason": "manifest-missing"}
    rows = {row["id"]: row for row in manifest.get("checks", [])}
    stale = [check["id"] for check in plan["checks"] if not sample_ready(check) or rows.get(check["id"], {}).get("status") != "passed" or rows[check["id"]].get("fingerprint") != fingerprint(root, check) or effects(root, check) or visual_coverage_problems(check) or not artifacts_match(root, rows[check["id"]])]
    # A newer substantive diagnostic failure revokes an older complete pass;
    # missing/unselected rows in a partial run do not affect readiness.
    observed: set[str] = set()
    planned = {check["id"]: check for check in plan["checks"]}
    for newer in acceptance_manifests(change_dir):
        if newer.get("run_id") == manifest.get("run_id"):
            break
        for row in newer.get("checks", []):
            name = row.get("id")
            check = planned.get(name)
            if not check or name in observed or row.get("reason") == "not-selected" or row.get("fingerprint") != fingerprint(root, check):
                continue
            observed.add(name)
            if row.get("status") == "failed" and name not in stale:
                stale.append(name)
    return {"status": "ready" if not stale and manifest.get("status") == "passed" else "blocked", "stale": stale, "run_id": manifest.get("run_id")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--change", required=True)
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--db", type=Path, help="Authorized local product SQLite path; read only")
    parser.add_argument("--db-alias", action="append", default=[], metavar="NAME=PATH",
                        help="Additional authorized read-only product SQLite for checks declaring product_db")
    parser.add_argument("--only", action="append", help="Run selected AC; reuse valid others")
    parser.add_argument("--readiness", action="store_true", help="Check current evidence without executing")
    args = parser.parse_args()
    try:
        aliases = {}
        for item in args.db_alias:
            name, sep, path = item.partition("=")
            if not sep or not re.fullmatch(r"[a-z][a-z0-9_-]*", name) or not path:
                raise ValueError("invalid --db-alias; expected NAME=PATH")
            aliases[name] = Path(path)
        result = readiness(args.root, args.change) if args.readiness else run_acceptance(args.root, args.change, args.db, set(args.only) if args.only else None, aliases)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = {"status": "blocked", "reason": str(exc)}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] in {"passed", "ready"} else 1


if __name__ == "__main__":
    sys.exit(main())
