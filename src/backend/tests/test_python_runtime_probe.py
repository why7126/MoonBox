import json
import subprocess
import sys
from app.verification.python_probe import PYTHON_PROBE


def test_real_imports_and_anyio_thread_are_exercised():
    result=subprocess.run([sys.executable,'-c',PYTHON_PROBE],capture_output=True,text=True,timeout=10)
    assert result.returncode==0
    payload=json.loads(result.stdout)
    assert payload['status']=='ready'
    assert set(payload['versions'])=={'pytest','httpx','anyio'}


def test_missing_dependency_is_failure_not_readiness(tmp_path):
    (tmp_path/'pytest.py').write_text('raise ImportError("synthetic missing dependency")')
    result=subprocess.run([sys.executable,'-c',PYTHON_PROBE],cwd=tmp_path,capture_output=True,text=True,timeout=10)
    assert result.returncode!=0 and not result.stdout


def test_container_probe_timeout_cleans_exact_owned_name(monkeypatch):
    from app.verification.python_probe import probe_image
    from app.verification.runner import RunnerUnavailable
    from types import SimpleNamespace
    import pytest
    calls=[]
    monkeypatch.setattr('shutil.which',lambda _: '/usr/bin/docker')
    def run(argv,**kwargs):
        calls.append(argv)
        if argv[1]=='run':raise subprocess.TimeoutExpired(argv,15)
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr(subprocess,'run',run)
    with pytest.raises(RunnerUnavailable,match='python_test_runtime_unavailable'):
        probe_image('sha256:'+'a'*64)
    assert calls[1][-1]==calls[0][calls[0].index('--name')+1]
    assert '--network' in calls[0] and 'none' in calls[0] and '--read-only' in calls[0]


def test_browser_failure_preserves_python_probe(monkeypatch):
    from app.verification import worker_probe
    from app.verification.runner import RunnerUnavailable
    from types import SimpleNamespace
    monkeypatch.setattr(worker_probe,'probe_browser_image',lambda _: (_ for _ in ()).throw(RunnerUnavailable('browser_probe_failed')))
    monkeypatch.setattr(worker_probe,'approved_template',lambda:SimpleNamespace(key='a'*64,data={'base':{'python_image':'approved'}}))
    monkeypatch.setattr(worker_probe,'probe_image',lambda _: {'status':'ready'})
    result=worker_probe.inspect_worker_capabilities('browser')
    assert result['browser']['reason_code']=='browser_probe_failed'
    assert result['python']['status']=='ready'
