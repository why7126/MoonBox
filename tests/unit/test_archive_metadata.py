"""Synthetic restoration failures; production proof is exercised separately by CLI."""
import json
from pathlib import Path
import pytest
from app.governance import archive_metadata as m
from app.governance.archive_finalization import inspect_document


@pytest.fixture
def sample(tmp_path, monkeypatch):
    folder = tmp_path / 'openspec/archive/2026-10-30-fix-sample'
    folder.mkdir(parents=True)
    (folder / 'acceptance.md').write_text('---\nacceptance_status: not_started\n---\n设计映射\n')
    journal = m.journal_path(tmp_path, 'fix-sample')
    journal.parent.mkdir(parents=True)
    journal.write_text('{"retained":true}\n')
    monkeypatch.setattr(m, 'archived_readiness', lambda *_: {'status': 'ready', 'run_id': 'one'})
    monkeypatch.setattr(m, 'latest_manifest', lambda *_: {'run_id': 'one', 'status': 'passed'})
    return tmp_path, folder, journal


def test_readonly_idempotent_and_history_preserved(sample):
    root, folder, journal = sample
    before = {p: p.read_bytes() for p in (folder / 'acceptance.md', journal)}
    assert m.restore(root, 'fix-sample')['status'] == 'ready'
    assert not m.receipt_path(root, 'fix-sample').exists()
    assert m.restore(root, 'fix-sample', apply=True)['status'] == 'restored'
    receipt = m.receipt_path(root, 'fix-sample').read_bytes()
    assert not inspect_document(root, folder / 'acceptance.md', completed=True)
    assert m.restore(root, 'fix-sample', apply=True)['status'] == 'unchanged'
    assert m.receipt_path(root, 'fix-sample').read_bytes() == receipt
    assert all(p.read_bytes() == raw for p, raw in before.items())


@pytest.mark.parametrize('target', ['source', 'journal', 'manifest', 'readiness', 'receipt', 'identity'])
def test_drift_never_overrides_conflict(sample, monkeypatch, target):
    root, folder, journal = sample
    m.restore(root, 'fix-sample', apply=True)
    receipt = m.receipt_path(root, 'fix-sample')
    if target == 'source':
        with (folder / 'acceptance.md').open('a') as h: h.write('modified')
    elif target == 'journal': journal.write_text('{}')
    elif target == 'manifest': monkeypatch.setattr(m, 'latest_manifest', lambda *_: {'run_id': 'two'})
    elif target == 'readiness': monkeypatch.setattr(m, 'archived_readiness', lambda *_: {'status': 'blocked'})
    else:
        record = json.loads(receipt.read_text())
        record['proof']['to' if target == 'receipt' else 'change_id'] = 'wrong'
        receipt.write_text(json.dumps(record))
    with pytest.raises(ValueError): m.restore(root, 'fix-sample', apply=True)
    hits = {h['kind'] for h in inspect_document(root, folder / 'acceptance.md', completed=True)}
    assert 'metadata-restoration-invalid' in hits
    assert 'current-metadata-conflict' in hits


def test_missing_or_symlink_receipt_fails_closed(sample):
    root, folder, journal = sample
    assert inspect_document(root, folder / 'acceptance.md', completed=True)
    path = m.receipt_path(root, 'fix-sample')
    path.parent.mkdir()
    path.symlink_to(journal)
    with pytest.raises(ValueError): m.restore(root, 'fix-sample', apply=True)


@pytest.mark.parametrize('state', ['failed', 'partial', 'blocked', 'passed'])
def test_only_not_started_is_restorable(sample, state):
    root, folder, _ = sample
    (folder / 'acceptance.md').write_text(f'---\nacceptance_status: {state}\n---\n')
    with pytest.raises(ValueError): m.restore(root, 'fix-sample', apply=True)
    assert not m.receipt_path(root, 'fix-sample').exists()


def test_failed_proof_cannot_create_receipt(sample, monkeypatch):
    root, _, _ = sample
    monkeypatch.setattr(m, 'archived_readiness', lambda *_: {'status': 'blocked'})
    with pytest.raises(ValueError): m.restore(root, 'fix-sample', apply=True)
    assert not m.receipt_path(root, 'fix-sample').exists()
