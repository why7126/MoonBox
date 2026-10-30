"""Build an executor-only Git view containing objects reachable from this checkout alone."""
import os
from pathlib import Path
import subprocess
import shutil
from uuid import uuid4
from app.chat.workspace import trusted_directory, git_env
from app.moonbox_worktree import Repository, WorktreeConflict


def prepare(workspace, runtime):
    repo = Repository.open(workspace)
    if (repo.root / '.git').is_dir():
        return None
    runtime = trusted_directory(runtime)
    target = runtime / ('git-view-' + repo.head())
    if target.exists():
        # Reuse is permitted only at exactly the recorded immutable checkout HEAD.
        marker = target / 'moonbox-head'
        if marker.is_symlink() or marker.read_text().strip() != repo.head():
            raise WorktreeConflict('git_view_revision_changed')
        trusted_directory(target)
    else:
        destination = target
        target = runtime / ('git-view-building-' + uuid4().hex)
        target.mkdir(mode=0o700)
        def git(*args, data=None):
            result = subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', *args],
                input=data, env=git_env(), capture_output=True, timeout=60)
            if result.returncode:
                raise WorktreeConflict('git_view_unavailable')
            return result.stdout
        try:
            git('init', '--bare', str(target))
            # Stream the pack; no shared object directory/alternates or peer refs are mounted.
            with (target / 'incoming.pack').open('xb') as pack:
                result = subprocess.run(['git', '-C', str(repo.root), 'pack-objects', '--stdout', '--revs'],
                    input=(repo.head()+'\n').encode(), env=git_env(), stdout=pack, stderr=subprocess.DEVNULL, timeout=60)
                if result.returncode:
                    raise WorktreeConflict('git_view_unavailable')
            with (target / 'incoming.pack').open('rb') as pack:
                result = subprocess.run(['git', '--git-dir='+str(target), 'index-pack', '--stdin'],
                    stdin=pack, env=git_env(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
                if result.returncode:
                    raise WorktreeConflict('git_view_unavailable')
            (target / 'incoming.pack').unlink()
            git('--git-dir='+str(target), 'update-ref', 'refs/heads/workspace', repo.head())
            git('--git-dir='+str(target), 'symbolic-ref', 'HEAD', 'refs/heads/workspace')
            git('--git-dir='+str(target), 'config', 'core.bare', 'false')
            git('--git-dir='+str(target), 'config', 'core.worktree', '/work')
            git('--git-dir='+str(target), 'read-tree', repo.head())
            (target / 'moonbox-head').write_text(repo.head())
            target.rename(destination)
            target = destination
        except BaseException:
            # Only remove the private directory created by this invocation.
            if target != destination:
                shutil.rmtree(target)
            raise
    pointer = runtime / 'git-pointer'
    if pointer.is_symlink():
        raise WorktreeConflict('git_view_pointer_invalid')
    pointer.write_text('gitdir: /git\n')
    return target, pointer
