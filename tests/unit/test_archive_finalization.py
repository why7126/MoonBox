"""Read-only synthetic document cases; not production archive evidence."""
from pathlib import Path
import pytest
from app.governance.archive_finalization import build_report, inspect_document, current_claims, needs_finalize, paragraphs


def put(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


@pytest.fixture
def archived(tmp_path):
    folder = tmp_path / 'openspec/archive/2026-10-30-fix-sample'
    put(folder / 'trace.md', '---\nstatus: archived\n---\n# 追溯\n')
    return tmp_path, folder


@pytest.mark.parametrize('text,kind', [
    ('当前交付状态：in_sprint，尚未实施。', 'current-state-conflict'),
    ('当前交付状态：\nin_sprint，尚未实施。', 'current-state-conflict'),
    ('## 当前交付状态\n\nin_sprint，尚未实施。', 'current-state-conflict'),
    ('## 历史记录\n当前交付状态：in_sprint。', 'current-state-review'),
    ('2026-10-01 当前交付状态：in_sprint。', 'current-state-review'),
    ('不覆盖首次 applied 及 execution.completed_at。', None),
    ('如果当前交付状态为 pending，则禁止归档。', None),
    ('当前生产部署状态尚未实施。', None),
    ('## 历史记录\n2026-10-01 当时验收 failed。\n\n## 最新验收\n已通过。', None),
    ('```yaml\n当前交付状态: pending\n```', None),
])
def test_current_claims(text, kind):
    hits = current_claims(text, completed=True)
    assert [h['kind'] for h in hits] == ([kind] if kind else [])
    assert current_claims(text, completed=False) == []


@pytest.mark.parametrize('text,blocked', [
    ('[证据](missing.md)', True),
    ('[证据][proof]\n\n[proof]: missing.md', True),
    ('## 历史记录\n[证据](missing.md)', True),
    ('## 历史记录\n原始路径 `openspec/changes/fix-sample/trace.md`', False),
    ('```md\n[样例](missing.md)\n```', False),
    ('[远程](https://example.com/docs) [锚点](#标题)', False),
    ('[证据](trace.md)', False),
    ('证据：`openspec/changes/fix-sample/trace.md`', True),
    ('[证据](openspec/archive/2026-10-30-fix-sample/missing.png)', True),
    ('[越界](../../../../secret.md)', True),
])
def test_navigation_and_history_unchanged(archived, text, blocked):
    root, folder = archived
    path = put(folder / 'acceptance.md', text)
    before = path.read_bytes()
    assert bool(inspect_document(root, path)) == blocked
    assert path.read_bytes() == before


def test_partial_parent_links_checked_without_changing_status(archived):
    root, folder = archived
    parent = put(root / 'issues/requirements/review/REQ-0001-sample/requirement.md',
                 '---\nstatus: approved\n---\nfix-sample 部分交付。当前交付状态：pending。\n')
    assert build_report(root, 'fix-sample')['status'] == 'finalized'
    put(parent.parent / 'acceptance.md', '[证据](missing.md)')
    assert build_report(root, 'fix-sample')['status'] == 'blocked'
    assert 'approved' in parent.read_text()


def test_sync_and_promotion_recovery(archived):
    root, folder = archived
    assert not needs_finalize(root, 'fix-sample')
    trace = folder / 'trace.md'
    trace.write_text('---\nstatus: applied\n---\n')
    assert needs_finalize(root, 'fix-sample')
    assert build_report(root, 'fix-sample')['status'] == 'blocked'
    trace.write_text('---\nstatus: archived\n---\n')
    issue = put(root / 'issues/bugs/review/BUG-0001-sample/bug.md', '---\nstatus: done\n---\nfix-sample\n')
    assert needs_finalize(root, 'fix-sample')
    assert build_report(root, 'fix-sample')['status'] == 'blocked'
    target = root / 'issues/bugs/archive' / issue.parent.name
    target.parent.mkdir(parents=True)
    issue.parent.rename(target)
    assert not needs_finalize(root, 'fix-sample')
    assert build_report(root, 'fix-sample')['status'] == 'finalized'


def test_symlink_and_identity_fail_closed(archived):
    root, folder = archived
    put(root / 'openspec/changes/fix-sample/trace.md', 'active')
    assert build_report(root, 'fix-sample')['status'] == 'blocked'
    (root / 'openspec/changes/fix-sample/trace.md').unlink()
    (root / 'openspec/changes/fix-sample').rmdir()
    path = put(folder / 'acceptance.md', '[证据](linked.md)')
    (folder / 'linked.md').symlink_to(folder / 'trace.md')
    assert inspect_document(root, path)[0]['kind'] == 'unsafe-reference'


def test_stale_metadata_detected_from_linked_archive_but_partial_preserved(archived):
    root, folder = archived
    issue = root / 'issues/bugs/review/BUG-0001-sample'
    put(issue / 'bug.md', '---\nstatus: in_sprint\n---\n当前交付状态：尚未实施。')
    put(issue / 'trace.md', '---\nstatus: in_sprint\nopenspec_changes:\n  - change_id: fix-sample\n---\n')
    assert 'current-metadata-conflict' in {h['kind'] for h in build_report(root, 'fix-sample')['findings']}
    put(issue / 'acceptance.md', '---\nacceptance_status: partial\n---\n')
    assert build_report(root, 'fix-sample')['status'] == 'finalized'


def test_historical_applied_trace_is_valid_without_rewriting(archived):
    root, folder = archived
    trace = put(folder / 'trace.md', '---\nstatus: applied\nexecution:\n  completed_at: 2026-10-30\n---\n')
    put(folder / 'tasks.md', '- [x] 已完成\n')
    before = trace.read_bytes()
    assert build_report(root, 'fix-sample')['status'] == 'finalized'
    assert trace.read_bytes() == before


def test_table_rows_keep_separate_subjects():
    rows = list(paragraphs('| fix-one | archived |\n| fix-two | applied |'))
    assert len(rows) == 2
    assert 'fix-two' not in rows[0][1]


@pytest.mark.parametrize('suffix', ['：说明', '，说明', '；说明', '。说明'])
def test_bare_reference_chinese_punctuation(archived, suffix):
    root, folder = archived
    put(root / 'docs/guide.md', '# 指南')
    path = put(folder / 'acceptance.md', '引用 docs/guide.md' + suffix)
    assert inspect_document(root, path) == []
    path.write_text('引用 docs/missing.md' + suffix)
    assert inspect_document(root, path)[0]['kind'] == 'missing-reference'


def test_explicit_link_can_contain_chinese_colon(archived):
    root, folder = archived
    put(root / 'docs/指南：说明.md', '# 指南')
    path = put(folder / 'acceptance.md', '[指南](docs/指南：说明.md)')
    assert inspect_document(root, path) == []


def test_incidental_history_reference_does_not_expand_issue_scope(archived):
    root, folder = archived
    issue = root / 'issues/bugs/archive/BUG-0002-unrelated'
    put(issue / 'bug.md', '---\nstatus: done\n---\n当前交付状态：pending。')
    put(issue / 'trace.md', '---\nopenspec_changes:\n  - change_id: fix-unrelated\n---\n历史参考 fix-sample\n')
    assert build_report(root, 'fix-sample')['status'] == 'finalized'


@pytest.mark.parametrize('explicit', [False, True])
def test_chinese_enumeration_path_boundary(archived, explicit):
    root, folder = archived
    target = 'openspec/changes/another/tasks.md'
    put(root / target, '# 任务')
    text = f'[入口]({target}、acceptance.md)' if explicit else f'实施入口：{target}、acceptance.md；仅计划。'
    path = put(folder / 'design.md', text)
    hits = inspect_document(root, path)
    assert bool(hits) == explicit  # Explicit punctuation remains part of the link.
    (root / target).unlink()
    assert inspect_document(root, path)  # Never hide a truly missing target.


def test_explicit_chinese_filename_is_not_split(archived):
    root, folder = archived
    put(folder / '任务、验收.md', '# 完成')
    path = put(folder / 'design.md', '[证据](任务、验收.md)')
    assert not inspect_document(root, path)
