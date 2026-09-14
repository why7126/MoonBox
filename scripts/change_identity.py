"""Read-only Change identity validation shared by governance entry points."""
from pathlib import Path
import re

import yaml

ID = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*')
ARCHIVE = re.compile(r'\d{4}-\d{2}-\d{2}-(.+)')


def validate(root: Path, new_id: str | None = None) -> list[str]:
    records: dict[str, list[str]] = {}
    errors = []
    for location in ('changes', 'archive'):
        parent = root / 'openspec' / location
        if not parent.is_dir():
            errors.append(f'缺少目录: openspec/{location}')
            continue
        for directory in sorted(parent.iterdir()):
            if not directory.is_dir():
                continue
            relative = directory.relative_to(root).as_posix()
            if directory.is_symlink():
                errors.append(f'Change 目录不能为符号链接: {relative}')
                continue
            cid = directory.name
            if location == 'archive':
                match = ARCHIVE.fullmatch(cid)
                if not match:
                    errors.append(f'归档目录缺少日期前缀: {relative}')
                    continue
                cid = match[1]
            if not ID.fullmatch(cid):
                errors.append(f'Change ID 格式无效: {relative}')
                continue
            records.setdefault(cid, []).append(relative)
            trace = directory / 'trace.md'
            if trace.is_file():
                try:
                    text = trace.read_text(encoding='utf-8')
                    match = re.match(r'^---\s*\n(.*?)\n---(?:\n|$)', text, re.S)
                    metadata = yaml.safe_load(match[1]) if match else {}
                    if metadata is not None and not isinstance(metadata, dict):
                        raise ValueError('Frontmatter must be a mapping')
                    value = (metadata or {}).get('change_id')
                    if value is not None and value != cid:
                        errors.append(f'trace.change_id 与目录不一致: {relative}/trace.md')
                except (OSError, UnicodeError, yaml.YAMLError, ValueError):
                    errors.append(f'trace Frontmatter 无法读取: {relative}/trace.md')
    for cid, paths in sorted(records.items()):
        if len(paths) > 1:
            errors.append(f'Change ID 重复 {cid}: ' + ', '.join(paths))
    if new_id is not None:
        if not ID.fullmatch(new_id):
            errors.append('待创建 Change ID 格式无效')
        elif new_id in records:
            errors.append(f'待创建 Change ID 已占用 {new_id}: ' + ', '.join(records[new_id]))
    return errors
