from scripts.workflow_sync.title_gate import validate_generated


def test_generation_gate_checks_before_completion(tmp_path):
    oid='BUG-0099-title';d=tmp_path/'issues/bugs/plan'/oid;d.mkdir(parents=True)
    (d/'bug.md').write_text('# 没有元数据的业务标题\n')
    (d/'trace.md').write_text('---\ntitle: 测试业务追溯\n---\n# 测试业务追溯\n')
    before=(d/'trace.md').read_bytes()
    assert validate_generated(tmp_path,'bug.generate',oid)
    assert (d/'trace.md').read_bytes()==before
    (d/'bug.md').write_text('---\ntitle: 测试业务缺陷\n---\n# 测试业务缺陷\n')
    assert not validate_generated(tmp_path,'bug.generate',oid)
    other=tmp_path/'issues/bugs/plan/BUG-9999-other';other.mkdir();(other/'bug.md').write_text('# bad')
    assert not validate_generated(tmp_path,'bug.generate',oid)


def test_missing_change_and_identity_are_rejected(tmp_path):
    assert validate_generated(tmp_path, 'bug.opsx', 'BUG-0099-title')
    assert validate_generated(tmp_path, 'bug.opsx', 'BUG-0099-title', 'missing-change')


def test_registry_title_sync_preserves_literal_backslashes(tmp_path, monkeypatch):
    import yaml
    from scripts.workflow_sync import patch
    from scripts.workflow_sync.collect import IssueRecord
    from scripts.workflow_sync.derive import DerivedIssue
    monkeypatch.setattr(patch, 'ROOT', tmp_path)
    directory = tmp_path/'issues/bugs/plan/BUG-0099-title'
    directory.mkdir(parents=True)
    registry = tmp_path/'issues/bugs/_registry.yaml'
    registry.write_text('entries:\n  - id: BUG-0099-title\n    title: 旧业务标题\n    status: captured\n')
    title = '支持中文路径 C:\\new\\file 与引号"业务"'
    issue = IssueRecord('BUG-0099-title', 'bug', directory, title=title, priority='medium')
    derived = DerivedIssue(issue.issue_id, 'bug', 'draft', None, '')
    patch.patch_registry_entry(registry, issue, derived, None)
    assert yaml.safe_load(registry.read_text())['entries'][0]['title'] == title


def test_engine_stops_before_projection_on_invalid_title(tmp_path, monkeypatch):
    from scripts.workflow_sync import engine
    monkeypatch.setattr(engine, 'ROOT', tmp_path)
    monkeypatch.setattr(engine, 'resolve_sprint_id', lambda *a, **kw: (None, 'not in sprint'))
    def unexpected_write_path():
        raise AssertionError('invalid titles reached projection loading')
    monkeypatch.setattr(engine, 'load_all_issues', unexpected_write_path)
    folder = tmp_path/'issues/bugs/plan/BUG-0099-title'
    folder.mkdir(parents=True)
    file = folder/'bug.md'
    file.write_text('# Invalid draft\n')
    before = file.read_bytes()
    report = engine.SyncEngine().run(event='bug.generate', bug_id='BUG-0099-title', sprint_id='auto')
    assert not report.ok and not report.updated
    assert file.read_bytes() == before
