"""Readiness heartbeat independent of blocking worker maintenance."""
from contextlib import contextmanager
import json
import threading
import time

from app.chat.platform import fingerprint


@contextmanager
def worker_heartbeat(state, interval=1.0):
    stopped = threading.Event()
    target = state / 'worker-ready.json'
    temporary = state / 'worker-ready.tmp'
    configuration = fingerprint()

    def publish():
        temporary.write_text(json.dumps({'time': time.time(), 'configuration': configuration}))
        temporary.chmod(0o600)
        temporary.replace(target)

    def refresh():
        while not stopped.wait(interval):
            try:
                publish()
            except OSError:
                # A failed publisher must not leave an apparently ready worker.
                target.unlink(missing_ok=True)
                return

    publish()
    thread = threading.Thread(target=refresh, name='worker-heartbeat', daemon=True)
    thread.start()
    try:
        yield
    finally:
        stopped.set()
        thread.join()
        target.unlink(missing_ok=True)
        temporary.unlink(missing_ok=True)
