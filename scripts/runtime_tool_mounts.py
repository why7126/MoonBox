"""Recognize empty tool-directory mounts injected into the Chat executor sandbox."""

import os
from pathlib import Path

TOOL_NAMES = {'.agents', '.codex'}
IGNORED_TREE_NAMES = {
    '.git', '.venv', 'node_modules', 'dist', 'build', 'coverage',
    '.pytest_cache', '.vite', '__pycache__', '.mintlify',
}
IGNORED_ROOT_TREES = {
    'logs', 'tmp', 'data/runtime', 'data/sqlite', 'data/uploads',
    'data/processed', 'data/minio', 'data/s3', 'data/mysql', 'data/tmp',
    'data/ai-usage', 'data/visual-evidence',
}


def repository_tool_paths(root: Path):
    """Find tool-name entries in project-owned trees without following links."""
    root = root.resolve()
    def fail(error):
        raise error

    for parent, directories, files in os.walk(root, followlinks=False, onerror=fail):
        base = Path(parent)
        kept = []
        for name in directories:
            path = base / name
            relative = path.relative_to(root).as_posix()
            if relative == '.agents' and not path.is_symlink():
                kept.append(name)  # Exempt this directory, not its descendants.
                continue
            if name in TOOL_NAMES:
                yield path
                continue
            if name in IGNORED_TREE_NAMES or relative in IGNORED_ROOT_TREES:
                continue
            kept.append(name)
        directories[:] = kept
        for name in files:
            if name in TOOL_NAMES:
                yield base / name


def is_ephemeral_tool_mount(root: Path, path: Path, *,
                            executor_root: Path = Path('/work')) -> bool:
    """Accept only exact empty tool paths in the marked Chat command sandbox."""
    writable_parents = ('issues', 'iterations', 'openspec/changes',
                        'openspec/specs', 'openspec/archive', 'docs/spec-logs')
    if root != executor_root or os.getenv('MOONBOX_CHAT_TOOL_SANDBOX') != '1' or path not in {
        root / parent / name for parent in writable_parents for name in TOOL_NAMES
    }:
        return False
    if path.is_symlink() or not path.is_dir():
        return False
    try:
        return not any(path.iterdir())
    except OSError:
        return False
