"""Lifecycle mirrors: physical directory is authoritative; historical bodies are opaque."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

STAGES = frozenset({'plan', 'review', 'archive'})


@dataclass(frozen=True)
class StageDrift:
    file: Path
    current: str
    target: str
    safe: bool


def stage_documents(issue_dir: Path) -> tuple[str, ...]:
    primary = 'requirement.md' if issue_dir.name.startswith('REQ-') else 'bug.md'
    return ('trace.md', primary, 'capture.md')


def stage_value(text: str) -> str | None:
    match = re.match(r'^---\n(.*?)\n---(?:\n|$)', text, re.DOTALL)
    if not match:
        return None
    values = yaml.safe_load(match.group(1))
    if not isinstance(values, dict) or 'lifecycle_stage' not in values:
        return None
    # Reject duplicate, nested, null and non-scalar stage values rather than guessing.
    lines = re.findall(r'^lifecycle_stage\s*:', match.group(1), re.MULTILINE)
    value = values['lifecycle_stage']
    if len(lines) != 1 or not isinstance(value, str):
        return '<invalid>'
    return value


def scan_stage_drift(issue_dir: Path, target: str | None = None) -> list[StageDrift]:
    target = target or issue_dir.parent.name
    if target not in STAGES:
        return []  # Legacy flat paths have no authoritative physical stage.
    result = []
    for name in stage_documents(issue_dir):
        path = issue_dir / name
        if not path.is_file():
            continue
        try:
            current = stage_value(path.read_text(encoding='utf-8'))
        except yaml.YAMLError:
            current = '<invalid>'
        if current is not None and current != target:
            result.append(StageDrift(path, current, target, current in STAGES))
    return result


def replace_stage(text: str, target: str) -> str:
    if target not in STAGES:
        raise ValueError('invalid target lifecycle_stage')
    current = stage_value(text)
    if current is None or current == target:
        return text
    if current not in STAGES:
        raise ValueError('invalid source lifecycle_stage')
    match = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    assert match
    block = re.sub(r'^(lifecycle_stage\s*:\s*)[^\n]*', lambda m: m[1] + target,
                   match[1], count=1, flags=re.MULTILINE)
    return '---\n' + block + '\n---' + text[match.end():]
