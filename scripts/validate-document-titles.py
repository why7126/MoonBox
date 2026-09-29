#!/usr/bin/env python3
"""Focused Chinese document title gate; never changes source documents."""
import argparse
import sys
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/backend'))
from app.governance.titles import validate_document, business_title


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='*')
    parser.add_argument('--bug')
    parser.add_argument('--req')
    parser.add_argument('--change')
    args = parser.parse_args()
    paths = [Path(p) for p in args.paths]
    for kind, oid in [('bugs', args.bug), ('requirements', args.req)]:
        if oid:
            matches = [p for p in (ROOT/'issues'/kind).glob('*/'+oid) if p.is_dir()]
            if len(matches) != 1:
                parser.error('Issue 身份缺失或不唯一')
            paths.extend(matches)
    if args.change:
        paths.append(ROOT/'openspec/changes'/args.change)
    if not paths:
        parser.error('请指定本次生成文件或 Issue/Change')
    errors = []
    files = set()
    for p in paths:
        if not p.exists():
            errors.append(f'{p.name}: 文件不存在')
        files.update(p.rglob('*.md') if p.is_dir() else [p])
    for p in sorted(files):
        if p.suffix == '.md':
            errors.extend(f'{p.name}: {e}' for e in validate_document(p.read_text()))
        elif p.name == '_registry.yaml':
            for e in yaml.safe_load(p.read_text()).get('entries', []):
                if not business_title(e.get('title')): errors.append(f"{e.get('id')}: title 无效")
    print('\n'.join(errors) if errors else f'中文标题校验通过：{len(files)} 份文件')
    return bool(errors)

if __name__ == '__main__':
    sys.exit(main())
