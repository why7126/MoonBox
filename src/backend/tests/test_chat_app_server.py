from pathlib import Path
import sys
import io
import json
import queue
import threading
import time
from types import SimpleNamespace
import pytest
from app.chat.app_server import AppServer,ExecutorError

def test_stream_burst_backpressures_without_losing_terminal_or_usage():
    frames = [{'method': 'item/agentMessage/delta', 'params': {'delta': 'a'}} for _ in range(140)]
    frames += [{'method': 'turn/completed'}, {'method': 'thread/tokenUsage/updated'}]
    server = object.__new__(AppServer)
    server.incoming = queue.Queue(maxsize=128)
    server.failure = None
    server.closed = False
    server.process = SimpleNamespace(stdout=io.BytesIO(b''.join(json.dumps(frame).encode() + b'\n' for frame in frames)))
    reader = threading.Thread(target=server._read, daemon=True)
    reader.start()
    deadline = time.monotonic() + 2
    while not server.incoming.full() and time.monotonic() < deadline:
        time.sleep(.01)
    assert server.incoming.full()
    time.sleep(1.2)
    assert reader.is_alive()
    assert server.failure is None
    received = [server.incoming.get(timeout=2) for _ in frames]
    reader.join(timeout=2)
    assert received == frames
    assert not reader.is_alive()
    assert server.failure == 'executor_disconnected'


def test_closing_full_stream_queue_unblocks_reader():
    server = object.__new__(AppServer)
    server.incoming = queue.Queue(maxsize=1)
    server.incoming.put({})
    server.failure = None
    server.closed = False
    server.process = SimpleNamespace(stdout=io.BytesIO(b'{"method":"turn/completed"}\n'))
    reader = threading.Thread(target=server._read, daemon=True)
    reader.start()
    server.closed = True
    reader.join(timeout=2)
    assert not reader.is_alive()
    assert server.failure is None

@pytest.fixture
def server_config(tmp_path):
    root=tmp_path.resolve();workspace=root/'workspace';workspace.mkdir();home=root/'home';home.mkdir();config=home/'codex';config.mkdir()
    fake=root/'fake-codex';source=(Path(__file__).parent/'fixtures/chat_app_server.py').read_text()
    fake.write_text('#!'+sys.executable+'\n'+source);fake.chmod(0o700)
    return dict(executable=fake,workspace=workspace,codex_home=config,home=home,timeout=1)

def test_interleaved_notifications_survive_rpc_and_resume_verifies_mapping(server_config):
    with AppServer(**server_config) as server:
        assert server.connect()=='thread'
        assert server.connect('thread')=='thread'
        assert server.start_turn('thread','synthetic')=='turn'
        assert server.event()['method']=='item/agentMessage/delta'
        assert server.event()['params']['turn']['status']=='completed'
    assert server.process.poll() is not None

@pytest.mark.parametrize(('mode','code'), [('disconnect','executor_disconnected'),('interactive','executor_interactive_request'),('oversized','executor_frame_limit')])
def test_uncertain_protocol_never_fabricates_terminal(server_config,mode,code):
    (server_config['workspace']/'fixture-mode').write_text(mode)
    with AppServer(**server_config) as server:
        server.connect()
        with pytest.raises(ExecutorError) as error:server.start_turn('thread','synthetic')
        assert error.value.code==code


def test_foreign_workspace_is_not_resumed(server_config):
    (server_config['workspace']/'fixture-mode').write_text('mismatch')
    with AppServer(**server_config) as server:
        with pytest.raises(ExecutorError) as error:server.connect('thread')
        assert error.value.code=='executor_workspace_mismatch'


def test_credentials_cannot_be_placed_in_repository(server_config):
    bad=server_config['workspace']/'credentials';bad.mkdir();server_config['codex_home']=bad
    with pytest.raises(ExecutorError):AppServer(**server_config)


def test_interrupt_does_not_block_terminal_when_ack_is_missing(server_config):
    (server_config['workspace']/'fixture-mode').write_text('interrupt-without-ack')
    with AppServer(**server_config) as server:
        server.connect();server.start_turn('thread','synthetic');server.interrupt('thread','turn')
        assert server.event()['method']=='item/agentMessage/delta'
        assert server.event()['params']['turn']['status']=='interrupted'


def test_named_profile_downgrades_write(server_config):
    with AppServer(**server_config,permission_profile='moonbox-write',write=True) as server:
        calls=[]
        def rpc(method,params):
            calls.append((method,params));return {'turn':{'id':'turn'}}
        server.rpc=rpc
        server.start_turn('thread','synthetic');server.write=False;server.start_turn('thread','synthetic')
        assert calls[0][1]['permissions']=='moonbox-write'
        assert calls[1][1]['permissions']=='moonbox-read'
        assert all('sandboxPolicy' not in params for _,params in calls)


def test_named_profile_supports_governance_scope(server_config):
    with AppServer(**server_config,write_scope='governance_write') as server:
        calls=[]
        def rpc(method,params):
            calls.append((method,params));return {'turn':{'id':'turn'}}
        server.rpc=rpc
        server.start_turn('thread','synthetic')
        assert calls[0][1]['permissions']=='moonbox-governance'
