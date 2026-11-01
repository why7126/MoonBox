"""Pure card metadata projection from an already authorized governance snapshot."""
from __future__ import annotations

import math
import re
from typing import Any

ROOT_STATES = {'unknown', 'hypothesis', 'probable', 'confirmed'}
PLACEHOLDER = re.compile(r'^(?:待(?:填写|补充|分析|完善|确认)|暂无|无|未填写|TBD|TODO|N/?A|[-—.…]+)(?:[。.!！\s]*)$', re.I)


def estimate_metadata(scope: Any, object_id: str, changes: list[str], *, source_issue_id: str | None = None) -> dict:
    """Prefer an explicit object total; never silently sum incomplete partitions."""
    def result(status, value=None):
        return {'estimated_person_days': value, 'estimate_status': status}

    def value(rows):
        values = [row.get('estimated_person_days') for row in rows]
        if any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in values):
            return result('invalid')
        if len(set(values)) != 1:
            return result('conflict')
        return result('available', values[0])

    if not isinstance(scope, list):
        return result('missing')
    rows = [r for r in scope if isinstance(r, dict)]
    if not object_id.startswith(('REQ-', 'BUG-')):
        # A source Issue row with a `change` link is still an Issue estimate.
        parts = [r for r in rows if r.get('id') == object_id or
                 (not r.get('id') and r.get('change') == object_id)]
        if any(r.get('change') not in (None, '', object_id) for r in parts):
            return result('conflict')
        if parts:
            return value(parts)
        # The caller proves unique, authorized ownership using the complete
        # relationship index, including hidden and archived siblings.
        if source_issue_id is None:
            return result('missing')
        totals = [r for r in rows if r.get('id') == source_issue_id]
        if not totals:
            return result('missing')
        if any(r.get('change') != object_id or
               any(r.get(k) not in (None, '', source_issue_id) for k in ('requirement', 'bug'))
               for r in totals):
            return result('conflict')
        metadata = value(totals)
        if metadata['estimate_status'] == 'available':
            metadata['estimate_source_issue_id'] = source_issue_id
        return metadata
    totals = [r for r in rows if r.get('id') == object_id]
    if totals:
        # Contradictory explicit ownership is never an authoritative total.
        if any(r.get(k) not in (None, '', object_id) for r in totals for k in ('requirement', 'bug')):
            return result('conflict')
        return value(totals)
    key = 'requirement' if object_id.startswith('REQ-') else 'bug'
    associated = [r for r in rows if r.get(key) == object_id]
    # Older scope records may omit id but carry an unambiguous object total.
    totals = [r for r in associated if not r.get('id') and not r.get('change')]
    if totals:
        return value(totals)
    if not changes or not associated:
        return result('missing')
    partitions: dict[str, list] = {}
    for row in associated:
        cid = row.get('change') or row.get('id')
        if cid not in changes:
            return result('conflict')
        partitions.setdefault(cid, []).append(row)
    if set(partitions) != set(changes):
        return result('missing')
    numbers = []
    for rows in partitions.values():
        part = value(rows)
        if part['estimate_status'] != 'available':
            return part
        numbers.append(part['estimated_person_days'])
    total = sum(numbers)
    return result('available', total) if math.isfinite(total) else result('invalid')


def root_cause_metadata(text: str, metadata: dict) -> dict:
    body = re.sub(r'\A---\s*\n.*?\n---\s*\n?', '', text, count=1, flags=re.S)
    body = re.sub(r'<!--.*?-->', '', body, flags=re.S)
    section = ''
    content = False
    declarations = []
    for line in body.splitlines():
        heading = re.match(r'^#{1,6}\s+(.+)', line)
        if heading:
            section = heading[1].strip()
            continue
        if section == '根因状态':
            match = re.match(r'\s*(?:status|root_cause_status|状态)\s*[:：]\s*`?([a-z_]+)', line)
            if match:
                declarations.append(match[1])
            continue
        if not re.search(r'根因|分析|证据|原因|假设', section):
            continue
        clean = re.sub(r'^\s*(?:[-*+]\s+(?:\[[ xX]\]\s*)?|\d+[.)]\s*)', '', line).strip(' `')
        label_value = re.sub(r'^.{1,24}[:：]\s*', '', clean).strip(' `*')
        if not clean or clean.startswith('```') or PLACEHOLDER.fullmatch(clean) or PLACEHOLDER.fullmatch(label_value):
            continue
        if clean.startswith('|'):
            cells = [c.strip(' `') for c in clean.strip('|').split('|')]
            if all(not c or re.fullmatch(r'[: -]+', c) for c in cells):
                continue
            if cells[0].lower() in ('id', '编号', '证据', '证据编号'):
                continue
            if not any(c and not PLACEHOLDER.fullmatch(c) and not re.fullmatch(r'E\d+', c, re.I) for c in cells[1:]):
                continue
        if re.fullmatch(r'[（(]?待[^。.!！]*[）)]?[。.]?', clean):
            continue
        content = True
    if not content:
        return {'root_cause_state': 'absent', 'root_cause_reason': None}
    dedicated = metadata.get('root_cause_status')
    generic = metadata.get('status')
    if dedicated is not None and (not isinstance(dedicated, str) or dedicated not in ROOT_STATES):
        return {'root_cause_state': 'pending', 'root_cause_reason': 'invalid'}
    states = ([dedicated] if dedicated is not None else []) + ([generic] if isinstance(generic, str) and generic in ROOT_STATES else []) + declarations
    if any(s not in ROOT_STATES for s in states):
        reason = 'invalid'
    elif len(set(states)) > 1:
        reason = 'conflict'
    elif not states:
        reason = 'missing'
    else:
        return {'root_cause_state': 'confirmed' if states[0] == 'confirmed' else 'pending', 'root_cause_reason': None}
    return {'root_cause_state': 'pending', 'root_cause_reason': reason}
