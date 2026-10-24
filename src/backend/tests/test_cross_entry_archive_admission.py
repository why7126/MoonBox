"""Synthetic REQ/BUG cross-entry lifecycle; never a real model-run claim."""
import json
import hashlib
import pytest
import yaml
from sqlalchemy import select, update
from app.chat.schema import governance_applications as applications, governance_candidates as candidates
from app.governance import store
from app.governance.archive_admission import change_acceptance
from app.governance.acceptance_evidence import fingerprint
from app.governance.execution_guard import acquire, terminal, read
from app.governance.execution_context import reconcile_external
from app.governance.snapshot import digest, Snapshot
from app.governance.candidates import frontmatter
from test_chat import chat
from test_governance_writer import writing, queue
from test_governance_review import review_files
from test_governance_candidates import front


@pytest.mark.parametrize("link_style", ["objects", "strings", "related_change", "related_changes"])
@pytest.mark.parametrize("bug", [False, True])
@pytest.mark.parametrize("failure", [None, "stale", "review", "rules", "running", "manual", "covered_scope", "uncovered_scope", "covered_review", "rejected_review"])
def test_review_cli_delivery_product_admission(writing, chat, monkeypatch, bug, failure, link_style):
    factory, project, _, _, permit = writing
    before, reviewed, oid, original_base = review_files(bug)
    action = "bug-review" if bug else "req-review"
    aid = queue((factory, project, before, reviewed, permit),
                candidate_action=action, object_id=oid, base_path=original_base)
    base = original_base.replace("/plan/", "/review/")
    current = dict(reviewed)
    cid = "cross-entry-delivery"
    domain = "bugs" if bug else "requirements"
    for name in ("trace.md", "bug.md" if bug else "requirement.md"):
        meta, body = frontmatter(current[f"{base}/{name}"])
        meta.update(status="in_sprint", iteration="sprint-001")
        if name == "trace.md":
            meta["openspec_changes"] = [{"change_id": cid, "status": "applied"}] if link_style == "objects" else [cid] if link_style == "strings" else []
            if link_style == "related_change":
                meta["related_change"] = cid
            if link_style == "related_changes":
                meta["related_changes"] = [cid]
        current[f"{base}/{name}"] = front(meta, body)
    registry = yaml.safe_load(current[f"issues/{domain}/_registry.yaml"])
    registry["entries"][0]["status"] = "in_sprint"
    current[f"issues/{domain}/_registry.yaml"] = yaml.safe_dump(registry).encode()
    current["iterations/change/sprint-001/sprint.yaml"] = yaml.safe_dump({
        "sprint_id": "sprint-001", domain: [oid], "changes": [cid]}).encode()
    change = f"openspec/changes/{cid}"
    current[f"{change}/trace.md"] = front({
        "status": "applied", "bug_id" if bug else "req_id": oid,
        "execution": {"completed_at": "2026-10-20 15:00:00"}})
    current[f"{change}/tasks.md"] = b"# Tasks\n- [x] delivered\n"
    if failure is not None:
        current[f"{change}/verification.md"] = b"# Synthetic verification\nFixture evidence for admission tests.\n"
    for name in ("proposal.md", "design.md"):
        current[f"{change}/{name}"] = b"# Delivery\n"
    # Heading-based unchecked Markdown is a projection, not a second auto gate.
    current[f"{base}/acceptance.md"] = front(
        {"acceptance_status": "passed", **({"manual_acceptance_status": "pending"} if failure == "manual" else {})},
        "\n### AC-001\n- [ ] verified by structured evidence\n")
    if failure in ("covered_scope", "uncovered_scope"):
        primary = f"{base}/bug.md" if bug else f"{base}/requirement.md"
        current[primary] += b"\nVerified new delivery scope\n"
    for path in project.root.rglob("*"):
        if path.is_file():
            path.unlink()
    for name, body in current.items():
        path = project.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
    if failure in ("covered_review", "rejected_review"):
        meta, body = frontmatter(current[f"{base}/review.md"])
        meta['result'] = 'rejected' if failure == 'rejected_review' else 'approved'
        current[f"{base}/review.md"] = front(meta, body + "\nLater scope review\n")
        (project.root / base / 'review.md').write_bytes(current[f"{base}/review.md"])
    check = {"id": "AC-001", "kind": "command", "inputs": [f"{base}/requirement.md" if not bug else f"{base}/bug.md"],
             "argv": ["unused-read-only-check"]}
    if failure in ("covered_review", "rejected_review"):
        check["inputs"].append(f"{base}/review.md")
    if failure == "uncovered_scope":
        check["inputs"] = [f"{change}/tasks.md"]
    linked_artifact = "openspec/changes/other-delivery/verification.md"
    if failure is None:
        check["artifacts"] = [linked_artifact]
    folder = project.root / change
    (folder / "acceptance-plan.json").write_text(json.dumps({"schema_version": 1, "change_id": cid, "checks": [check]}))
    report = folder / "evidence/acceptance/run"
    report.mkdir(parents=True)
    (report / "manifest.json").write_text(json.dumps({"run_id": "run", "scope": "complete", "status": "passed",
        "checks": [{"id": "AC-001", "status": "passed", "fingerprint": fingerprint(project.root, check),
                    "artifacts": [{"path": linked_artifact, "sha256": hashlib.sha256(b"proof").hexdigest()}] if failure is None else []}]}))
    if failure == "stale":
        path = project.root / check["inputs"][0]
        path.write_bytes(path.read_bytes() + b"\nchanged scope")
    if failure == "review":
        current[f"{base}/review.md"] += b"\nchanged decision"
    if failure == "rules":
        current["rules/new-rule.md"] = b"new rule"
    if failure is None:
        # A retained legacy journal remains valid after a disjoint completed archive.
        from app.governance.archive_recovery import tree_hash, journal_path, delivery_input_hash
        delta = "## ADDED Requirements\n### Requirement: 归档事实\n系统 SHALL 核验规格。\n"
        own_delta = folder / 'specs/own-cap/spec.md'
        own_delta.parent.mkdir(parents=True); own_delta.write_text(delta)
        specs = project.root / 'openspec/specs'; specs.mkdir(parents=True, exist_ok=True)
        initial_hash = tree_hash(specs)
        own_record = {'schema_version': 4, 'input_projection': 1,
                      'delivery_input_hash': delivery_input_hash(folder),
                      'change_id': cid, 'archive_date': '2026-10-20',
                      'active_change_hash': tree_hash(folder), 'baseline_spec_hash': initial_hash,
                      'expected_spec_hash': 'e' * 64}
        jp = journal_path(project.root, cid); jp.parent.mkdir(parents=True, exist_ok=True)
        jp.write_text(json.dumps(own_record))
        archive = project.root / 'openspec/archive/2026-10-20-other-delivery'
        (archive / 'specs/other-cap').mkdir(parents=True)
        (archive / 'specs/other-cap/spec.md').write_text(delta)
        (archive / 'trace.md').write_text('---\nstatus: archived\n---\n')
        (archive / 'verification.md').write_text('proof')
        (specs / 'other-cap').mkdir(); (specs / 'other-cap/spec.md').write_text(delta)
        journal_path(project.root, 'other-delivery').write_text(json.dumps({
            'change_id': 'other-delivery', 'archive_date': '2026-10-20',
            'baseline_spec_hash': initial_hash, 'expected_spec_hash': tree_hash(specs)}))
        for path in [own_delta, archive / 'specs/other-cap/spec.md', archive / 'trace.md',
                     archive / 'verification.md', specs / 'other-cap/spec.md']:
            current[path.relative_to(project.root).as_posix()] = path.read_bytes()
    with factory() as db:
        if failure is None:
            from app.governance.preparation import _preflight_object_session
            prepared = _preflight_object_session(db, "alice", project, oid, "opsx-archive")
            assert prepared['id'] == oid
            from types import SimpleNamespace
            from app.chat.policy import _archive_ready
            assert _archive_ready(SimpleNamespace(scalar=lambda query: '/opsx-archive ' + oid),
                                  {'active_turn_id': 'test'}, prepared, registry['entries'][0])
        app = db.execute(select(applications).where(applications.c.id == aid)).mappings().one()
        candidate = db.execute(select(candidates).where(candidates.c.id == app["candidate_id"])).mappings().one()
        db.execute(update(applications).where(applications.c.id == aid).values(state="applied", phase="verified"))
        acquire(db, scope_key=project.key, object_id=oid, operation_id=candidate["turn_id"],
                conversation_id=candidate["conversation_id"], owner_id="alice", action=action,
                confirmed_stage="review-ready", baseline_revision=digest(before))
        if failure != "running":
            terminal(db, candidate["turn_id"], "completed")
        store.write(candidate["id"], "baseline", {"workspace_mode": "source", "files": {k:v.decode() for k,v in before.items()}})
        store.write(candidate["id"], "result", {"after": {k:reviewed[k].decode() if k in reviewed else None for k in set(before)|set(reviewed) if before.get(k) != reviewed.get(k)}})
        store.write(aid, "operation", {"workflow_sync": {"object_id": oid, "event": action.replace("-", "."), "source_hash": digest(reviewed)}})
        old_version = read(db, project.key, oid)["version"]
        reconcile_external(db, project, oid, "acceptance", Snapshot(current, digest(current)))
        guard = read(db, project.key, oid)
        accepted = failure in (None, "covered_scope", "covered_review")
        assert guard["state"] == ("validated" if accepted else "running" if failure == "running" else "needs_review")
        assert guard["operation_id"] == candidate["turn_id"]
        assert guard["version"] == old_version + accepted
        assert len(db.execute(select(applications)).all()) == 1
        if failure in (None, "stale", "manual"):
            verdict = change_acceptance(project.root, cid)
            assert verdict["ready"] == (failure is None)
            assert verdict["total"] == 1
            from app.services.requirement_center import _acceptance_readiness, using_governance_root
            with using_governance_root(project.root):
                pending, total, reason = _acceptance_readiness(project.root / base)
            assert total == 1
            assert (reason is None) == (failure is None)
            from app.governance.archive_admission import noop_archive_retry_ready
            assert noop_archive_retry_ready(project.root, oid, Snapshot(current, digest(current))) == (failure is None)

        if failure is None:
            db.execute(update(candidates).where(candidates.c.id == candidate['id']).values(state='applied'))
        db.commit()

    if failure is None:
        # Reacceptance output and hook narrative arrive AFTER journal creation.
        # Both actual HTTP send and CLI admission must survive that normal order.
        refreshed = folder / 'evidence/acceptance/refreshed'
        refreshed.mkdir(parents=True)
        fresh = json.loads((report / 'manifest.json').read_text())
        fresh['run_id'] = 'refreshed'
        (refreshed / 'manifest.json').write_text(json.dumps(fresh))
        with (folder / 'trace.md').open('a') as handle:
            handle.write('\n再次验收与收尾记录\n')
        assert change_acceptance(project.root, cid)['ready']
        # Exercise the actual turn endpoint, after a concurrent unrelated edit.
        from app.governance import preparation
        original = preparation._preflight_object_session
        calls = []
        def racing_preflight(*args):
            item = original(*args)
            calls.append(1)
            if len(calls) == 1:
                path = project.root / 'docs/unrelated.md'
                path.parent.mkdir(exist_ok=True)
                path.write_text('unrelated concurrent edit')
            return item
        monkeypatch.setattr(preparation, '_preflight_object_session', racing_preflight)
        monkeypatch.setattr('app.chat.isolated.allowed', lambda *args: True)
        monkeypatch.setattr('app.chat.settings.execution_limits', lambda: dict(user_concurrency=3, space_concurrency=3,
            user_monthly_tokens=10000, space_monthly_tokens=10000, user_storage_bytes=10000000,
            space_storage_bytes=10000000, turn_reserved_tokens=10, turn_reserved_bytes=1000000))
        client, _ = chat
        url = f"/api/v1/chat/conversations/{candidate['conversation_id']}/turns"
        payload = {'client_request_id': 'archive-race', 'prompt': '/opsx-archive ' + oid}
        # Actual send refuses an unproven spec edit before persisting a turn.
        unknown = project.root / 'openspec/specs/unproven.md'
        unknown.write_text('not backed by an archive')
        rejected = client.post(url, json={**payload, 'client_request_id': 'archive-unproven'})
        assert rejected.status_code == 409, rejected.text
        assert '归档规格基线变化' in rejected.text
        unknown.unlink()
        response = client.post(url, json=payload)
        assert response.status_code == 200, response.text
        assert response.json()['data']['status'] == 'queued'
        assert len(calls) == 3  # two baseline checks plus enqueue guard revalidation
        replay = client.post(url, json=payload)
        assert replay.status_code == 200, replay.text
        assert replay.json()['data']['id'] == response.json()['data']['id']


