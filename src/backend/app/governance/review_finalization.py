"""Complete stale review projections without inventing an approval or losing evidence."""
import re

import yaml

from app.chat.service import ChatError
from app.governance.candidates import frontmatter
from app.governance.review import review_outcome, validate_review


def finalize_review(before, after, oid, base, action):
    try:
        validate_review(before, after, oid, base, action)
        return after
    except ChatError as error:
        # Document, migration and approval gates precede projection checks.
        if (error.details or {}).get('reason') not in ('registry_target', 'index'):
            raise
    result = dict(after)
    folder = base.split('/')[1]
    target = base.replace('/plan/', '/review/')
    destination = target if f'{target}/review.md' in after else base
    outcome = review_outcome(frontmatter(after[f'{destination}/review.md'])[0])
    registry = f'issues/{folder}/_registry.yaml'
    index = f'issues/{folder}/CHANGELOG.md'
    previous = yaml.safe_load(before[registry])
    current = yaml.safe_load(after[registry])
    old_rows = [row for row in previous['entries'] if row['id'] == oid]
    rows = [row for row in current['entries'] if row['id'] == oid]
    if len(rows) != 1 or len(old_rows) != 1:
        raise ChatError(2604, '评审注册表身份冲突，已保留成果', 409,
                        kind='governance_validation_failed', details={'reason': 'registry_target'})
    wanted = {'status': outcome, 'path': destination,
              'lifecycle_stage': 'review' if destination == target else 'plan'}
    for key, value in wanted.items():
        actual = rows[0].get(key)
        if actual not in (old_rows[0].get(key), value, value + '/' if key == 'path' else value):
            raise ChatError(2604, '评审注册表结论冲突，已保留成果', 409,
                            kind='governance_validation_failed', details={'reason': 'registry_target'})
        rows[0][key] = value
    if current != yaml.safe_load(after[registry]):
        result[registry] = yaml.safe_dump(current, allow_unicode=True, sort_keys=False).encode()
    pattern = re.compile(r'^\|\s*' + re.escape(oid) + r'\s*\|')
    lines = after[index].decode().splitlines(keepends=True)
    old_status = old_rows[0]['status']
    wanted_stage = 'review' if destination == target else 'plan'
    wanted_next = (f'`/sprint-propose --{"bug" if folder == "bugs" else "req"} {oid}`'
                   if outcome == 'approved' else '无')
    for number, line in enumerate(lines):
        if pattern.match(line):
            cells = line.replace(base, destination).split('|')
            cells = [cell.replace(old_status, outcome) if cell.strip() == old_status else cell
                     for cell in cells]
            # Full CHANGELOG rows also carry lifecycle stage and the next action.
            if len(cells) == 12:
                old_line = next((raw for raw in before[index].decode().splitlines()
                                 if pattern.match(raw)), None)
                if old_line is None:
                    raise ChatError(2604, '评审索引原始条目缺失，已保留成果', 409,
                                    kind='governance_validation_failed', details={'reason': 'index'})
                old_cells = old_line.split('|')
                for position, desired in ((5 if folder == 'bugs' else 4, wanted_stage),
                                          (9, wanted_next)):
                    if cells[position].strip() not in (old_cells[position].strip(), desired):
                        raise ChatError(2604, '评审索引结论冲突，已保留成果', 409,
                                        kind='governance_validation_failed', details={'reason': 'index'})
                    cells[position] = f' {desired} '
            lines[number] = '|'.join(cells)
    result[index] = ''.join(lines).encode()
    # Validate the complete result again, including unrelated objects and index rows.
    validate_review(before, result, oid, base, action)
    return result
