"""Bounded response-after-send auditing for requirement-center reads only."""
import json
import logging
from threading import BoundedSemaphore
from time import monotonic
from weakref import finalize
from starlette.background import BackgroundTasks

# Keep the bounded, content-free completion timing observable with the default
# Uvicorn setup as well as deployments that already configure root handlers.
_audit_log = logging.getLogger('moonbox.requirement_center.audit')
_audit_log.setLevel(logging.INFO)
if not _audit_log.hasHandlers():
    _audit_log.addHandler(logging.StreamHandler())

_slots = BoundedSemaphore(16)


def defer_read_audit(request, response, persist, request_id):
    """Return False for synchronous fallback; never discard an audit on overload."""
    if (request.method != 'GET' or response is None or
            not request.url.path.startswith('/api/v1/requirement-center/')):
        return False
    if not _slots.acquire(blocking=False):
        logging.getLogger('moonbox.chat').warning('chat.request_audit_capacity_fallback')
        return False
    # Release reservations even when ASGI send is cancelled before background execution.
    release = finalize(response, _slots.release)
    previous = response.background

    def complete():
        started = monotonic()
        success = False
        try:
            success = persist() is True
        except Exception:
            logging.getLogger('moonbox.chat').warning('chat.request_log_unavailable')
        finally:
            release()
            _audit_log.info(
                'requirement_center.deferred_audit %s', json.dumps({
                    'request_id': request_id, 'success': success,
                    'duration_ms': round((monotonic() - started) * 1000, 2)}))
    try:
        tasks = BackgroundTasks()
        tasks.add_task(complete)
        if previous is not None:
            tasks.add_task(previous)
        response.background = tasks
    except BaseException:
        release()
        raise
    return True
