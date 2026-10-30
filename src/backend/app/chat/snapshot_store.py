"""Streaming workspace capture with immutable, database-backed manifests."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import PurePosixPath
import stat
import subprocess
import time

from sqlalchemy import delete, insert, select, update
from app.chat import content_store, service
from app.chat.content_schema import entries, objects, versions
from app.chat.workspace import WorkspaceError, trusted_directory, git_env


def names(root):
    """Git enumerates authorized tracked/unignored paths without stdout aggregation."""
    probe = subprocess.run(['git', '-C', str(root), 'rev-parse', '--is-inside-work-tree'],
                           env=git_env(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if probe.returncode == 0:
        process = subprocess.Popen(['git', '-C', str(root), 'ls-files', '-co', '--exclude-standard', '-z'],
            env=git_env(), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        pending = b''
        try:
            while data := process.stdout.read(65536):
                pending += data
                while b'\0' in pending:
                    raw, pending = pending.split(b'\0', 1)
                    if raw:
                        try: yield raw.decode('utf-8')
                        except UnicodeDecodeError: raise WorkspaceError('仓库路径非UTF-8') from None
                if len(pending) > 65536:
                    raise WorkspaceError('仓库路径格式异常')
            if process.wait() or pending:
                raise WorkspaceError('仓库文件枚举失败')
        finally:
            process.stdout.close()
            if process.poll() is None:
                process.terminate(); process.wait()
    else:
        def walk(directory, prefix=''):
            with os.scandir(directory) as children:
                for child in children:
                    if child.name == '.git': continue
                    relative = prefix + child.name
                    if child.is_dir(follow_symlinks=False):
                        fd = os.open(child.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
                        try: yield from walk(fd, relative + '/')
                        finally: os.close(fd)
                    else: yield relative
        fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try: yield from walk(fd)
        finally: os.close(fd)


def parent_fd(root_fd, relative):
    path = PurePosixPath(relative)
    if path.is_absolute() or not path.parts or any(part in ('..', '.git') for part in path.parts):
        raise WorkspaceError('仓库包含越界路径')
    fd = os.dup(root_fd)
    try:
        for part in path.parts[:-1]:
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd); fd = next_fd
        return fd, path.name
    except BaseException:
        os.close(fd); raise


def read_file(db, cid, root_fd, relative, *, retain, checkpoint=None):
    if retain:
        verified = read_file(db, cid, root_fd, relative, retain=False)
        if verified['kind'] != 'file': return verified
        from app.chat.schema import conversations
        owner = db.execute(select(conversations.c.space_id, conversations.c.repository_id).where(conversations.c.id == cid)).one()
        existing = db.scalar(select(objects.c.id).join(conversations, conversations.c.id == objects.c.conversation_id).where(
            conversations.c.space_id == owner.space_id, conversations.c.repository_id == owner.repository_id,
            objects.c.status == 'complete', objects.c.sha256 == verified['digest'],
            objects.c.byte_count == verified['byte_count']).limit(1).with_for_update())
        if existing: return {**verified, 'object_id': existing}
    directory, name = parent_fd(root_fd, relative)
    try:
        info = os.stat(name, dir_fd=directory, follow_symlinks=False)
        if stat.S_ISLNK(info.st_mode):
            value = os.readlink(name, dir_fd=directory).encode()
            return dict(kind='symlink', mode=0, digest=hashlib.sha256(value).hexdigest(),
                        byte_count=len(value), object_id=None)
        if not stat.S_ISREG(info.st_mode): raise WorkspaceError('工作区包含特殊文件')
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        try:
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
                raise WorkspaceError('文件类型或硬链接不安全')
            digest = hashlib.sha256(); size = 0
            oid = content_store.begin(db, cid, 'file') if retain else None
            number = 0; pending = bytearray()
            while block := os.read(fd, 64 * 1024):
                digest.update(block); size += len(block)
                if retain:
                    pending.extend(block)
                    if len(pending) == content_store.CHUNK_BYTES:
                        content_store.append(db, oid, number, bytes(pending))
                        pending.clear(); number += 1
                        if checkpoint: checkpoint(db)
            if retain and pending:
                content_store.append(db, oid, number, bytes(pending))
                if checkpoint: checkpoint(db)
            after = os.fstat(fd)
            fields = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns', 'st_mode', 'st_nlink')
            current = os.stat(name, dir_fd=directory, follow_symlinks=False)
            if any(getattr(before, field) != getattr(after, field) or
                   getattr(after, field) != getattr(current, field) for field in fields) or size != before.st_size:
                raise WorkspaceError('文件在快照期间变化')
            if retain: oid = content_store.finish(db, oid)
            return dict(kind='file', mode=stat.S_IMODE(after.st_mode), digest=digest.hexdigest(),
                        byte_count=size, object_id=oid)
        finally: os.close(fd)
    finally: os.close(directory)


def page(db, version_id, after='', limit=100):
    if not 0 < limit <= 256: raise ValueError('invalid snapshot page')
    return list(db.execute(select(entries).where(entries.c.version_id == version_id,
        entries.c.path_key > after).order_by(entries.c.path_key).limit(limit)).mappings())


def capture(factory, cid, tid, root, phase, *, fence=None, roots=None, policy_roots=None):
    root = trusted_directory(root)
    def enumerate_paths():
        if policy_roots is not None:
            from app.moonbox_exec_server.scope import names as scoped_names
            yield from scoped_names(root, policy_roots)
        elif roots is None:
            yield from names(root)
        else:
            for prefix in roots:
                if prefix not in ('openspec', 'issues', 'iterations'): raise ValueError('invalid trusted scope')
                if (root/prefix).exists():
                    for path in names(root/prefix): yield prefix+'/'+path
    version = service.identity(); vid = version['id']
    with factory() as db:
        if fence: fence(db)
        previous = db.scalar(select(versions.c.id).where(versions.c.conversation_id == cid,
            versions.c.turn_id == tid, versions.c.phase == phase,
            versions.c.status.in_(('building', 'abandoned'))).order_by(versions.c.created_at.desc()).limit(1))
        if previous:
            vid = previous
            db.execute(update(versions).where(versions.c.id == vid).values(status='building'))
        else:
            db.execute(insert(versions).values(**version, conversation_id=cid, turn_id=tid,
                                              phase=phase, status='building'))
        db.commit()
    cursor = ''
    while previous:
        with factory() as db:
            if fence: fence(db)
            batch = page(db, vid, cursor, 256)
            if not batch: break
            cursor = batch[-1]['path_key']
            db.execute(update(entries).where(entries.c.version_id == vid,
                entries.c.path_key.in_([item['path_key'] for item in batch])).values(verified=0))
            db.commit()
    root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        with factory() as db:
            if fence: fence(db)
            pending_bytes = 0; pending_files = 0; last_commit = time.monotonic()
            def checkpoint(session):
                nonlocal pending_bytes, pending_files, last_commit
                pending_bytes += content_store.CHUNK_BYTES
                if pending_bytes >= 4*1024*1024 or time.monotonic()-last_commit >= .25:
                    session.commit()
                    pending_bytes = 0; pending_files = 0; last_commit = time.monotonic()
                    if fence: fence(session)
            for relative in enumerate_paths():
                key = hashlib.sha256(relative.encode()).hexdigest()
                old = db.execute(select(entries).where(entries.c.version_id == vid, entries.c.path_key == key)).mappings().first()
                if old and old['verified'] == 2: continue
                value = read_file(db, cid, root_fd, relative, retain=True, checkpoint=checkpoint)
                if old:
                    db.execute(update(entries).where(entries.c.version_id == vid, entries.c.path_key == key)
                        .values(**value, verified=2))
                else:
                    db.execute(insert(entries).values(version_id=vid, path_key=key, path=relative, verified=2, **value))
                db.execute(update(versions).where(versions.c.id == vid).values(scan_cursor=key))
                pending_files += 1
                if pending_files >= 256 or time.monotonic()-last_commit >= .25:
                    db.commit(); pending_files = 0; pending_bytes = 0; last_commit = time.monotonic()
                    if fence: fence(db)
            db.commit()
        # Entries absent from the restarted first pass are no longer part of its manifest.
        while True:
            with factory() as db:
                if fence: fence(db)
                stale = list(db.scalars(select(entries.c.path_key).where(entries.c.version_id == vid,
                    entries.c.verified == 0).limit(256)))
                if not stale: break
                db.execute(delete(entries).where(entries.c.version_id == vid, entries.c.path_key.in_(stale)))
                db.commit()
        # Independently enumerate again; changed/added/removed files invalidate
        # publication. There is no claim of an atomic filesystem point-in-time.
        with factory() as db:
            if fence: fence(db)
            pending_files = 0; last_commit = time.monotonic()
            for relative in enumerate_paths():
                key = hashlib.sha256(relative.encode()).hexdigest()
                old = db.execute(select(entries).where(entries.c.version_id == vid, entries.c.path_key == key)).mappings().first()
                if old is None: raise WorkspaceError('快照期间文件清单变化')
                current = read_file(db, cid, root_fd, relative, retain=False)
                if any(old[field] != current[field] for field in ('kind', 'mode', 'digest', 'byte_count')):
                    raise WorkspaceError('快照期间文件内容变化')
                db.execute(update(entries).where(entries.c.version_id == vid,
                    entries.c.path_key == key).values(verified=1))
                pending_files += 1
                if pending_files >= 256 or time.monotonic()-last_commit >= .25:
                    db.commit(); pending_files = 0; last_commit = time.monotonic()
                    if fence: fence(db)
            db.commit()
        with factory() as db:
            if db.scalar(select(entries.c.path_key).where(entries.c.version_id == vid, entries.c.verified != 1).limit(1)):
                raise WorkspaceError('快照期间文件清单变化')
        manifest = hashlib.sha256(); cursor = ''
        while True:
            with factory() as db: batch = page(db, vid, cursor, 256)
            if not batch: break
            for item in batch:
                manifest.update(json.dumps([item[k] for k in ('path','kind','mode','digest','byte_count')],
                                           ensure_ascii=False, separators=(',', ':')).encode())
            cursor = batch[-1]['path_key']
        with factory() as db:
            if fence: fence(db)
            db.execute(update(versions).where(versions.c.id == vid).values(status='complete',
                manifest_hash=manifest.hexdigest(), updated_at=service.now()))
            from app.chat.observability import storage_span
            storage_span(db, tid, 'snapshot_scan', metadata={'storage_mode': 'chunks_v2'})
            db.commit()
        return {'format_version': 2, 'version_id': vid, 'hash': manifest.hexdigest()}
    except BaseException:
        # A secondary database outage must not hide the original failure.
        from contextlib import suppress
        with suppress(Exception):
            with factory() as db:
                db.execute(update(versions).where(versions.c.id == vid).values(status='abandoned'))
                db.commit()
        raise
    finally: os.close(root_fd)


def import_legacy(db, cid, tid, snapshot):
    if snapshot.get('format_version') == 2: return snapshot
    row = service.identity(); vid = row['id']
    db.execute(insert(versions).values(**row, conversation_id=cid, turn_id=tid,
        phase='legacy', status='complete', manifest_hash=snapshot['hash']))
    for path, item in snapshot['files'].items():
        text = item.get('text'); oid = None
        if text is not None:
            data = text.encode()
            oid = content_store.put(db, cid, 'legacy', (data[n:n+content_store.CHUNK_BYTES]
                for n in range(0, len(data), content_store.CHUNK_BYTES)))
        db.execute(insert(entries).values(version_id=vid, path_key=hashlib.sha256(path.encode()).hexdigest(),
            path=path, kind=item['kind'], mode=0o755 if item.get('executable') else 0o644,
            digest=item['sha256'], byte_count=item['size'], object_id=oid, verified=1))
    return {'format_version': 2, 'version_id': vid, 'hash': snapshot['hash']}


def diff_page(db, before, after, cursor='', limit=100):
    """Merge ordered manifest pages; memory depends on window, not file count."""
    if db.scalar(select(versions.c.id).where(versions.c.id.in_((before, after)), versions.c.status == 'expired').limit(1)):
        raise service.ChatError(2507, '文件版本已按恢复点保留策略轮转，对话记录仍保留', 410)
    def iterator(vid):
        key = cursor
        while True:
            batch = page(db, vid, key, 100)
            if not batch: return
            yield from batch
            key = batch[-1]['path_key']
    left = iterator(before); right = iterator(after)
    old = next(left, None); new = next(right, None); result = []; last = cursor
    def rename_peer(item, source, destination):
        from sqlalchemy import exists
        other = entries.alias('other_manifest')
        matches = list(db.execute(select(entries).where(entries.c.version_id == source,
            entries.c.digest == item['digest'], entries.c.kind == item['kind'], entries.c.mode == item['mode'],
            ~exists(select(other.c.path_key).where(other.c.version_id == destination,
                other.c.path_key == entries.c.path_key))).limit(2)).mappings())
        return matches[0] if len(matches) == 1 else None
    while old is not None or new is not None:
        key = min(x['path_key'] for x in (old,new) if x is not None)
        a = old if old and old['path_key'] == key else None
        b = new if new and new['path_key'] == key else None
        previous_path = None; skip_renamed_delete = False; renamed_before = None
        if a is None:
            peer = rename_peer(b, before, after)
            reverse = rename_peer(peer, after, before) if peer else None
            if reverse and reverse['path_key'] == b['path_key']:
                previous_path = peer['path']; renamed_before = peer
        elif b is None:
            peer = rename_peer(a, after, before)
            reverse = rename_peer(peer, before, after) if peer else None
            skip_renamed_delete = bool(reverse and reverse['path_key'] == a['path_key'])
        if not skip_renamed_delete and (a is None or b is None or any(a[k] != b[k] for k in ('digest','kind','mode'))):
            original = a or renamed_before
            result.append({'file_id': key, 'path': (b or a)['path'],
                'status': 'renamed' if previous_path else 'added' if a is None else 'deleted' if b is None else 'modified',
                'previous_path': previous_path,
                'before_file_id': original['path_key'] if original else None,
                'before_sha256': original['digest'] if original else None, 'after_sha256': b['digest'] if b else None,
                'before_size': original['byte_count'] if original else 0, 'after_size': b['byte_count'] if b else 0,
                'patch': None, 'diff_status': 'content_available', 'reason': '全文按需加载', 'before_object': original['object_id'] if original else None,
                'after_object': b['object_id'] if b else None})
        if a is not None: old = next(left, None)
        if b is not None: new = next(right, None)
        last = key
        if len(result) == limit: break
    return {'files': result, 'next_cursor': last if old is not None or new is not None else None}
