"""Trusted subprocess context carries no independent authorization."""
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import pytest
from app.governance.controlled_successor import authority
from app.governance.replacement_executor import ArchiveDriver
from app.governance.replacement_tool_context import read_context


def value():
    return dict(actor='owner',space_id='space',repository_id='repo',binding_revision='a'*64,
                operation_id='original-operation',fence=2)


def pipe_value(payload):
    read,write=os.pipe()
    os.write(write,json.dumps(payload).encode());os.close(write)
    return read


@pytest.mark.parametrize('damage',[{'fence':True},{'fence':0},{'operation_id':None},{'actor':''},{'approved':True}])
def test_context_rejects_unknown_and_inconsistent_claims(damage):
    with pytest.raises(ValueError):read_context(pipe_value(value()|damage))


def test_context_cannot_be_loaded_from_repository_file(tmp_path):
    file=tmp_path/'context.json';file.write_text(json.dumps(value()))
    with file.open('rb') as stream:
        with pytest.raises(ValueError,match='requires_pipe'):read_context(stream.fileno())


@pytest.mark.parametrize('routed', [False, True])
def test_workflow_child_inherits_only_identity_and_fence(tmp_path,monkeypatch,routed):
    project=SimpleNamespace(root=tmp_path,key='b'*64,space_id='space',repository_id='repo',binding_revision='a'*64)
    driver=object.__new__(ArchiveDriver);driver.project=project;driver.package=None
    monkeypatch.setattr(driver,'recheck_tools',lambda:None)
    if routed: driver.package=SimpleNamespace(root=tmp_path/'deployed-tools')
    calls=[]
    def run(args,**kwargs):
        assert kwargs['cwd']==tmp_path
        if routed: assert kwargs['env']['PYTHONPATH']==str(tmp_path/'deployed-tools/src/backend')
        assert args[:3]==[sys.executable,'-m','app.governance.replacement_tool_context']
        assert args[4]=='sync-workflow-status.py'
        fd=int(args[3]);assert kwargs['pass_fds']==(fd,)
        calls.append(read_context(os.dup(fd)))
        return subprocess.CompletedProcess(args,0,'','')
    monkeypatch.setattr(subprocess,'run',run)
    with authority(None,project,'owner','original-operation',2):
        driver._run([sys.executable,str(tmp_path/'scripts/sync-workflow-status.py'),'--event','opsx.archive'],tmp_path)
    assert calls==[value()]


def test_timeout_preserves_safe_error_and_closes_inherited_fd(tmp_path,monkeypatch):
    project=SimpleNamespace(root=tmp_path,key='b'*64,space_id='space',repository_id='repo',binding_revision='a'*64)
    driver=object.__new__(ArchiveDriver);driver.project=project;driver.package=None
    monkeypatch.setattr(driver,'recheck_tools',lambda:None)
    fds=[]
    def timeout(args,**kwargs):
        fds.extend(kwargs['pass_fds']);raise subprocess.TimeoutExpired(args,180)
    monkeypatch.setattr(subprocess,'run',timeout)
    with authority(None,project,'owner'):
        with pytest.raises(ValueError,match='archive_tool_timeout'):
            driver._run([sys.executable,str(tmp_path/'scripts/validate-change-identity.py')],tmp_path)
    for fd in fds:
        with pytest.raises(OSError):os.fstat(fd)
