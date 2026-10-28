"""登记、检查和精确回收临时 Docker 验证资源；默认只预览。"""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'logs/temporary-docker'
PREFIX = 'moonbox.temp.'


class GuardError(Exception):
    pass


def docker(*args):
    try:
        result = subprocess.run(['docker', *args], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise GuardError('docker_unavailable_or_timeout') from error
    if result.returncode:
        # Docker stderr may contain host paths or credentials. Keep output bounded.
        if 'address pools have been fully subnetted' in result.stderr:
            raise GuardError('docker_network_address_pool_exhausted')
        raise GuardError('docker_command_failed:' + args[0])
    return result.stdout.strip()


def daemon():
    value = docker('info', '--format', '{{.ID}}')
    if not value:
        raise GuardError('daemon_identity_missing')
    return hashlib.sha256(value.encode()).hexdigest()


def labels(record):
    return {PREFIX + 'managed': 'true', PREFIX + 'run': record['run'],
            PREFIX + 'expires': str(record['expires'])}


def valid_record(record):
    if (not isinstance(record, dict) or record.get('schema_version') != 1
            or not re.fullmatch(r'[a-f0-9]{32}', str(record.get('run', '')))
            or not re.fullmatch(r'[a-f0-9]{64}', str(record.get('daemon', '')))
            or type(record.get('expires')) is not int
            or type(record.get('created')) is not int
            or not 0 < record['expires'] - record['created'] <= 86400
            or record.get('status') not in ('open', 'closed')):
        raise GuardError('invalid_registry_record')
    return record


def save(folder, record):
    target = folder / (record['run'] + '.json')
    if target.is_symlink():
        raise GuardError('registry_symlink')
    stage = folder / ('.' + uuid.uuid4().hex)
    try:
        with stage.open('x') as stream:
            os.chmod(stage, 0o600)
            json.dump(record, stream, ensure_ascii=False, indent=2)
        stage.replace(target)
    finally:
        stage.unlink(missing_ok=True)


@contextmanager
def locked(folder):
    if any(p.is_symlink() for p in [folder, *folder.parents]):
        raise GuardError('registry_symlink')
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(folder / '.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def load(folder, run):
    if not re.fullmatch(r'[a-f0-9]{32}', run):
        raise GuardError('invalid_run')
    path = folder / (run + '.json')
    if path.is_symlink():
        raise GuardError('registry_symlink')
    record = valid_record(json.loads(path.read_text()))
    if record['run'] != run:
        raise GuardError('registry_identity_mismatch')
    return record


def inventory(record, kind):
    args = ['ps', '-aq', '--no-trunc'] if kind == 'container' else ['network', 'ls', '-q', '--no-trunc']
    # Select by run alone so a damaged managed/expiry label is detected, not hidden.
    ids = docker(*args, '--filter', 'label=' + PREFIX + 'run=' + record['run']).splitlines()
    resources = []
    for resource_id in ids:
        if not re.fullmatch(r'[a-f0-9]{64}', resource_id):
            raise GuardError('invalid_resource_id')
        item = json.loads(docker(kind, 'inspect', resource_id))[0]
        actual = item.get('Config', {}).get('Labels', {}) if kind == 'container' else item.get('Labels', {})
        if item.get('Id') != resource_id or any((actual or {}).get(k) != v for k, v in labels(record).items()):
            raise GuardError('resource_identity_mismatch')
        resources.append(item)
    return resources


def snapshot(record):
    if daemon() != record['daemon']:
        raise GuardError('daemon_mismatch')
    return inventory(record, 'container'), inventory(record, 'network')


def reconcile(folder, record, *, apply=False, expired_only=False, check=False):
    containers, networks = snapshot(record)
    result = {'run': record['run'], 'containers': len(containers), 'networks': len(networks),
              'expired': record['expires'] <= int(time.time()), 'status': 'remaining'}
    if check:
        result['status'] = 'remaining' if containers or networks else 'clean'
        return result
    if expired_only and not result['expired']:
        return {**result, 'status': 'not_due'}
    # Never remove a container with anonymous/named volumes: rm would orphan data.
    if any(m.get('Type') == 'volume' for c in containers for m in c.get('Mounts', [])):
        raise GuardError('volume_requires_manual_review')
    owned = {c['Id'] for c in containers}
    if any(set(n.get('Containers') or {}) - owned for n in networks):
        raise GuardError('network_has_foreign_endpoints')
    if expired_only and any(c.get('State', {}).get('Running') for c in containers):
        raise GuardError('expired_running_requires_review')
    if not apply:
        return {**result, 'status': 'preview' if containers or networks else 'clean'}
    # Caller must stop creating resources first. Re-inspect and compare before each rm.
    for item in containers:
        current = {c['Id']: c for c in inventory(record, 'container')}
        if item['Id'] not in current:
            continue
        if daemon() != record['daemon']:
            raise GuardError('daemon_mismatch')
        if expired_only:
            # No --force: Docker atomically refuses a concurrently started container.
            docker('container', 'rm', item['Id'])
        else:
            docker('container', 'rm', '--force', item['Id'])
    for item in networks:
        current = {n['Id']: n for n in inventory(record, 'network')}
        if item['Id'] not in current:
            continue
        if current[item['Id']].get('Containers'):
            raise GuardError('network_still_connected')
        if daemon() != record['daemon']:
            raise GuardError('daemon_mismatch')
        docker('network', 'rm', item['Id'])
    containers, networks = snapshot(record)
    if containers or networks:
        raise GuardError('cleanup_incomplete')
    record.update(status='closed', closed=int(time.time()))
    save(folder, record)
    return {**result, 'status': 'clean', 'containers': 0, 'networks': 0}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    register = sub.add_parser('register', help='创建前登记；输出创建资源所需标签')
    register.add_argument('--change', required=True)
    register.add_argument('--purpose', choices=['test', 'acceptance', 'repair', 'smoke'], required=True)
    register.add_argument('--ttl-hours', type=int, default=4, choices=range(1, 25))
    for name in ['check', 'cleanup']:
        command = sub.add_parser(name, help='检查零残留' if name == 'check' else '结束清理；默认预览')
        command.add_argument('--run', required=True)
        if name == 'cleanup':
            command.add_argument('--apply', action='store_true', help='确认本 run 已停止创建资源并执行删除')
    reap = sub.add_parser('reap', help='扫描所有登记记录；到期停止资源可回收，运行资源报告阻断')
    reap.add_argument('--apply', action='store_true', help='执行回收；不终止运行容器')
    args = parser.parse_args(argv)
    try:
        with locked(REGISTRY):
            if args.command == 'register':
                if not re.fullmatch(r'[a-z][a-z0-9-]{2,100}', args.change):
                    raise GuardError('invalid_change')
                if not (ROOT / 'openspec/changes' / args.change / 'proposal.md').is_file():
                    raise GuardError('active_change_missing')
                now = int(time.time())
                record = dict(schema_version=1, run=uuid.uuid4().hex, change=args.change,
                              purpose=args.purpose, created=now, expires=now + args.ttl_hours * 3600,
                              daemon=daemon(), status='open')
                save(REGISTRY, record)
                print(json.dumps({'run': record['run'], 'expires': record['expires'], 'labels': labels(record)}))
                return 0
            results = []
            runs = [p.stem for p in sorted(REGISTRY.glob('*.json'))] if args.command == 'reap' else [args.run]
            for run in runs:
                try:
                    record = load(REGISTRY, run)
                    results.append(reconcile(REGISTRY, record, apply=getattr(args, 'apply', False),
                                             expired_only=args.command == 'reap', check=args.command == 'check'))
                except (GuardError, OSError, ValueError, KeyError, TypeError) as error:
                    results.append({'status': 'blocked', 'error': str(error) if isinstance(error, GuardError) else 'invalid_registry_or_response'})
            print(json.dumps({'results': results}, ensure_ascii=False))
            return int(any(r['status'] == 'blocked' or (args.command == 'check' and r['status'] != 'clean') for r in results))
    except (GuardError, OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'status': 'blocked', 'error': str(error) if isinstance(error, GuardError) else 'invalid_registry_or_response'}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
