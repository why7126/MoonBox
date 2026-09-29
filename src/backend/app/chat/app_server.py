"""Version-pinned App Server stdio adapter. Deployment must isolate credentials separately."""
from __future__ import annotations
from collections import deque
import json
import os
from pathlib import Path
import queue
import re
import signal
import subprocess
import sys
import threading
import time
from app.chat.workspace import trusted_directory

class ExecutorError(RuntimeError):
    """Only stable codes leave this adapter; never forward raw protocol errors or stderr."""
    def __init__(self, code):
        self.code = code
        super().__init__(code)


class AppServer:
    VERSION = 'codex-cli 0.153.4'
    def __init__(self, executable, workspace, codex_home, *, home, write=False, timeout=30, permission_profile=None, effort=None, write_scope=None):
        self.workspace = trusted_directory(workspace)
        self.codex_home = trusted_directory(codex_home)
        self.home = trusted_directory(home)
        if self.codex_home == self.workspace or self.workspace in self.codex_home.parents:
            raise ExecutorError('credential_directory_inside_workspace')
        if permission_profile is not None and not re.fullmatch(r'moonbox-(read|write|governance)', permission_profile):
            raise ExecutorError('invalid_permission_profile')
        if effort not in (None,'low','medium','high'):raise ExecutorError('invalid_executor_effort')
        self.effort = effort
        self.write_scope = self._normalize_write_scope(write_scope if write_scope is not None else ('implementation_write' if write else 'read_only'))
        self.permission_profile = permission_profile or self.permission_profile_for_scope(self.write_scope)
        self.timeout = timeout; self.write = write; self.seq = 0
        self.incoming = queue.Queue(maxsize=128); self.pending = deque(); self.failure = None; self.closed = False
        self.env = {'PATH': '/usr/local/bin:/usr/bin:/bin', 'HOME': str(self.home), 'CODEX_HOME': str(self.codex_home)}
        version = subprocess.run(self.version_command(executable), capture_output=True, env=self.env, timeout=30)
        if version.returncode or version.stdout.decode().strip() != self.VERSION:
            raise ExecutorError('unsupported_executor_version')
        self.process = subprocess.Popen([sys.executable, str(Path(__file__).with_name('process_guard.py')), *self.launch_command(executable)],
            cwd=self.workspace, env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, start_new_session=True)
        self.reader = threading.Thread(target=self._read, daemon=True); self.reader.start()
        try:
            self.rpc('initialize', {'clientInfo': {'name': 'moonbox_chat', 'version': '0.1.0'}, **({'capabilities': {'experimentalApi': True}} if self.permission_profile else {})})
            self._send({'method': 'initialized'})
        except Exception:
            self.close(); raise

    def version_command(self, executable):
        return [str(executable), '--version']

    def launch_command(self, executable):
        return [str(executable), 'app-server', '--stdio', '-c', 'shell_environment_policy.inherit="none"']

    def _normalize_write_scope(self, scope):
        if scope in ('implementation_write', 'write', True): return 'implementation_write'
        if scope in ('governance_write', 'governance'): return 'governance_write'
        return 'read_only'

    def permission_profile_for_scope(self, scope):
        return {'implementation_write': 'moonbox-write', 'governance_write': 'moonbox-governance'}.get(self._normalize_write_scope(scope), 'moonbox-read')

    def set_write_scope(self, scope):
        self.write_scope = self._normalize_write_scope(scope)
        self.write = self.write_scope == 'implementation_write'
        self.permission_profile = self.permission_profile_for_scope(self.write_scope)

    def _read(self):
        try:
            while True:
                line = self.process.stdout.readline(262145)
                if not line: self.failure = 'executor_disconnected'; return
                if len(line) > 262144: self.failure = 'executor_frame_limit'; return
                try: value = json.loads(line)
                except (ValueError, UnicodeDecodeError): self.failure = 'executor_invalid_frame'; return
                if not isinstance(value, dict): self.failure = 'executor_invalid_frame'; return
                try: self.incoming.put(value, timeout=1)
                except queue.Full: self.failure = 'executor_buffer_limit'; return
        except (OSError, ValueError):
            self.failure = 'executor_disconnected'

    def _send(self, value):
        try:
            encoded = (json.dumps(value, ensure_ascii=False)+'\n').encode()
            if len(encoded) > 262144: raise ExecutorError('executor_input_limit')
            self.process.stdin.write(encoded); self.process.stdin.flush()
        except (OSError, ValueError): raise ExecutorError('executor_disconnected')

    def _next(self, deadline):
        while time.monotonic() < deadline:
            try: return self.incoming.get(timeout=min(.2, max(.001, deadline-time.monotonic())))
            except queue.Empty:
                if self.failure: raise ExecutorError(self.failure)
        raise ExecutorError('executor_timeout')

    def rpc(self, method, params):
        # One owning worker serializes RPCs; no browser-supplied method names.
        self.seq += 1; request_id = self.seq
        self._send({'id': request_id, 'method': method, 'params': params})
        deadline = time.monotonic()+self.timeout
        while True:
            try: value = self._next(deadline)
            except ExecutorError as error:
                if error.code == 'executor_timeout': raise ExecutorError('executor_timeout_'+method.replace('/', '_'))
                raise
            if 'method' in value and 'id' in value:
                self._send({'id': value['id'], 'error': {'code': -32601, 'message': 'Interactive requests are not supported'}})
                raise ExecutorError('executor_interactive_request')
            if value.get('id') == request_id and 'method' not in value:
                if 'error' in value: raise ExecutorError('executor_rpc_rejected')
                if not isinstance(value.get('result'), dict): raise ExecutorError('executor_invalid_result')
                return value['result']
            if len(self.pending) >= 128: raise ExecutorError('executor_buffer_limit')
            self.pending.append(value)

    def connect(self, thread_id=None):
        policy = {'cwd': str(self.workspace), 'approvalPolicy': 'never', 'sandbox': 'workspace-write' if self.write else 'read-only'}
        if self.permission_profile:
            policy.pop('sandbox')
            policy['permissions'] = self.permission_profile
        if thread_id:
            previous = self.rpc('thread/read', {'threadId': thread_id, 'includeTurns': False})['thread']
            self._verify_thread(previous, thread_id)
            result = self.rpc('thread/resume', {'threadId': thread_id, **policy})
        else: result = self.rpc('thread/start', policy)
        self._verify_thread(result.get('thread', {}), thread_id)
        return result['thread']['id']

    def _verify_thread(self, thread, expected):
        if not isinstance(thread.get('id'), str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,96}', thread['id']) or (expected and thread.get('id') != expected): raise ExecutorError('executor_thread_mismatch')
        if thread.get('cwd') != str(self.workspace): raise ExecutorError('executor_workspace_mismatch')

    def start_turn(self, thread_id, prompt):
        policy = {'sandboxPolicy':
            {'type': 'workspaceWrite', 'writableRoots': [str(self.workspace)], 'networkAccess': False,
             'excludeTmpdirEnvVar': True, 'excludeSlashTmp': True} if self.write else {'type': 'readOnly'}}
        if self.permission_profile:
            # Resolve read/write for every turn, so a governance downgrade cannot retain write rights.
            scope = 'read_only' if self.write_scope == 'implementation_write' and not self.write else self.write_scope
            policy = {'permissions': self.permission_profile_for_scope(scope)}
        result = self.rpc('turn/start', {'threadId': thread_id, 'input': [{'type': 'text', 'text': prompt}],
            'cwd': str(self.workspace), 'approvalPolicy': 'never', **({'effort':self.effort} if self.effort else {}), **policy})
        turn = result.get('turn', {})
        if not isinstance(turn.get('id'), str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,96}', turn['id']): raise ExecutorError('executor_missing_turn')
        return turn['id']

    def interrupt(self, thread_id, turn_id):
        self.seq += 1
        self._send({'id': self.seq, 'method': 'turn/interrupt', 'params': {'threadId': thread_id, 'turnId': turn_id}})
        # Do not block notification consumption waiting for an interrupt ACK.
        # A sent request is not stopped; only matching turn/completed confirms termination.
        return self.seq

    def read_turn(self, thread_id, turn_id):
        result = self.rpc('thread/read', {'threadId': thread_id, 'includeTurns': True})['thread']
        self._verify_thread(result, thread_id)
        return next((turn for turn in result.get('turns', []) if turn.get('id') == turn_id), None)

    def delete_thread(self, thread_id):
        previous = self.rpc('thread/read', {'threadId':thread_id, 'includeTurns':False})['thread']
        self._verify_thread(previous, thread_id)
        self.rpc('thread/delete', {'threadId':thread_id})
        return True

    def event(self, timeout=1):
        if self.pending: return self.pending.popleft()
        try: return self._next(time.monotonic()+timeout)
        except ExecutorError as error:
            if error.code == 'executor_timeout': return None
            raise

    def close(self):
        if self.closed: return
        self.closed = True
        # Terminate the adapter's process group, not an arbitrary PID from persisted data.
        if self.process.poll() is None:
            try: os.killpg(self.process.pid, signal.SIGTERM)
            except ProcessLookupError: pass
        try: self.process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            try: os.killpg(self.process.pid, signal.SIGKILL)
            except ProcessLookupError: pass
            self.process.wait(timeout=3)
        for stream in [self.process.stdin, self.process.stdout]:
            try: stream.close()
            except OSError: pass
        self.reader.join(timeout=1)

    def __enter__(self): return self
    def __exit__(self, *_): self.close()
