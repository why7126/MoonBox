#!/usr/bin/env python3
"""Read-only route inspection/launch; operation authorization stays in archive entry."""
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/backend'))
from app.governance.archive_tools import selected


def main():
    package = selected()
    if package and os.environ.get('MOONBOX_ARCHIVE_ROUTED') == '1' and Path(__file__).resolve().parent != package.scripts:
        raise ValueError('archive_tool_entry_mismatch')
    if sys.argv[1:] == ['--check']:
        print(package.digest if package else 'legacy')
        return 0
    if package is None:
        return 0
    if len(sys.argv) < 3 or sys.argv[1] != '--launch':
        raise ValueError('archive_tool_entry_invalid')
    package.verify()
    environment = dict(os.environ, MOONBOX_ARCHIVE_ROUTED='1', PYTHONDONTWRITEBYTECODE='1',
                       PYTHONPATH=str(package.root / 'src/backend'))
    return subprocess.run(['bash', str(package.scripts / 'archive-change.sh'), *sys.argv[2:]],
                          env=environment).returncode


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except ValueError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
