"""Shared read-only acceptance evidence checks for product and CLI.

Never executes commands declared by a repository plan.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
from pathlib import Path
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
AC_ID = re.compile(r"^AC-[A-Za-z0-9-]+$")

def within(base: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or not path.parts or not relative.strip():
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
    if "orchestration_version" in plan and plan["orchestration_version"] != 1:
        raise ValueError("unsupported orchestration version")
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
            if (check.get("turn_id") is not None and not ID.fullmatch(str(check["turn_id"]))) or not isinstance(check.get("command_contains"), str) or not check["command_contains"]:
                raise ValueError(f"{name}: turn_id and command_contains required")
            proof = check.get("execution_proof", "command")
            if proof not in {"command", "trusted_archive_v1"}:
                raise ValueError(f"{name}: invalid execution proof")
            if proof == "trusted_archive_v1":
                object_id = check.get("trusted_archive_object_id")
                if (not isinstance(object_id, str) or not re.fullmatch(r"sprint-\d{3}", object_id)
                        or check["command_contains"] != f"/sprint-archive {object_id}"
                        or check.get("expected_exit_code", 0) != 0
                        or check.get("require_acceptance_gate_blocked", False)):
                    raise ValueError(f"{name}: invalid trusted archive proof")
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
        produced = check.get("produces_artifacts", [])
        if not isinstance(produced, list) or any(p not in artifacts for p in produced) or (produced and check["kind"] != "command"):
            raise ValueError("produces_artifacts must be declared command artifacts")
        for artifact in artifacts:
            path = within(change_dir.parents[2], artifact)
            relative = path.relative_to(change_dir.parents[2].resolve())
            if relative.parts[0] in {"data", "logs", "tmp"} or path.name.startswith(".env"):
                raise ValueError(f"{name}: raw or temporary artifacts cannot be retained")
    # Additive v1 fields: old plans retain their original fingerprints.
    for check in checks:
        dependencies = check.get("depends_on", [])
        if not isinstance(dependencies, list) or any(x not in seen or x == check["id"] for x in dependencies):
            raise ValueError("unknown/self dependency")
        if not isinstance(check.get("deduplicate", False), bool):
            raise ValueError("deduplicate must be boolean")
        sections = check.get("input_sections", {})
        if not isinstance(sections, dict) or any(k not in check["inputs"] or not isinstance(v, list) or not v or any(not isinstance(h, str) or not h.startswith("#") for h in v) for k, v in sections.items()):
            raise ValueError("input_sections requires input paths and exact Markdown headings")
        collection = check.get("collection", {})
        if not isinstance(collection, dict) or collection.get("state", "pending") not in {"pending", "collecting", "collected", "blocked"}:
            raise ValueError("invalid collection state")
        if plan.get("orchestration_version") == 1 and plan.get("preflight"):
            check["_plan_preflight"] = plan["preflight"]
        if plan.get("environment_contract"):
            check["_environment_contract"] = plan["environment_contract"]
        if plan.get("orchestration_version") == 1 and "environment" in plan:
            check["_environment"] = plan["environment"]
    contract = plan.get("environment_contract")
    if contract is not None:
        required_fields = ("deployment", "workspace_mode", "sample_scope", "authorization_ref", "cleanup_after", "login_strategy")
        if not isinstance(contract, dict) or any(not isinstance(contract.get(k), str) or not contract[k].strip() for k in required_fields):
            raise ValueError("environment_contract missing deployment/workspace/sample/authorization/cleanup/login")
        if contract["workspace_mode"] not in {"source", "isolated", "readonly"} or contract["cleanup_after"] != "evidence-and-recovery-verified":
            raise ValueError("invalid workspace mode or premature cleanup policy")
        if type(contract.get("retry_limit")) is not int or not 0 <= contract["retry_limit"] <= 2:
            raise ValueError("environment retry_limit must be 0..2; not automatic write permission")
        browser = contract.get("browser_capabilities", [])
        if not isinstance(browser, list) or any(x not in {"screenshot", "viewport", "computed_style", "network", "console"} for x in browser):
            raise ValueError("invalid browser capabilities")
    by_id = {c["id"]: c for c in checks}
    for check in ordered_checks(checks):
        if check.get("depends_on"):
            check["_dependencies"] = [by_id[d] for d in check["depends_on"]]
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
        scope = plan.get("issue_acceptance_scope", "full")
        if scope not in {"full", "partial"}:
            raise ValueError("invalid Issue acceptance scope")
        if scope == "partial":
            mapping = plan.get("issue_ac_mapping")
            scope_text = plan.get("scope_description")
            local = change_dir / "acceptance.md"
            local_ac = set(re.findall(r"^- \[[ xX]\] (AC-[A-Za-z0-9-]+)\b", local.read_text(encoding="utf-8"), re.MULTILINE)) if local.is_file() else set()
            if (local_ac != seen or not isinstance(scope_text, str) or not scope_text.strip()
                    or not isinstance(mapping, dict) or set(mapping) != seen
                    or any(not isinstance(ids, list) or not ids
                           or any(not isinstance(ac, str) or ac not in issue_ac for ac in ids)
                           for ids in mapping.values())):
                raise ValueError("partial acceptance requires local AC coverage and explicit Issue mapping")
        elif issue_ac != seen:
            raise ValueError("acceptance plan AC set differs from linked Issue")
    elif plan.get("issue_acceptance_scope") == "partial":
        raise ValueError("partial acceptance requires a linked Issue")
    return plan

def ordered_checks(checks: list[dict]) -> list[dict]:
    remaining = list(checks)
    ordered = []
    completed = set()
    while remaining:
        ready = [c for c in remaining if set(c.get("depends_on", [])) <= completed]
        if not ready:
            raise ValueError("cyclic acceptance dependencies")
        for check in ready:
            ordered.append(check)
            completed.add(check["id"])
            remaining.remove(check)
    return ordered

SOURCE_INPUT_ROOTS = {"src", "scripts", "tests"}
SOURCE_INPUT_FILES = {"AGENTS.md", ".gitignore"}


def input_path(root: Path, relative: str, *, source_root: Path | None = None) -> Path:
    # Explicit source inputs only; never fall back for missing governance facts.
    # Select the authorized root before resolving. An unused projection path
    # supplies no evidence about the source path that will actually be read.
    parts = Path(relative).parts
    if source_root is not None and (
        (parts and parts[0] in SOURCE_INPUT_ROOTS) or relative in SOURCE_INPUT_FILES
    ):
        return within(source_root, relative)
    return within(root, relative)


def input_bytes(root: Path, check: dict, relative: str, *, source_root: Path | None = None) -> bytes:
    path = input_path(root, relative, source_root=source_root)
    headings = check.get("input_sections", {}).get(relative)
    if not headings:
        if path.is_dir():
            return directory_input(path)
        return fingerprint_input(path, relative) if path.is_file() else b"<missing>"
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    selected = []
    for heading in headings:
        matches = [i for i, line in enumerate(lines) if line.rstrip() == heading]
        if len(matches) != 1:
            raise ValueError("input section missing or ambiguous")
        start = matches[0]
        level = len(heading) - len(heading.lstrip("#"))
        end = next((i for i in range(start + 1, len(lines))
                    if re.match(r"^#{1," + str(level) + r"} ", lines[i])), len(lines))
        selected.append("".join(lines[start:end]))
    return "\n".join(selected).encode()

def directory_input(path: Path) -> bytes:
    """Content-address a directory, including names, empty folders and deletions.

    Never follow links or read special files. Keep legacy file fingerprints intact.
    """
    entries = []
    def walk_error(error):
        raise ValueError("unreadable acceptance input directory") from error
    for parent, directories, files in os.walk(path, followlinks=False, onerror=walk_error):
        for name in sorted(directories + files):
            item = Path(parent) / name
            relative = item.relative_to(path).as_posix()
            if item.is_symlink():
                raise ValueError("acceptance input directory contains symlink")
            if item.is_dir():
                entries.append([relative, "directory"])
            elif item.is_file():
                entries.append([relative, "file", hashlib.sha256(item.read_bytes()).hexdigest()])
            else:
                raise ValueError("acceptance input directory contains special file")
    return b"directory-v1\0" + json.dumps(sorted(entries), ensure_ascii=False, separators=(",", ":")).encode()


def fingerprint(root: Path, check: dict, *, source_root: Path | None = None) -> str:
    digest = hashlib.sha256(json.dumps(check, ensure_ascii=False, sort_keys=True).encode())
    for relative in check["inputs"]:
        digest.update(relative.encode())
        digest.update(input_bytes(root, check, relative, source_root=source_root))
    for dependency in check.get("_dependencies", []):
        digest.update(fingerprint(root, dependency, source_root=source_root).encode())
    return digest.hexdigest()

def sample_ready(check: dict) -> bool:
    if check.get("collection", {}).get("state", "collected") != "collected":
        return False
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

def artifact_path(root: Path, relative: str) -> Path:
    """Resolve a moved Change's evidence without changing its recorded identity/hash."""
    path = within(root, relative)
    parts = Path(relative).parts
    if len(parts) < 4 or parts[:2] != ("openspec", "changes"):
        return path
    from app.governance.archive_recovery import IDENTITY, archive_paths, completed_archive
    change = parts[2]
    if not IDENTITY.fullmatch(change):
        raise ValueError("invalid evidence Change identity")
    active = root / "openspec/changes" / change
    if active.exists():
        return path
    matches = archive_paths(root, change)
    if len(matches) != 1 or matches[0].is_symlink() or not completed_archive(matches[0], change):
        return path
    candidate = matches[0].joinpath(*parts[3:])
    # Reject links even when they happen to resolve inside this repository.
    for part in (candidate, *candidate.parents):
        if part == root:
            break
        if part.is_symlink():
            raise ValueError("unsafe archived evidence link")
    return within(matches[0], str(Path(*parts[3:])))


