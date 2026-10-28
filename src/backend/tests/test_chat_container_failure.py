import queue
import time
from types import SimpleNamespace
import pytest
from app.chat.app_server import ExecutorError
from app.chat.container_server import ContainerAppServer


@pytest.mark.parametrize('event,exit_code,expected',[('oom\n',137,'container_memory_exhausted'),('',137,'container_terminated'),('',1,'executor_disconnected')])
def test_container_diagnostics_require_real_oom_evidence(monkeypatch,event,exit_code,expected):
    server=ContainerAppServer.__new__(ContainerAppServer)
    server.recovery_context=None
    server.incoming=queue.Queue();server.failure='executor_disconnected'
    server.created_epoch=1;server.container_name='synthetic';server.docker='docker'
    server.process=SimpleNamespace(poll=lambda:exit_code)
    monkeypatch.setattr('app.chat.container_server.subprocess.run',lambda *a,**k:SimpleNamespace(returncode=0,stdout=event))
    with pytest.raises(ExecutorError) as error:server._next(time.monotonic()+1)
    assert error.value.code==expected
