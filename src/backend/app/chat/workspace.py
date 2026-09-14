"""独立会话代码目录与内容快照；不是容器/凭证隔离的替代品。"""
from __future__ import annotations
import difflib
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import tarfile
from uuid import UUID

class WorkspaceError(RuntimeError):
    pass


def trusted_directory(path):
    path = Path(path).absolute()
    # Check every component before resolving; never silently accept a symlink alias.
    for part in [*reversed(path.parents), path]:
        if part.is_symlink(): raise WorkspaceError('目录包含符号链接')
    if not path.is_dir(): raise WorkspaceError('目录不存在')
    return path


def git_env():
    return {'PATH': '/usr/bin:/bin', 'HOME': '/nonexistent', 'GIT_CONFIG_NOSYSTEM': '1',
            'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_TERMINAL_PROMPT': '0', 'LC_ALL': 'C'}


def git(repo, *args):
    result = subprocess.run(['git', '-C', str(repo), *args], env=git_env(), capture_output=True, timeout=30)
    if result.returncode: raise WorkspaceError('仓库操作失败')
    return result.stdout


def prepare_workspace(source, root, conversation_id, max_bytes=512*1024*1024, max_files=10000):
    """Copy only the configured repository's committed tree; never import hooks/config/untracked secrets."""
    try: identifier = str(UUID(conversation_id))
    except (ValueError, TypeError, AttributeError): raise WorkspaceError('会话标识无效')
    source, root = trusted_directory(source), trusted_directory(root)
    target = root / identifier
    if target.exists() or target.is_symlink(): raise WorkspaceError('工作区已存在，必须使用已保存映射恢复')
    head = git(source, 'rev-parse', '--verify', 'HEAD').decode().strip()
    if not re.fullmatch(r'[0-9a-f]{40,64}', head): raise WorkspaceError('仓库基准无效')
    target.mkdir(mode=0o700)
    process = subprocess.Popen(['git', '-C', str(source), 'archive', '--format=tar', head], env=git_env(), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    total = 0; count = 0
    try:
        with tarfile.open(fileobj=process.stdout, mode='r|') as archive:
            for member in archive:
                path = PurePosixPath(member.name)
                if path.is_absolute() or '..' in path.parts or '.git' in path.parts:
                    raise WorkspaceError('仓库包含越界路径')
                # Reject links/devices rather than extracting or following their targets.
                if not (member.isdir() or member.isfile()): raise WorkspaceError('仓库包含不支持的链接或特殊文件')
                destination = target.joinpath(*path.parts)
                if member.isdir(): destination.mkdir(parents=True, exist_ok=True); continue
                count += 1; total += member.size
                if count > max_files or total > max_bytes: raise WorkspaceError('仓库超过工作区初始化边界')
                destination.parent.mkdir(parents=True, exist_ok=True)
                stream = archive.extractfile(member)
                with destination.open('xb') as output:
                    while data := stream.read(65536): output.write(data)
                destination.chmod(0o700 if member.mode & 0o111 else 0o600)
        if process.wait(timeout=30) != 0: raise WorkspaceError('仓库导出失败')
        git(target, 'init', '-q', '-b', 'chat/'+identifier)
        # Establish a clean session baseline; imported files are not user changes.
        git(target, '-c', 'core.hooksPath=/dev/null', 'add', '--all')
        git(target, '-c', 'core.hooksPath=/dev/null', '-c', 'user.name=MoonBox',
            '-c', 'user.email=workspace@example.invalid', 'commit', '--allow-empty', '-qm', 'Session baseline')
        return {'workspace_id': identifier, 'source_commit': head, 'path': target}
    except Exception:
        # Do not delete possibly modified code; caller records a failed initialization for controlled cleanup.
        raise
    finally:
        if process.poll() is None: process.kill()
        process.wait(timeout=5)
        process.stdout.close()


def workspace_path(root, workspace_id):
    try: identifier = str(UUID(workspace_id))
    except (ValueError, TypeError, AttributeError): raise WorkspaceError('工作区标识无效')
    base = trusted_directory(root)
    return trusted_directory(base / identifier)


def snapshot(path, *, max_files=10000, max_total_bytes=512*1024*1024, text_bytes=65536, max_text_bytes=4*1024*1024):
    """Use dir-fd/O_NOFOLLOW reads. Links are metadata only, and are never traversed."""
    root = trusted_directory(path); files = {}; total = 0; text_total = 0
    def walk(fd, prefix=''):
        nonlocal total, text_total
        for name in sorted(os.listdir(fd)):
            if name == '.git': continue
            relative = prefix + name
            info = os.stat(name, dir_fd=fd, follow_symlinks=False)
            if stat.S_ISDIR(info.st_mode):
                child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                try: walk(child, relative+'/')
                finally: os.close(child)
                continue
            if len(files) >= max_files: raise WorkspaceError('工作区文件数量超过快照边界')
            if stat.S_ISLNK(info.st_mode):
                # Hash target spelling without returning it (it may contain a private absolute path).
                value = os.readlink(name, dir_fd=fd).encode()
                files[relative] = {'kind': 'symlink', 'sha256': hashlib.sha256(value).hexdigest(), 'size': len(value), 'text': None, 'reason': '符号链接仅记录元数据'}
                continue
            if not stat.S_ISREG(info.st_mode): raise WorkspaceError('工作区包含特殊文件')
            item = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
            try:
                before = os.fstat(item)
                if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1: raise WorkspaceError('文件类型或硬链接不安全')
                total += before.st_size
                if total > max_total_bytes: raise WorkspaceError('工作区超过快照容量边界')
                digest = hashlib.sha256(); chunks = []; read = 0
                while block := os.read(item, 65536):
                    read += len(block)
                    if read > before.st_size: raise WorkspaceError('文件在快照期间变化')
                    digest.update(block)
                    if before.st_size <= text_bytes and text_total + before.st_size <= max_text_bytes: chunks.append(block)
                after = os.fstat(item)
                if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino) or read != before.st_size:
                    raise WorkspaceError('文件在快照期间变化')
                content = b''.join(chunks); text = None; reason = None
                if before.st_size > text_bytes or text_total + before.st_size > max_text_bytes: reason = '内容超过文本展示边界'
                elif b'\0' in content: reason = '二进制文件'
                else:
                    try: text = content.decode('utf-8'); text_total += before.st_size
                    except UnicodeDecodeError: reason = '非UTF-8文本'
                files[relative] = {'kind': 'file', 'sha256': digest.hexdigest(), 'size': read, 'executable': bool(before.st_mode & 0o111), 'text': text, 'reason': reason}
            finally: os.close(item)
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try: walk(fd)
    finally: os.close(fd)
    manifest = {name: {k: v for k, v in item.items() if k not in ('text', 'reason')} for name, item in files.items()}
    return {'hash': hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest(), 'files': files}