def artifacts_match(root: Path, row: dict, *, archive_dir: Path | None = None) -> bool:
    for item in row.get("artifacts", []):
        path = artifact_path(root, item["path"])
        if archive_dir:
            parts = Path(item["path"]).parts
            if len(parts) >= 4 and parts[:3] == ("openspec", "changes", archive_dir.name[11:]):
                path = within(archive_dir, str(Path(*parts[3:])))
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            return False
    return True

def acceptance_manifests(change_dir: Path) -> list[dict]:
    base = change_dir / "evidence" / "acceptance"
    manifests = []
    for path in sorted([*base.glob("*/manifest.json"), *base.glob("checkpoints/*/manifest.json")], key=lambda item: item.stat().st_mtime_ns, reverse=True):
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

def archived_readiness(root: Path, folder: Path) -> dict:
    """Read retained completion evidence after migration, never fall back to checkboxes."""
    from app.governance.archive_recovery import recovery_admission, tree_hash
    try:
        before = tree_hash(folder)
        plan = read_plan(folder)
        recovery = recovery_admission(root, plan["change_id"])
        manifest = latest_manifest(folder)
        if not manifest:
            raise ValueError("archive evidence incomplete")
        rows = manifest.get("checks", [])
        ids = [row.get("id") for row in rows]
        expected = {check["id"] for check in plan["checks"]}
        if len(ids) != len(set(ids)) or set(ids) != expected:
            raise ValueError("archive evidence coverage mismatch")
        checks = {check["id"]: check for check in plan["checks"]}
        stale = [row["id"] for row in rows if row.get("status") != "passed"
                 or {item["path"] for item in row.get("artifacts", [])} != set(checks[row["id"]].get("artifacts", []))
                 or not artifacts_match(root, row, archive_dir=folder)]
        if tree_hash(folder) != before:
            return {"status": "blocked", "reason": "archive-evidence-changed", "stale": list(expected)}
        evidence_ready = not stale and manifest.get("status") == "passed"
        return {"status": "ready" if evidence_ready and recovery['ready'] and recovery.get('mode') == 'archived' else "blocked",
                "evidence_status": "ready" if evidence_ready else "blocked", "stale": stale,
                "recovery_status": "ready" if recovery['ready'] else "blocked",
                "recovery_reason": recovery.get('recovery_reason'),
                "reason": recovery.get('reason') if not recovery['ready'] else (None if evidence_ready else 'archived-evidence-invalid'),
                "diagnostics": recovery.get('diagnostics', []), "run_id": manifest["run_id"]}
    except (OSError, ValueError, KeyError, TypeError):
        return {"status": "blocked", "reason": "archived-evidence-invalid"}


