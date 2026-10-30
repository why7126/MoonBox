import hashlib
import pytest
from app.moonbox_rollout.recovery import Entry, fingerprint, preflight, rotation_candidates


def file(value, mode=0o644):
    return Entry('file', hashlib.sha256(value.encode()).hexdigest(), mode, len(value))


@pytest.mark.parametrize('before,after,current,action', [
    (file('a'), file('b'), file('b'), 'restore'),
    (file('a'), file('b'), file('c'), 'conflict'),
    (None, file('b'), file('b'), 'delete'),
    (None, file('b'), file('c'), 'conflict'),
    (file('a'), None, None, 'restore'),
    (file('a'), None, file('new'), 'conflict'),
    (file('a'), file('b'), file('a'), 'already_restored'),
    (file('a'), file('a'), file('external'), 'unchanged'),
    (file('a', 0o755), file('a'), file('a', 0o600), 'conflict'),
])
def test_three_way_preserves_later_edits(before, after, current, action):
    manifests = [{ 'src/file': e } if e else {} for e in (before, after, current)]
    assert preflight(*manifests, ['src/file']) == [{'path': 'src/file', 'action': action}]


def test_scope_and_baseline_participate_in_reuse_identity():
    manifest = {'src/file': file('a')}
    first = fingerprint(manifest, policy_version='p1', head_commit='h1')
    assert first == fingerprint(manifest, policy_version='p1', head_commit='h1')
    assert first != fingerprint(manifest, policy_version='p2', head_commit='h1')
    assert first != fingerprint(manifest, policy_version='p1', head_commit='h2')


@pytest.mark.parametrize('path', ['../secret', '/secret', 'src/../secret', '.git/config', 'src//x', 'src\\x', ''])
def test_untrusted_path_rejected(path):
    with pytest.raises(ValueError):
        preflight({}, {}, {}, [path])


def test_ten_unprotected_versions_plus_pins_not_ten_turns():
    points = [dict(id=str(i), sequence=i, state='complete', changed=True) for i in range(14)]
    points += [dict(id='pending', sequence=15, state='incomplete', changed=True)]
    points += [dict(id='read-only', sequence=16, state='complete', changed=False)]
    assert rotation_candidates(points, {'0', '1'}) == ['3', '2']
    with pytest.raises(ValueError):
        rotation_candidates(points, set(), keep=0)


def test_capture_includes_ignored_writable_files_but_excludes_runtime_and_shared_logs(tmp_path):
    from app.moonbox_exec_server.scope import names
    from app.moonbox_core.delivery_policy import writable_roots
    for relative in ('src/ignored.txt', 'src/.env.secret', 'src/node_modules/lib.js', 'docs/guide.md', 'docs/spec-logs/shared.md'):
        path = tmp_path/relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('synthetic')
    (tmp_path/'.gitignore').write_text('src/ignored.txt\n')
    assert set(names(tmp_path, writable_roots('example-change'))) == {'src/ignored.txt', 'docs/guide.md'}


@pytest.mark.parametrize('value', ['0', '-1', 'bad', '１'])
def test_invalid_retention_configuration_is_rejected(monkeypatch, value):
    from app.moonbox_rollout.catalog import retention_count
    monkeypatch.setenv('MOONBOX_WORKSPACE_RECOVERY_KEEP', value)
    with pytest.raises(ValueError, match='invalid_retention'):
        retention_count()