def difference(before, after, max_patch_bytes=262144):
    result = []; used = 0
    for name in sorted(before['files'].keys() | after['files'].keys()):
        old, new = before['files'].get(name), after['files'].get(name)
        if old and new and (old['sha256'], old['kind'], old.get('executable')) == (new['sha256'], new['kind'], new.get('executable')): continue
        item = {'path': name, 'status': 'added' if old is None else 'deleted' if new is None else 'modified',
                'before_sha256': old['sha256'] if old else None, 'after_sha256': new['sha256'] if new else None,
                'before_size': old['size'] if old else 0, 'after_size': new['size'] if new else 0}
        unavailable = next((value['reason'] for value in [old, new] if value and value['text'] is None), None)
        if unavailable: item.update(patch=None, reason=unavailable)
        else:
            patch = ''.join(difflib.unified_diff((old['text'] if old else '').splitlines(True), (new['text'] if new else '').splitlines(True), fromfile='a/'+name, tofile='b/'+name))
            if used + len(patch.encode()) > max_patch_bytes: item.update(patch=None, reason='差异超过展示边界')
            else: item.update(patch=patch, reason=None); used += len(patch.encode())
        result.append(item)
    # Exact content-preserving renames are explicit; modified renames remain honest add/delete pairs.
    removed = [item for item in result if item['status'] == 'deleted']
    consumed = set()
    for item in result:
        if item['status'] != 'added': continue
        previous = next((old for old in removed if old['path'] not in consumed and old['before_sha256'] == item['after_sha256'] and before['files'][old['path']]['kind'] == after['files'][item['path']]['kind']), None)
        if previous:
            consumed.add(previous['path']); item.update(status='renamed', previous_path=previous['path'], before_sha256=previous['before_sha256'], before_size=previous['before_size'], patch='', reason=None)
    result = [item for item in result if not (item['status'] == 'deleted' and item['path'] in consumed)]
    return {'before_hash': before['hash'], 'after_hash': after['hash'], 'files': result}
