"""Shared, read-only Issue acceptance admission; no repository code execution."""
from pathlib import Path
import re
import yaml
from app.governance.acceptance_evidence import read_plan, readiness, latest_manifest, readiness_reason, archived_readiness


def protected_rule_integrity(root: Path, change: str) -> dict:
    """Keep archived rule obligations unless the successor only adds scenarios.

    The historical exact exception remains valid, but no old confirmation or
    newly invented text proof can turn an arbitrary rewrite into an append.
    """
    from types import SimpleNamespace
    from .compatible_successor import append_only
    from .rule_change import conflicts, supported

    if not (root / 'openspec/changes' / change / 'specs').is_dir():
        return {'ready': True}

    rejected = []
    for row in conflicts(SimpleNamespace(root=root), change):
        allowed = False
        if row['operation'] == 'MODIFIED':
            try:
                allowed = bool(append_only(row['before'], row['after']))
            except ValueError:
                allowed = supported(row['before'], row['after'])
        if not allowed:
            rejected.append({'capability': row['key'][0], 'requirement': row['key'][1],
                             'protected_changes': row['protected_changes']})
    return ({'ready': False, 'reason': '已归档规则的原约束被删除或改写',
             'recovery_reason': 'archive_requirement_conflict', 'diagnostics': rejected}
            if rejected else {'ready': True})


def metadata(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("frontmatter_missing")
    data = yaml.safe_load(text.split("---", 2)[1])
    if not isinstance(data, dict):
        raise ValueError("frontmatter_invalid")
    return data


def issue_identity(trace):
    values = [trace[key] for key in ("requirement", "requirement_id", "req_id",
              "source_requirement", "bug", "bug_id", "source_bug", "related_bug")
              if trace.get(key)]
    if any(not isinstance(value, str) for value in values) or len(set(values)) > 1:
        raise ValueError("issue_identity_ambiguous")
    return values[0] if values else None


def linked_changes(entry, trace):
    """Normalize supported registry/trace associations without losing aliases."""
    changes = set()
    for source in (entry, trace):
        for key in ("related_change", "related_changes", "openspec_changes"):
            value = source.get(key) or []
            for item in value if isinstance(value, list) else [value]:
                cid = item.get("change_id") if isinstance(item, dict) else item
                if isinstance(cid, str) and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", cid):
                    changes.add(cid)
    return sorted(changes)


def _issue_acceptance(root: Path, issue_dir: Path, changes=(), *, source_root: Path | None = None):
    """Structured evidence takes precedence over its Markdown projection."""
    result = dict(ready=False, done=0, total=0, reason="验收来源待核实", source="manual")
    try:
        doc = issue_dir / "acceptance.md"
        meta = metadata(doc)
        text = doc.read_text(encoding="utf-8")
        ids = set(re.findall(r"^(?:#{1,6}\s+|[-*]\s+\[[ xX]\]\s+)(AC-[A-Za-z0-9-]+)\b", text, re.M))
        checked = {key for mark, key in re.findall(r"^[-*]\s+\[([xX ])\]\s+(AC-[A-Za-z0-9-]+)\b", text, re.M) if mark != " "}
        plans = []
        for cid in changes:
            active = root / "openspec/changes" / cid
            from app.governance.archive_recovery import archive_paths
            folders = ([active] if active.is_dir() else []) + archive_paths(root, cid)
            if len(folders) != 1:
                raise ValueError("change_identity_ambiguous")
            if (folders[0] / "acceptance-plan.json").is_file():
                plans.append((cid, folders[0]))
        if plans:
            passed, planned = set(), set()
            all_ready = True
            failures = []
            for cid, folder in plans:
                plan = read_plan(folder)
                trace = metadata(folder / "trace.md")
                identity = issue_identity(trace)
                if identity != issue_dir.name or plan.get("issue_id", identity) != identity:
                    raise ValueError("acceptance_identity_mismatch")
                checks = {c["id"] for c in plan["checks"]}
                evidence = (readiness(root, cid, source_root=source_root) if folder.parent.name == "changes"
                            else archived_readiness(root, folder))
                manifest = latest_manifest(folder) or {}
                stale = set(evidence.get("stale", checks))
                passed.update(r["id"] for r in manifest.get("checks", []) if r.get("status") == "passed" and r["id"] not in stale)
                planned.update(checks)
                all_ready &= evidence["status"] == "ready"
                if evidence["status"] != "ready":
                    failures.append(evidence)
            missing = ids - planned
            total = len(planned | ids)
            done = len((passed & planned) | (checked & missing))
            manual = meta.get("manual_acceptance_status")
            ready = all_ready and missing <= checked and meta.get("acceptance_status") in {"passed", "accepted", "approved", "done", "complete", "completed"} and manual not in {"pending", "failed", "required"}
            blocked = next((item for item in failures if item.get('recovery_reason')), {})
            return dict(ready=ready, done=done, total=total, source="evidence",
                        recovery_reason=blocked.get('recovery_reason'), diagnostics=blocked.get('diagnostics', []),
                        reason=None if ready else (readiness_reason(blocked) if blocked else
                            "人工验收尚未签认" if manual in {"pending", "failed", "required"} else "验收证据缺失、过期或未全部通过"))
        ready = meta.get("manual_acceptance_status") not in {"pending", "failed", "required"} and bool(ids) and ids <= checked and meta.get("acceptance_status") in {"passed", "accepted", "approved", "done", "complete", "completed"}
        return dict(ready=ready, done=len(checked & ids), total=len(ids), source="manual",
                    reason=None if ready else "验收未完成，请查看验收项与交付证据")
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError):
        return result


