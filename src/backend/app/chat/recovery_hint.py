"""Conservative, one-check suppression of unchanged local executor records."""
import hashlib
import itertools
import re
from pathlib import Path

_HINTS = {}


def fingerprint(server_factory, workspace, thread_id):
    root = getattr(server_factory, 'recovery_runtime_root', None)
    auth = getattr(server_factory, 'recovery_auth_source', None)
    if root is None or auth is None or not re.fullmatch(r'[0-9a-f-]{36}', thread_id): return None
    from app.chat.container_server import preflight_key
    runtime = Path(root)/hashlib.sha256(str(workspace).encode()).hexdigest()
    if not runtime.is_dir(): return None
    try:
        files = list(itertools.islice((runtime/'sessions').rglob('*.jsonl'), 4097))
        if len(files)>4096: return None
        matched = [p for p in files if p.name.endswith(thread_id+'.jsonl')]
        if len(matched)!=1 or matched[0].is_symlink(): return None
        files = matched + list(runtime.glob('state_*.sqlite*'))
        if any(p.is_symlink() for p in files): return None
        stats = [(p.name,p.stat().st_ino,p.stat().st_size,p.stat().st_mtime_ns,p.stat().st_ctime_ns) for p in sorted(files)]
        key = preflight_key(workspace,runtime,auth)
        if key is None: return None
        return hashlib.sha256((key+repr(stats)).encode()).hexdigest()
    except (OSError, ValueError): return None


def unchanged(tid, signature):
    previous = _HINTS.pop(tid, None)
    return signature is not None and previous == signature


def remember(tid, before, after):
    if before is not None and before == after:
        if len(_HINTS)>=1024: _HINTS.clear()
        _HINTS[tid]=after