def readiness(root: Path, change: str, *, source_root: Path | None = None) -> dict:
    change_dir = change_path(root, change)
    plan = read_plan(change_dir)
    manifest = latest_manifest(change_dir)
    if not manifest:
        return {"status": "blocked", "reason": "manifest-missing"}
    rows = {row["id"]: row for row in manifest.get("checks", [])}
    stale, diagnostics, current_fingerprints = [], [], {}
    for check in plan["checks"]:
        name = check["id"]
        row = rows.get(name, {})
        code, paths = None, []
        try:
            current_fingerprints[name] = fingerprint(root, check, source_root=source_root)
            missing = [p for p in check["inputs"]
                       if not input_path(root, p, source_root=source_root).exists()]
            if missing:
                code, paths = "input-missing", missing
            elif not sample_ready(check):
                code = "sample-pending"
            elif row.get("status") != "passed":
                code = "check-not-passed"
            elif row.get("fingerprint") != current_fingerprints.get(name):
                code = "input-changed"
            elif effects(root, check):
                code = "effect-mismatch"
            elif visual_coverage_problems(check) or not artifacts_match(root, row):
                code = "evidence-invalid"
        except (OSError, ValueError, KeyError, TypeError):
            # Do not send raw filesystem errors or plan contents to the card.
            code = "input-unreadable"
        if code:
            stale.append(name)
            diagnostics.append({"ac_id": name, "code": code,
                                "paths": [p for p in paths if safe_diagnostic_path(p)][:3]})
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
            if not check or name in observed or row.get("reason") == "not-selected" or row.get("fingerprint") != current_fingerprints.get(name):
                continue
            observed.add(name)
            if row.get("status") == "failed" and name not in stale:
                stale.append(name)
                diagnostics.append({"ac_id": name, "code": "newer-check-failed", "paths": []})
    return {"status": "ready" if not stale and manifest.get("status") == "passed" else "blocked", "stale": stale, "run_id": manifest.get("run_id"), "diagnostics": diagnostics}


