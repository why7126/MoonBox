"""A stopped archive turn may reopen only a fingerprinted partial source."""
import hashlib
import json
from types import SimpleNamespace

import pytest

from app.chat import relations
from app.governance import preparation


CHANGE = 'add-isolated-ac012'
ISSUE = 'REQ-9312-ac012-issue-window'


def _journal(root):
    path = root / 'openspec/archive/.archive-recovery' / f'{CHANGE}.json'
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({'change_id': CHANGE,
                                'expected_spec_hash': hashlib.sha256().hexdigest()}))
    return path


def test_legacy_change_is_readable_only_with_matching_archive_journal(tmp_path):
    base = tmp_path / 'openspec/changes/archive' / f'2026-10-16-{CHANGE}'
    base.mkdir(parents=True)
    (base / 'trace.md').write_text('---\ntitle: 隔离归档\nstatus: applied\n---\n')
    assert relations._entries(tmp_path, CHANGE) == []
    journal = _journal(tmp_path)
    entries = relations._entries(tmp_path, CHANGE)
    assert len(entries) == 1 and entries[0]['status'] == 'archive_pending'
    specs = tmp_path / 'openspec/specs'
    specs.mkdir(parents=True)
    (specs / 'unexpected.md').write_text('external edit')
    assert relations._entries(tmp_path, CHANGE) == []
    assert journal.exists() and base.is_dir()


def test_issue_archive_reentry_needs_exact_source_and_spec_hash(tmp_path):
    archive = tmp_path / 'openspec/archive' / f'2026-10-16-{CHANGE}'
    archive.mkdir(parents=True)
    _journal(tmp_path)
    files = {
        'issues/requirements/_registry.yaml': (
            f'entries:\n  - id: {ISSUE}\n    path: issues/requirements/archive/{ISSUE}/\n'
            '    status: done\n'),
        f'issues/requirements/archive/{ISSUE}/trace.md': (
            f'---\nstatus: done\nopenspec_changes:\n  - change_id: {CHANGE}\n---\n'),
        f'issues/requirements/archive/{ISSUE}/requirement.md': 'isolated requirement',
        f'openspec/archive/{archive.name}/trace.md': (
            f'---\nstatus: archived\nrequirement_id: {ISSUE}\n---\n'),
    }
    snapshot = SimpleNamespace(files={name: body.encode() for name, body in files.items()})
    assert preparation._require_issue_fact_source(snapshot, ISSUE, 'opsx-archive', tmp_path)['id'] == ISSUE
    snapshot.files[f'openspec/archive/{archive.name}/trace.md'] = (
        b'---\nstatus: archived\nrequirement_id: REQ-9999-other\n---\n')
    with pytest.raises(preparation.service.ChatError):
        preparation._require_issue_fact_source(snapshot, ISSUE, 'opsx-archive', tmp_path)
