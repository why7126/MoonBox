"""Bounded Docker recovery context, shared only within the owning thread."""
from contextvars import ContextVar
from contextlib import contextmanager
import hashlib
import subprocess
import time
from app.chat.app_server import ExecutorError

CURRENT = ContextVar('chat_recovery_runtime', default=None)


class Runtime:
    def __init__(self, tid, seconds=60, lease_token=None):
        self.key = hashlib.sha256(tid.encode()).hexdigest()
        self.lease_token = lease_token
        self.started_epoch = time.time()
        self.deadline = time.monotonic() + seconds
        self.metrics = {'cache_hit': False, 'container_metrics_available': False}

    def remaining(self, maximum):
        value = self.deadline - time.monotonic()
        if value <= 0: raise ExecutorError('executor_timeout_recovery')
        return min(maximum, value)

    def labels(self):
        self.remaining(60)
        return ['--label', 'moonbox.chat.recovery=' + self.key, '--label', 'moonbox.chat.recovery-lease=' + (self.lease_token or self.key)]

    def cleanup(self, *, stale=False):
        # Exact turn label, never a name prefix; no volumes or host data removal.
        filters = ['--filter', 'label=moonbox.chat.recovery='+self.key]
        if not stale: filters += ['--filter', 'label=moonbox.chat.recovery-lease='+(self.lease_token or self.key)]
        result = subprocess.run(['docker', 'ps', '-aq', *filters],
                                capture_output=True, text=True, timeout=5)
        if result.returncode: raise ExecutorError('recovery_cleanup_failed')
        ids = result.stdout.split()
        if ids:
            removed = subprocess.run(['docker', 'rm', '-f', *ids], capture_output=True, timeout=10)
            if removed.returncode: raise ExecutorError('recovery_cleanup_failed')

        check = subprocess.run(['docker', 'ps', '-aq', *filters],
                               capture_output=True, text=True, timeout=5)
        if check.returncode or check.stdout.strip(): raise ExecutorError('recovery_cleanup_failed')


    def collect_metrics(self):
        result = subprocess.run(['docker', 'events', '--since', str(self.started_epoch),
            '--until', str(time.time()), '--filter', 'label=moonbox.chat.recovery-lease='+(self.lease_token or self.key),
            '--format', '{{.Action}}'], capture_output=True, text=True, timeout=5)
        if result.returncode: return
        actions = result.stdout.splitlines()
        self.metrics['container_metrics_available'] = True
        self.metrics['containers_created'] = actions.count('create')
        self.metrics['containers_removed'] = actions.count('destroy')


@contextmanager
def scope(tid, seconds=60, lease_token=None):
    runtime = Runtime(tid, seconds, lease_token)
    token = CURRENT.set(runtime)
    try: yield runtime
    finally: CURRENT.reset(token)


def timeout(maximum):
    runtime = CURRENT.get()
    return runtime.remaining(maximum) if runtime else maximum


def run(*args, **kwargs):
    kwargs['timeout'] = timeout(kwargs.get('timeout', 30))
    return subprocess.run(*args, **kwargs)
