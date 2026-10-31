"""Immutable deployment tool selection; never accepts an Agent-supplied root.

The optional configuration is fixed outside the repository. Its entire ancestor
chain and package must be non-writable by the runtime identity.
"""
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat

CONFIG = Path('/etc/moonbox/archive-tools.json')
MOUNT = '/opt/moonbox/archive-tools'
PROTOCOL = 1


def trusted(path: Path):
    for item in (path, *path.parents):
        if item.is_symlink() or not item.exists() or os.access(item, os.W_OK):
            raise ValueError('archive_tools_not_trusted')


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('archive_tool_manifest_invalid')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs)


@dataclass(frozen=True)
class ToolPackage:
    root: Path
    digest: str
    host_root: str

    @property
    def scripts(self):
        return self.root / 'scripts'

    def verify(self):
        try:
            trusted(self.root)
            manifest = self.root / 'manifest.json'
            trusted(manifest)
            raw = manifest.read_bytes()
            if len(raw) > 4 * 1024 * 1024 or hashlib.sha256(raw).hexdigest() != self.digest:
                raise ValueError('archive_tool_digest_mismatch')
            data = strict_json(raw)
            if set(data) != {'schema_version', 'files'} or data['schema_version'] != PROTOCOL or not isinstance(data['files'], dict):
                raise ValueError('archive_tool_manifest_invalid')
            actual = set()
            for path in self.root.rglob('*'):
                trusted(path)
                mode = path.lstat().st_mode
                if stat.S_ISDIR(mode):
                    continue
                if not stat.S_ISREG(mode) or path.stat().st_nlink != 1:
                    raise ValueError('archive_tool_manifest_invalid')
                relative = path.relative_to(self.root).as_posix()
                if relative != 'manifest.json':
                    actual.add(relative)
            if actual != set(data['files']):
                raise ValueError('archive_tool_inventory_mismatch')
            for relative, digest in data['files'].items():
                name = PurePosixPath(relative)
                if name.is_absolute() or '..' in name.parts or str(name) != relative:
                    raise ValueError('archive_tool_manifest_invalid')
                if hashlib.sha256((self.root / relative).read_bytes()).hexdigest() != digest:
                    raise ValueError('archive_tool_digest_mismatch')
            required = {'scripts/archive-change.sh', 'scripts/archive-recovery-guard.py',
                        'src/backend/app/governance/archive_tools.py'}
            if not required <= actual:
                raise ValueError('archive_tool_package_incomplete')
            return self
        except (OSError, TypeError, KeyError, json.JSONDecodeError):
            raise ValueError('archive_tool_configuration_invalid') from None


def selected():
    if not CONFIG.exists() and not CONFIG.is_symlink():
        return None
    try:
        trusted(CONFIG)
        data = strict_json(CONFIG.read_bytes())
        if set(data) != {'schema_version', 'root', 'host_root', 'digest'} or data['schema_version'] != PROTOCOL:
            raise ValueError('archive_tool_configuration_invalid')
        for key in ('root', 'host_root'):
            value = data[key]
            if not isinstance(value, str) or not value.startswith('/') or any(c in value for c in ',\n\r') or '..' in Path(value).parts:
                raise ValueError('archive_tool_configuration_invalid')
        return ToolPackage(Path(data['root']), data['digest'], data['host_root']).verify()
    except (OSError, TypeError, KeyError, json.JSONDecodeError):
        raise ValueError('archive_tool_configuration_invalid') from None


def check_binding(manifest, package):
    """Legacy operations cannot silently acquire a new tool identity."""
    expected = manifest.get('archive_tool_digest')
    actual = package.digest if package else None
    if expected != actual:
        raise ValueError('archive_tool_version_unproven')


def business_root(default):
    # Only routed launchers set this; cwd remains the authorized business root.
    if os.environ.get('MOONBOX_ARCHIVE_ROUTED') == '1':
        package = selected()
        if package is None:
            raise ValueError('archive_tool_configuration_missing')
        return Path.cwd()
    return Path(default)


def operation_binding(root, operation_id, package, *, original=None, recorded=None):
    """Bind controlled operations through their existing input_hash column.

    A sidecar carries the pre-write fingerprint; its hash is committed to the DB.
    Recovery only reads it, including completed replay and disabled routing.
    """
    path = root / 'openspec/archive/.archive-tool-bindings' / (hashlib.sha256(operation_id.encode()).hexdigest() + '.json')
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('archive_tool_binding_invalid')
    if recorded is not None:
        if not path.exists():
            if package or recorded.startswith('rt1:'): raise ValueError('archive_tool_version_unproven')
            return recorded
        raw = path.read_bytes()
        if 'rt1:' + hashlib.sha256(raw).hexdigest()[:60] != recorded:
            raise ValueError('archive_tool_binding_invalid')
        value = strict_json(raw)
        check_binding(value, package)
        if value.get('operation_id') != operation_id:
            raise ValueError('archive_tool_binding_invalid')
        return recorded
    if package is None:
        if path.exists(): raise ValueError('archive_tool_version_unproven')
        return original
    value = {'operation_id': operation_id, 'archive_tool_digest': package.digest, 'original': original}
    raw = json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != raw: raise ValueError('archive_tool_binding_invalid')
    else:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    return 'rt1:' + hashlib.sha256(raw).hexdigest()[:60]


def worker_ready():
    """No database writes when a configured rollback executor is unavailable."""
    import subprocess
    try:
        if selected() is None:
            return True
        from app.chat.container_server import ContainerAppServer
        result = subprocess.run(['docker', 'image', 'inspect', '--format', '{{.Id}}', ContainerAppServer.IMAGE],
                                capture_output=True, text=True, timeout=10)
        return result.returncode == 0 and result.stdout.strip().startswith('sha256:')
    except (ValueError, OSError, subprocess.TimeoutExpired):
        return False
