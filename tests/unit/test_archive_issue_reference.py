"""Bound historical references; active documents and ambiguous Issues stay blocked."""
from pathlib import Path
import pytest
from app.governance import archive_issue_reference as r


@pytest.fixture
def sample(tmp_path, monkeypatch):
    doc = tmp_path / 'openspec/archive/2026-10-30-fix-sample/trace.md'
    doc.parent.mkdir(parents=True)
    doc.write_text('history')
    old = tmp_path / 'issues/requirements/review/REQ-0001-sample'
    dest = tmp_path / 'issues/requirements/archive/REQ-0001-sample'
    old.mkdir(parents=True)
    (old / 'trace.md').write_text('---\nstatus: done\nlifecycle_stage: review\nopenspec_changes:\n- change_id: fix-sample\n---\n')
    (old / 'prototype').mkdir()
    (old / 'prototype/index.html').write_text('prototype')
    monkeypatch.setattr(r, 'recovery_admission', lambda *_: {'ready': True, 'mode': 'archived'})
    return tmp_path, doc, old, dest


def test_plan_then_archive_without_changing_source_document(sample):
    root, doc, old, dest = sample
    original = old / 'prototype/index.html'
    before = doc.read_bytes()
    assert r.resolve(root, doc, original, source=old, target=dest) == dest / 'prototype/index.html'
    dest.parent.mkdir(parents=True)
    old.rename(dest)
    trace = dest / 'trace.md'
    trace.write_text(trace.read_text().replace('lifecycle_stage: review', 'lifecycle_stage: archive'))
    assert r.resolve(root, doc, original) == dest / 'prototype/index.html'
    assert doc.read_bytes() == before
    (dest / 'prototype/index.html').unlink()
    assert r.resolve(root, doc, original) is None


@pytest.mark.parametrize('cause', ['active-document', 'ambiguous', 'not-done', 'unlinked', 'sibling-active', 'proof-failed', 'symlink'])
def test_resolution_fails_closed(sample, monkeypatch, cause):
    root, doc, old, dest = sample
    if cause == 'active-document': doc = root / 'openspec/changes/fix-sample/trace.md'
    if cause == 'ambiguous': dest.mkdir(parents=True)
    if cause in {'not-done', 'unlinked', 'sibling-active'}:
        trace = old / 'trace.md'
        text = trace.read_text()
        if cause == 'not-done': text = text.replace('done', 'in_sprint')
        if cause == 'unlinked': text = text.replace('fix-sample', 'another')
        if cause == 'sibling-active': text = text.replace('- change_id: fix-sample', '- change_id: fix-sample\n- change_id: pending-change')
        trace.write_text(text)
    if cause == 'proof-failed': monkeypatch.setattr(r, 'recovery_admission', lambda *_: {'ready': False})
    if cause == 'symlink':
        resource = old / 'prototype/index.html'
        resource.unlink()
        resource.symlink_to(doc)
    assert r.resolve(root, doc, old / 'prototype/index.html', source=old, target=dest) is None


def test_prototype_bare_paths_stop_at_chinese_prose():
    from scripts.workflow_sync.prototype_references import references
    refs = references(Path('acceptance.md'), '对照prototype/web/context.md完成复核；prototype/web为结构原型\n- docs/knowledge-base/best-practices/prototype-driven-ui-gate.md')
    assert [r.value for r in refs] == ['prototype/web/context.md', 'prototype/web']
    refs = references(Path('acceptance.md'), '[原型](prototype/web/中文原型.html)')
    assert [r.value for r in refs] == ['prototype/web/中文原型.html']
