"""Prepare only the explicitly selected private local governance directory."""
import os
from pathlib import Path
import sys


def prepare(create=False):
    if os.environ.get('MOONBOX_GOVERNANCE_CAPTURE_MODE', 'disabled') not in ('continuous', 'disabled'):
        raise ValueError('unknown Capture mode')
    root = Path(os.environ['MOONBOX_GOVERNANCE_HOST_STATE_ROOT'])
    if not root.is_absolute(): raise ValueError('absolute directory required')
    for path in [root, *root.parents]:
        if path.is_symlink(): raise ValueError('symlink refused')
    if root.exists() and (not root.is_dir() or root.stat().st_mode & 0o077 or root.stat().st_uid != os.getuid()):
        raise ValueError('private directory requires owner and 0700')
    if create: root.mkdir(mode=0o700, parents=True, exist_ok=True)


if __name__ == '__main__':
    try: prepare(sys.argv[1] == 'prepare');print('治理私有目录检查通过')
    except Exception: raise SystemExit('治理目录配置无效：检查绝对路径、目录属主和0700权限') from None
