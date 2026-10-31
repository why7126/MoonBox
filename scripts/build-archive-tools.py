#!/usr/bin/env python3
"""Build a new immutable package; never install or replace a deployment."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def build(source, target):
    if target.exists() or target.is_symlink():
        raise ValueError('archive_tool_destination_exists')
    target.mkdir(parents=True)
    files = {}
    for relative in ('scripts', 'src/backend/app', 'rules'):
        for path in sorted((source / relative).rglob('*')):
            if '__pycache__' in path.parts or path.suffix == '.pyc':
                continue
            if path.is_symlink():
                raise ValueError('archive_tool_source_symlink')
            if not path.is_file():
                continue
            allowed = {'.py', '.sh'} if relative == 'scripts' else {'.py'} if relative == 'src/backend/app' else {'.md', '.json', '.yaml', '.yml'}
            if path.suffix not in allowed:
                continue
            name = path.relative_to(source).as_posix()
            destination = target / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)
            destination.chmod(0o555 if path.stat().st_mode & 0o111 else 0o444)
            files[name] = hashlib.sha256(destination.read_bytes()).hexdigest()
    raw = (json.dumps({'schema_version': 1, 'files': files}, sort_keys=True, separators=(',', ':')) + '\n').encode()
    (target / 'manifest.json').write_bytes(raw)
    (target / 'manifest.json').chmod(0o444)
    for path in sorted(target.rglob('*'), reverse=True):
        if path.is_dir(): path.chmod(0o555)
    target.chmod(0o555)
    return hashlib.sha256(raw).hexdigest()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(build(Path(__file__).resolve().parents[1], args.output))