def issue_acceptance(root: Path, issue_dir: Path, changes=(), *, source_root: Path | None = None):
    result = _issue_acceptance(root, issue_dir, changes, source_root=source_root)
    if result['ready']:
        from app.governance.archive_recovery import recovery_admission
        for cid in changes:
            recovery = recovery_admission(root, cid, source_root=source_root)
            if not recovery['ready']:
                return {**result, 'ready': False, 'reason': recovery['reason'],
                        'recovery_reason': recovery['recovery_reason']}
    return result


def change_acceptance(root: Path, change: str, *, source_root: Path | None = None):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,100}", change):
        return dict(ready=False, reason="change_identity_invalid")
    active = root / "openspec/changes" / change
    archived = [p for base in ("openspec/archive", "openspec/changes/archive")
                for p in (root / base).glob(f"????-??-??-{change}") if p.is_dir()]
    if len(archived) + int(active.is_dir()) != 1:
        return dict(ready=False, reason="change_identity_ambiguous")
    folder = active if active.is_dir() else archived[0]
    def finish(result):
        if folder != active or not result['ready']:
            return result
        protected = protected_rule_integrity(root, change)
        return {**result, **protected} if not protected['ready'] else result
    try:
        trace = metadata(folder / "trace.md")
        oid = issue_identity(trace)
        if not oid:
            if (folder / "acceptance-plan.json").is_file():
                try:
                    evidence = (readiness(root, change, source_root=source_root) if folder == active
                                else archived_readiness(root, folder))
                except (OSError, ValueError, KeyError, TypeError):
                    evidence = {"status": "blocked"}
                if evidence['status'] != 'ready':
                    return dict(ready=False, reason=readiness_reason(evidence))
                from app.governance.archive_recovery import recovery_admission
                recovery = recovery_admission(root, change, source_root=source_root)
                return finish({**recovery, "reason": recovery.get("reason")})
            from app.governance.archive_recovery import recovery_admission
            recovery = recovery_admission(root, change, source_root=source_root)
            return finish({**recovery, 'reason': recovery.get('reason', 'standalone_change')})
        if not isinstance(oid, str) or not re.fullmatch(r"(REQ|BUG)-\d{4}-[a-z0-9-]+", oid):
            raise ValueError("issue_identity_invalid")
        domain = "requirements" if oid.startswith("REQ-") else "bugs"
        dirs = [root / "issues" / domain / stage / oid for stage in ("plan", "review", "archive")]
        dirs = [p for p in dirs if (p / "acceptance.md").is_file()]
        if len(dirs) != 1:
            return dict(ready=False, reason="issue_acceptance_missing_or_ambiguous")
        return finish(issue_acceptance(root, dirs[0], [change], source_root=source_root))
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError):
        return dict(ready=False, reason="acceptance_source_invalid")


def noop_archive_retry_ready(root, oid, snapshot, *, source_root=None):
    """Current readiness after a trusted terminal attempt proved zero writes."""
    from app.governance.execution_validation import validate_external
    from app.governance.change_index import ChangeIndex
    from app.governance.candidates import frontmatter
    try:
        if not validate_external(snapshot.files, oid, 'acceptance'):
            return False
        if oid.startswith(('REQ-', 'BUG-')):
            domain = 'requirements' if oid.startswith('REQ-') else 'bugs'
            registry = yaml.safe_load(snapshot.files[f'issues/{domain}/_registry.yaml'])
            entries = [e for e in registry['entries'] if e['id'] == oid]
            if len(entries) != 1:
                return False
            trace, _ = frontmatter(snapshot.files[entries[0]['path'].rstrip('/') + '/trace.md'])
            links = linked_changes(entries[0], trace)
        else:
            links = [oid]
        index = ChangeIndex(root)
        return bool(links) and all(change_acceptance(root, cid, source_root=source_root)['ready']
            and cid in index.records and not index.acceptance_source_reason(index.records[cid], source_root=source_root) for cid in links)
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError):
        return False