@pytest.mark.parametrize("alias", ["req_id", "requirement_id", "source_requirement", "requirement", "bug_id", "source_bug", "related_bug", "bug"])
def test_archive_executor_uses_same_issue_aliases(tmp_path, monkeypatch, alias):
    from app.chat.policy import _archive_ready
    from types import SimpleNamespace
    oid = "BUG-9097-test" if alias in {"bug_id", "source_bug", "related_bug", "bug"} else "REQ-9096-test"
    folder = tmp_path / "openspec/changes/test-archive"
    folder.mkdir(parents=True)
    (folder / "trace.md").write_text("---\n" + yaml.safe_dump({alias:oid,"status":"applied"}) + "---\n")
    db = SimpleNamespace(scalar=lambda query: "/opsx-archive " + oid)
    item = {"id":oid,"path":"issues/review/"+oid,"root":tmp_path}
    assert _archive_ready(db,{"active_turn_id":"turn"},item,{"related_change":"test-archive"})
    domain = "bugs" if oid.startswith("BUG") else "requirements"
    issue = tmp_path / "issues" / domain / "review" / oid
    issue.mkdir(parents=True)
    (issue / "acceptance.md").write_text("---\nacceptance_status: passed\n---\n- [x] AC-001 已验收\n")
    assert change_acceptance(tmp_path, "test-archive")["ready"]
    (folder / "trace.md").write_text("---\n" + yaml.safe_dump({alias:oid,"requirement_id":"REQ-0001-conflict","req_id":"REQ-0002-conflict","status":"applied"}) + "---\n")
    assert not _archive_ready(db,{"active_turn_id":"turn"},item,{"related_change":"test-archive"})
    assert not change_acceptance(tmp_path, "test-archive")["ready"]


