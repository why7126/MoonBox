"""Independent package failures cannot select workspace code or change evidence."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from app.governance import archive_tools as tools


def fixture_package(tmp_path, monkeypatch):
    root = tmp_path / 'package'
    files = {'scripts/archive-change.sh': b'exit 0', 'scripts/archive-recovery-guard.py': b'pass',
             'src/backend/app/governance/archive_tools.py': b'pass'}
    for name, raw in files.items():
        path = root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
    raw = json.dumps({'schema_version': 1, 'files': {k: hashlib.sha256(v).hexdigest() for k,v in files.items()}}).encode()
    (root / 'manifest.json').write_bytes(raw)
    config = tmp_path / 'config.json'
    config.write_text(json.dumps({'schema_version': 1, 'root': str(root), 'host_root': str(root), 'digest': hashlib.sha256(raw).hexdigest()}))
    monkeypatch.setattr(tools, 'CONFIG', config)
    # Unit tests isolate integrity from OS permissions; real Docker tests cover access.
    monkeypatch.setattr(tools.os, 'access', lambda *a: False)
    return root


def test_default_compatibility(tmp_path, monkeypatch):
    monkeypatch.setattr(tools, 'CONFIG', tmp_path / 'absent')
    assert tools.selected() is None
    tools.check_binding({}, None)


@pytest.mark.parametrize('mutation,code', [('drift','digest_mismatch'),('missing','inventory_mismatch'),
                                         ('extra','inventory_mismatch'),('symlink','not_trusted'),('writable','not_trusted')])
def test_fail_closed(tmp_path, monkeypatch, mutation, code):
    root = fixture_package(tmp_path, monkeypatch)
    target = root / 'scripts/archive-change.sh'
    if mutation == 'drift': target.write_text('changed')
    elif mutation == 'missing': target.unlink()
    elif mutation == 'extra': (root/'extra').write_text('extra')
    elif mutation == 'symlink': target.unlink(); target.symlink_to('/etc/passwd')
    else: monkeypatch.setattr(tools.os, 'access', lambda *a: True)
    with pytest.raises(ValueError, match=code): tools.selected()


def test_manifest_traversal_and_unknown_protocol(tmp_path, monkeypatch):
    root = fixture_package(tmp_path, monkeypatch)
    raw = json.dumps({'schema_version': 2, 'files': {'../escape': 'a'*64}}).encode()
    (root/'manifest.json').write_bytes(raw)
    config = json.loads(tools.CONFIG.read_text());config['digest']=hashlib.sha256(raw).hexdigest()
    tools.CONFIG.write_text(json.dumps(config))
    with pytest.raises(ValueError, match='manifest_invalid'): tools.selected()


def test_bindings_resume_replay_rollback_and_legacy(tmp_path, monkeypatch):
    fixture_package(tmp_path, monkeypatch); package = tools.selected()
    root = tmp_path/'business'; root.mkdir()
    digest = tools.operation_binding(root, 'operation', package, original='input')
    before = {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*') if p.is_file()}
    for _ in range(2):
        assert tools.operation_binding(root, 'operation', package, recorded=digest) == digest
    for candidate in (None, tools.ToolPackage(package.root, 'b'*64, package.host_root)):
        with pytest.raises(ValueError, match='version_unproven'):
            tools.operation_binding(root, 'operation', candidate, recorded=digest)
    with pytest.raises(ValueError, match='version_unproven'):
        tools.operation_binding(root, 'legacy', package, recorded='a'*64)
    assert before == {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*') if p.is_file()}


def test_business_root_and_manifest_binding(tmp_path, monkeypatch):
    fixture_package(tmp_path, monkeypatch); package = tools.selected()
    business=tmp_path/'business';business.mkdir();monkeypatch.chdir(business)
    monkeypatch.setenv('MOONBOX_ARCHIVE_ROUTED','1')
    assert tools.business_root(package.root)==business
    tools.check_binding({'archive_tool_digest':package.digest},package)
    with pytest.raises(ValueError,match='version_unproven'): tools.check_binding({},package)
    with pytest.raises(ValueError,match='version_unproven'): tools.check_binding({'archive_tool_digest':package.digest},None)


def test_actual_launch_requires_in_container_validation(tmp_path, monkeypatch):
    from app.chat.container_server import ContainerAppServer
    fixture_package(tmp_path, monkeypatch); package=tools.selected()
    server=object.__new__(ContainerAppServer);server.archive_package=package
    command=server.archive_launch()
    assert command[:3]==['python','-B','-c']
    assert command[3].index('p=selected()') < command[3].index('os.execvp')
    compile(command[3], '<probe>', 'exec')
    monkeypatch.setattr(tools,'selected',lambda:None)
    with pytest.raises(Exception,match='archive_tool_changed'): server.archive_launch()


def test_missing_executor_freezes_claim_before_any_database_action(tmp_path, monkeypatch):
    from app.chat.worker import claim
    fixture_package(tmp_path, monkeypatch)
    import subprocess
    monkeypatch.setattr(subprocess,'run',lambda *a,**k:SimpleNamespace(returncode=1,stdout=''))
    class Untouched:
        def __getattr__(self, name): raise AssertionError('database must remain untouched')
    assert claim(Untouched(),'worker') is None


def test_controlled_input_hash_excludes_only_new_binding_sidecar(tmp_path):
    from app.governance.replacement_inputs import archive_input_tree
    from app.governance.archive_recovery import tree_hash
    (tmp_path/'old').write_text('historical evidence')
    before=tree_hash(tmp_path)
    binding=tmp_path/'.archive-tool-bindings';binding.mkdir();(binding/'one.json').write_text('{}')
    assert archive_input_tree(tmp_path)==before
    (tmp_path/'old').write_text('changed')
    assert archive_input_tree(tmp_path)!=before


def test_driver_routed_subprocess_keeps_business_cwd_and_trusted_imports(tmp_path, monkeypatch):
    from app.governance.replacement_executor import ArchiveDriver
    import subprocess
    fixture_package(tmp_path,monkeypatch);package=tools.selected()
    monkeypatch.setattr(ArchiveDriver,'_trusted',staticmethod(lambda path:None))
    monkeypatch.setattr('shutil.which',lambda name:'/usr/bin/true')
    monkeypatch.setattr('app.governance.replacement_executor.tree_hash',lambda path:'hash')
    business=tmp_path/'business';business.mkdir()
    driver=ArchiveDriver(SimpleNamespace(root=business,key='scope'))
    calls=[]
    def run(args, **kwargs):
        calls.append((args,kwargs))
        return SimpleNamespace(returncode=0,stdout='',stderr='')
    monkeypatch.setattr(subprocess,'run',run)
    driver.validate_static('sample-change')
    assert len(calls)==5
    for args,options in calls:
        assert Path(args[1]).parent==package.scripts
        assert options['cwd']==business
        assert options['env']['PYTHONPATH']==str(package.root/'src/backend')
        assert options['env']['MOONBOX_ARCHIVE_ROUTED']=='1'
    monkeypatch.setattr(tools,'selected',lambda:None)
    with pytest.raises(ValueError,match='archive_tool_changed'):driver.validate_static('sample-change')
    assert len(calls)==5


def test_nested_unknown_binding_named_files_remain_fingerprinted(tmp_path):
    from app.governance.replacement_inputs import archive_input_tree
    (tmp_path/'.archive-tool-bindings').mkdir()
    nested=tmp_path/'history/.archive-tool-bindings';nested.mkdir(parents=True)
    file=nested/'evidence';file.write_text('first')
    before=archive_input_tree(tmp_path)
    file.write_text('second')
    assert before!=archive_input_tree(tmp_path)


def test_removed_controlled_binding_cannot_downgrade_to_legacy(tmp_path, monkeypatch):
    fixture_package(tmp_path,monkeypatch);package=tools.selected()
    root=tmp_path/'business';root.mkdir()
    recorded=tools.operation_binding(root,'op',package,original='original')
    assert len(recorded)==64 and recorded.startswith('rt1:')
    next((root/'openspec/archive/.archive-tool-bindings').iterdir()).unlink()
    with pytest.raises(ValueError,match='version_unproven'):
        tools.operation_binding(root,'op',None,recorded=recorded)
