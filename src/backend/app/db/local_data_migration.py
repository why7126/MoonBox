"""本地 SQLite 路径预检与离线迁移；不会在启动时移动数据。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
from datetime import datetime
from uuid import uuid4

CANONICAL = Path('data/sqlite/moonbox.db')
LEGACY = Path('data/runtime/backend/sqlite/moonbox.db')
DATABASE_URL = 'sqlite:////app/data/sqlite/moonbox.db'
LEGACY_MEDIA = ('uploads', 'processed', 'media')


def _safe_file(path: Path) -> None:
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValueError('database_path_unsafe')
    for parent in path.parents:
        if parent.is_symlink():
            raise ValueError('database_parent_unsafe')


def _digest(path: Path) -> str:
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def _legacy_media_files(root: Path, name: str) -> list[Path]:
    directory = root / 'data/runtime/backend' / name
    for parent in (directory, *directory.parents):
        if parent.is_symlink():
            raise ValueError('legacy_media_path_unsafe')
    if directory.is_symlink():
        raise ValueError('legacy_media_path_unsafe')
    if not directory.is_dir():
        return []
    items = list(directory.rglob('*'))
    if any(path.is_symlink() for path in items):
        raise ValueError('legacy_media_path_unsafe')
    return [path for path in items if path.is_file()]


def inspect_database(path: Path) -> dict:
    """只读报告；表名来自 SQLite 元数据，输出不含行内容或宿主路径。"""
    _safe_file(path)
    if not path.exists():
        return {'exists': False}
    with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) as db:
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('database_integrity_failed')
        names = [row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        counts = {name: db.execute('SELECT count(*) FROM "' + name.replace('"', '""') + '"').fetchone()[0] for name in names}
        version = db.execute('PRAGMA user_version').fetchone()[0]
        schema_version = db.execute('SELECT schema_version FROM schema_metadata WHERE id=1').fetchone()[0] if 'schema_metadata' in names else None
        logical = hashlib.sha256()
        for statement in db.iterdump():
            logical.update(statement.encode('utf-8'))
            logical.update(b'\n')
    return {'exists': True, 'bytes': path.stat().st_size, 'sha256': _digest(path),
            'logical_sha256': logical.hexdigest(), 'user_version': version,
            'schema_version': schema_version, 'table_counts': counts}


def report(root: Path) -> dict:
    root = Path(root).absolute()
    canonical = inspect_database(root / CANONICAL)
    legacy = inspect_database(root / LEGACY)
    different = canonical['exists'] and legacy['exists'] and (
        canonical['logical_sha256'] != legacy['logical_sha256'] or
        canonical['schema_version'] != legacy['schema_version'])
    media = {}
    for name in LEGACY_MEDIA:
        files = _legacy_media_files(root, name)
        media[name] = {'files': len(files), 'bytes': sum(path.stat().st_size for path in files)}
    return {'canonical': canonical, 'legacy': legacy, 'different': bool(different),
            'legacy_media': media}


def preflight(root: Path, database_url: str) -> dict:
    root = Path(root).absolute()
    if database_url != DATABASE_URL:
        raise ValueError('sqlite_database_url_not_canonical')
    _safe_file(root / CANONICAL)
    _safe_file(root / LEGACY)
    if any(Path(str(root / LEGACY) + suffix).exists() for suffix in ('', '-wal', '-shm')):
        raise ValueError('legacy_database_requires_offline_migration')
    if any(_legacy_media_files(root, name) for name in LEGACY_MEDIA):
        raise ValueError('legacy_media_requires_review')
    return {'canonical_mount': True, 'legacy_database': False}


def _backup(source: Path, target: Path) -> None:
    _safe_file(source)
    target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with sqlite3.connect(source.as_uri() + '?mode=ro', uri=True) as original, sqlite3.connect(target) as copy:
        original.backup(copy)
        if copy.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('backup_integrity_failed')
    target.chmod(0o600)
    with target.open('rb') as handle:
        os.fsync(handle.fileno())


def migrate(root: Path, *, select: str, confirm_stopped: bool) -> dict:
    root = Path(root).absolute()
    if not confirm_stopped:
        raise ValueError('stop_services_before_migration')
    if select not in ('legacy', 'canonical'):
        raise ValueError('explicit_source_required')
    before = report(root)
    if not before[select]['exists']:
        raise ValueError('selected_database_missing')
    folder = root / 'data/runtime/migrations' / (datetime.now().strftime('%Y%m%d%H%M%S') + '-' + uuid4().hex[:8])
    folder.mkdir(mode=0o700, parents=True, exist_ok=False)
    for name, relative in (('legacy', LEGACY), ('canonical', CANONICAL)):
        if before[name]['exists']:
            _backup(root / relative, folder / (name + '.sqlite'))
    manifest = {'selected': select, 'before': before, 'switched': False,
                'task': {'id': folder.name, 'type': 'local_data_migration',
                         'status': 'prepared', 'spans': ['inventory', 'source_backup', 'target_backup']}}
    output = folder / 'manifest.json'
    output.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True), encoding='utf-8')
    output.chmod(0o600)
    if select == 'legacy':
        target = root / CANONICAL
        target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        stage = target.parent / ('.moonbox-migration-' + uuid4().hex + '.sqlite')
        try:
            shutil.copyfile(folder / 'legacy.sqlite', stage)
            stage.chmod(0o600)
            if inspect_database(stage)['logical_sha256'] != before['legacy']['logical_sha256']:
                raise ValueError('staged_database_mismatch')
            os.replace(stage, target)
            manifest['switched'] = True
            manifest['task']['spans'].append('switch')
        finally:
            stage.unlink(missing_ok=True)
    manifest['task']['status'] = 'switched' if manifest['switched'] else 'preserved'
    output.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True), encoding='utf-8')
    output.chmod(0o600)
    return {'inventory_id': folder.name, 'selected': select, 'switched': manifest['switched'],
            'legacy_preserved': before['legacy']['exists'], 'canonical_preserved': before['canonical']['exists']}


def rollback(root: Path, inventory_id: str, *, confirm_stopped: bool) -> dict:
    root = Path(root).absolute()
    if not confirm_stopped:
        raise ValueError('stop_services_before_rollback')
    if not re.fullmatch(r'[0-9]{14}-[0-9a-f]{8}', inventory_id):
        raise ValueError('invalid_inventory_id')
    folder = root / 'data/runtime/migrations' / inventory_id
    manifest_path = folder / 'manifest.json'
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError('migration_manifest_missing')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest.get('selected') not in ('legacy', 'canonical'):
        raise ValueError('migration_manifest_invalid')
    previous = folder / 'canonical.sqlite'
    if manifest.get('selected') != 'legacy' or not previous.is_file():
        raise ValueError('rollback_source_missing')
    current = root / CANONICAL
    _backup(current, folder / ('before-rollback-' + uuid4().hex + '.sqlite'))
    stage = current.parent / ('.moonbox-rollback-' + uuid4().hex + '.sqlite')
    try:
        shutil.copyfile(previous, stage)
        stage.chmod(0o600)
        if inspect_database(stage)['sha256'] != inspect_database(previous)['sha256']:
            raise ValueError('rollback_checksum_mismatch')
        os.replace(stage, current)
    finally:
        stage.unlink(missing_ok=True)
    manifest.setdefault('task', {}).setdefault('spans', []).append('rollback')
    manifest['task']['status'] = 'rolled_back'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True), encoding='utf-8')
    return {'rolled_back': True, 'inventory_id': inventory_id}


def cleanup_legacy(root: Path, inventory_id: str, *, confirm_stopped: bool, verified: bool) -> dict:
    root = Path(root).absolute()
    if not confirm_stopped:
        raise ValueError('stop_services_before_cleanup')
    if not verified:
        raise ValueError('verify_services_before_cleanup')
    if not re.fullmatch(r'[0-9]{14}-[0-9a-f]{8}', inventory_id):
        raise ValueError('invalid_inventory_id')
    folder = root / 'data/runtime/migrations' / inventory_id
    manifest_path = folder / 'manifest.json'
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError('migration_manifest_missing')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest.get('selected') not in ('legacy', 'canonical'):
        raise ValueError('migration_manifest_invalid')
    legacy = root / LEGACY
    canonical = root / CANONICAL
    if not manifest['before']['legacy']['exists'] or not (folder / 'legacy.sqlite').is_file():
        raise ValueError('legacy_backup_missing')
    if not legacy.exists():
        return {'legacy_removed': False, 'already_absent': True}
    if inspect_database(legacy)['logical_sha256'] != manifest['before']['legacy']['logical_sha256']:
        raise ValueError('legacy_database_changed')
    if any(Path(str(legacy) + suffix).exists() for suffix in ('-wal', '-shm')):
        raise ValueError('legacy_database_companion_files_present')
    selected = manifest['selected']
    selected_backup = folder / (selected + '.sqlite')
    expected_hash = inspect_database(selected_backup)['logical_sha256']
    if not canonical.exists() or inspect_database(canonical)['logical_sha256'] != expected_hash:
        raise ValueError('canonical_database_not_verified')
    _safe_file(legacy)
    legacy.unlink()
    manifest.setdefault('task', {}).setdefault('spans', []).append('cleanup_legacy')
    manifest['task']['status'] = 'legacy_cleaned'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True), encoding='utf-8')
    return {'legacy_removed': True, 'inventory_id': inventory_id}


def main() -> None:
    parser = argparse.ArgumentParser(description='本地 SQLite 路径预检及离线迁移')
    parser.add_argument('action', choices=('preflight', 'report', 'migrate', 'rollback', 'cleanup-legacy'))
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--database-url', default=DATABASE_URL)
    parser.add_argument('--select', choices=('legacy', 'canonical'))
    parser.add_argument('--inventory-id')
    parser.add_argument('--confirm-stopped', action='store_true')
    parser.add_argument('--verified', action='store_true', help='确认 API、Worker、关键数据与重启验证已通过')
    args = parser.parse_args()
    try:
        if args.action == 'preflight':
            result = preflight(args.root, args.database_url)
        elif args.action == 'report':
            result = report(args.root)
        elif args.action == 'migrate':
            result = migrate(args.root, select=args.select, confirm_stopped=args.confirm_stopped)
        elif args.action == 'rollback':
            result = rollback(args.root, args.inventory_id or '', confirm_stopped=args.confirm_stopped)
        else:
            result = cleanup_legacy(args.root, args.inventory_id or '', confirm_stopped=args.confirm_stopped,
                                    verified=args.verified)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    except (ValueError, OSError, sqlite3.Error) as exc:
        # Only stable codes are exposed, not filesystem paths or SQL contents.
        code = str(exc) if isinstance(exc, ValueError) and re.fullmatch(r'[a-z_]+', str(exc)) else 'local_data_operation_failed'
        parser.exit(2, code + '\n')


if __name__ == '__main__':
    main()