def safe_diagnostic_path(relative: str) -> bool:
    """Only bounded repository-relative identifiers may reach user-visible text."""
    return (isinstance(relative, str) and len(relative) <= 180
            and re.fullmatch(r"[A-Za-z0-9_./-]+", relative) is not None
            and not Path(relative).is_absolute() and ".." not in Path(relative).parts
            and all(not part.startswith(".env") and part not in {".git", ".ssh", ".aws"}
                    for part in Path(relative).parts))


def readiness_reason(evidence: dict) -> str | None:
    if evidence.get("status") == "ready":
        return None
    if evidence.get("recovery_reason"):
        details = []
        for item in evidence.get("diagnostics", [])[:3]:
            values = [item.get(key, '') for key in ('change_id', 'capability', 'requirement')]
            if all(isinstance(value, str) and re.fullmatch(r'[\w \u4e00-\u9fff:：()（）-]{1,120}', value) for value in values):
                details.append('/'.join(values))
        reason = evidence.get("reason") or "归档恢复核验受阻"
        return reason + ("：" + "、".join(details) if details else "")
    if evidence.get("reason") == "manifest-missing":
        return "尚无完整验收记录，请执行自动验收并查看验收报告"
    labels = {
        "input-missing": "验收输入缺失",
        "input-changed": "验收输入或计划已变化，请重新验收",
        "input-unreadable": "验收输入不可读取或路径不安全，请核查绑定与权限",
        "sample-pending": "验收样本尚未采集完成",
        "check-not-passed": "验收项尚未通过",
        "effect-mismatch": "验收预期效果不再成立",
        "evidence-invalid": "验收附件或视觉证据无效",
        "newer-check-failed": "较新验收轮次失败",
    }
    details = []
    for diagnostic in evidence.get("diagnostics", [])[:3]:
        ac = diagnostic.get("ac_id", "")
        if not isinstance(ac, str) or not AC_ID.fullmatch(ac) or len(ac) > 64:
            continue
        paths = [p for p in diagnostic.get("paths", []) if safe_diagnostic_path(p)][:3]
        text = f"{ac}：{labels.get(diagnostic.get('code'), '验收原因待核查')}"
        details.append(text + ("（" + "、".join(paths) + "）" if paths else ""))
    if not details:
        details = ["验收未就绪，具体原因待核查"]
    return "；".join(details) + "；请查看 Change 验收报告"