@pytest.mark.parametrize("mutation", [None, "source", "tests", "governance", "deleted-governance", "missing-source"])
def test_governance_projection_reads_trusted_source_without_masking_drift(tmp_path, mutation):
    import shutil
    from app.governance.acceptance_evidence import readiness
    source = tmp_path / "source"
    projection = tmp_path / "projection"
    change = "split-root-archive"
    folder = source / "openspec/changes" / change
    folder.mkdir(parents=True)
    for relative, body in [("src/example.py", "implementation"), ("scripts/check.py", "check"), ("tests/unit/check.py", "test"),
                           ("issues/requirements/review/REQ-9096-test/requirement.md", "scope")]:
        path = source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
    check = {"id": "AC-001", "kind": "command", "argv": ["read-only-evidence"],
             "inputs": ["src/example.py", "scripts/check.py", "tests/unit/check.py",
                        "issues/requirements/review/REQ-9096-test/requirement.md"]}
    (folder / "acceptance-plan.json").write_text(json.dumps(
        {"schema_version": 1, "change_id": change, "checks": [check]}))
    evidence = folder / "evidence/acceptance/run"
    evidence.mkdir(parents=True)
    (evidence / "manifest.json").write_text(json.dumps(
        {"run_id": "run", "scope": "complete", "status": "passed",
         "checks": [{"id": "AC-001", "status": "passed", "fingerprint": fingerprint(source, check)}]}))
    for directory in ("openspec", "issues"):
        shutil.copytree(source / directory, projection / directory)
    assert readiness(projection, change)["status"] == "blocked"
    if mutation == "source":
        (source / "src/example.py").write_text("changed implementation")
    elif mutation == "tests":
        (source / "tests/unit/check.py").write_text("changed test")
    elif mutation == "governance":
        (projection / check["inputs"][-1]).write_text("changed scope")
    elif mutation == "deleted-governance":
        (projection / check["inputs"][-1]).unlink()
    elif mutation == "missing-source":
        (source / "scripts/check.py").unlink()
    assert readiness(projection, change, source_root=source)["status"] == (
        "ready" if mutation is None else "blocked")
