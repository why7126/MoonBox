"""Validate bounded review outcomes and explicit stage migrations."""
import difflib
import hashlib
import re

import yaml

from app.chat.service import ChatError
from app.governance.candidates import frontmatter, without
from app.governance.snapshot import digest
from app.governance.titles import validate_document

REVIEW_REASONS = {
    'outcome_conflict', 'outcome', 'identity', 'scope', 'review', 'migration_set',
    'destination_exists', 'document_size', 'document_title', 'acceptance_scope',
    'unrelated_document_edit', 'state', 'stage', 'trace_scope', 'lifecycle_scope',
    'lifecycle', 'approval', 'primary_scope', 'root_cause', 'registry',
    'registry_ids', 'other_object', 'registry_target', 'registry_scope', 'index',
}


def review_outcome(metadata):
    status, result = metadata.get('status'), metadata.get('result')
    if 'status' in metadata and 'result' in metadata and status != result:
        raise ValueError('outcome_conflict')
    value = status if 'status' in metadata else result
    if value not in ('approved', 'rejected', 'deferred'):
        raise ValueError('outcome')
    return value


def allowed_paths(base, files):
    target = base.replace('/plan/', '/review/')
    names = {p[len(base) + 1:] for p in files if p.startswith(base + '/')}
    names.add('review.md')
    folder = base.split('/')[1]
    return {f'{prefix}/{name}' for prefix in (base, target) for name in names} | {
        f'issues/{folder}/_registry.yaml', f'issues/{folder}/CHANGELOG.md'}


def validate_review(before, after, oid, base, action):
    try:
        bug = action == 'bug-review'
        folder, field, primary, prefix = ('bugs', 'bug_id', 'bug.md', 'BUG') if bug else (
            'requirements', 'requirement_id', 'requirement.md', 'REQ')
        if not re.fullmatch(rf'{prefix}-\d{{4}}-[a-z0-9-]+', oid) or base != f'issues/{folder}/plan/{oid}':
            raise ValueError('identity')
        changed = {p for p in before.keys() | after.keys() if before.get(p) != after.get(p)}
        if not changed <= allowed_paths(base, before):
            raise ValueError('scope')
        old, _ = frontmatter(before[f'{base}/trace.md'])
        target = base.replace('/plan/', '/review/')
        migrated = f'{target}/review.md' in after
        destination = target if migrated else base
        review, review_body = frontmatter(after[f'{destination}/review.md'])
        result = review_outcome(review)
        if result not in ('approved', 'rejected', 'deferred') or migrated != (result == 'approved'):
            raise ValueError('outcome')
        if old.get('status') != 'pending_review' or review.get(field) != oid or len(review_body.strip()) < 20:
            raise ValueError('review')
        original = {p[len(base) + 1:] for p in before if p.startswith(base + '/')}
        actual = {p[len(destination) + 1:] for p in after if p.startswith(destination + '/')}
        if actual != original | {'review.md'} or (migrated and any(p.startswith(base + '/') for p in after)):
            raise ValueError('migration_set')
        if any(p.startswith(target + '/') for p in before):
            raise ValueError('destination_exists')
        for name in actual:
            body = after[f'{destination}/{name}']
            if not body.strip() or len(body) > 1024 * 1024:
                raise ValueError('document_size')
            if name.endswith('.md') and validate_document(body.decode()):
                raise ValueError('document_title')
            if name not in ('review.md', 'trace.md', primary):
                expected = before[f'{base}/{name}'].replace(base.encode(), destination.encode())
                if name == 'acceptance.md':
                    old_meta, old_text = frontmatter(expected)
                    new_meta, new_text = frontmatter(body)
                    event = 'bug' if bug else 'req'
                    synced_text = old_text.replace(f'source_event: {event}.complete', f'source_event: {event}.review')
                    # Workflow Sync terminates its generated block with a blank line.
                    if without(old_meta, {'updated_at'}) != without(new_meta, {'updated_at'}) or new_text.rstrip('\n') not in (old_text.rstrip('\n'), synced_text.rstrip('\n')):
                        raise ValueError('acceptance_scope')
                    continue
                if body != expected:
                    raise ValueError('unrelated_document_edit')
        new, _ = frontmatter(after[f'{destination}/trace.md'])
        doc, _ = frontmatter(after[f'{destination}/{primary}'])
        old_doc, _ = frontmatter(before[f'{base}/{primary}'])
        stage = 'review' if migrated else 'plan'
        for data in (new, doc):
            identity_fields = (field, 'req_id') if data is new and not bug else (field,)
            identities = [data[key] for key in identity_fields if key in data]
            if not identities or any(value != oid for value in identities) or data.get('status') != result:
                raise ValueError('state')
        if new.get('lifecycle_stage') != stage:
            raise ValueError('stage')
        normalized_old, _ = frontmatter(before[f'{base}/trace.md'].replace(base.encode(), destination.encode()))
        mutable = {'status', 'updated_at', 'lifecycle', 'lifecycle_stage'}
        if without(normalized_old, mutable) != without(new, mutable):
            raise ValueError('trace_scope')
        old_life, new_life = old.get('lifecycle', {}), new.get('lifecycle', {})
        if without(old_life, {'reviewed', 'approved'}) != without(new_life, {'reviewed', 'approved'}):
            raise ValueError('lifecycle_scope')
        if not new_life.get('reviewed') or (result == 'approved' and not new_life.get('approved')):
            raise ValueError('lifecycle')
        if result != 'approved' and new_life.get('approved') != old_life.get('approved'):
            raise ValueError('approval')
        normalized_doc, _ = frontmatter(before[f'{base}/{primary}'].replace(base.encode(), destination.encode()))
        if without(normalized_doc, mutable) != without(doc, mutable):
            raise ValueError('primary_scope')
        if bug and result == 'approved':
            root, _ = frontmatter(after[f'{destination}/root-cause.md'])
            if root.get('status') != 'confirmed':
                raise ValueError('root_cause')
        registry, index = f'issues/{folder}/_registry.yaml', f'issues/{folder}/CHANGELOG.md'
        a, b = yaml.safe_load(before[registry]), yaml.safe_load(after[registry])
        if without(a, {'updated_at', 'entries'}) != without(b, {'updated_at', 'entries'}):
            raise ValueError('registry')
        if [e['id'] for e in a['entries']] != [e['id'] for e in b['entries']]:
            raise ValueError('registry_ids')
        for previous, following in zip(a['entries'], b['entries']):
            if previous['id'] != oid:
                if previous != following:
                    raise ValueError('other_object')
                continue
            if (following.get('status') != result or following.get('path', '').rstrip('/') != destination
                    or following.get('lifecycle_stage') != stage or following.get('title') != old_doc.get('title')):
                raise ValueError('registry_target')
            if without(previous, {'updated_at', 'status', 'path', 'lifecycle_stage'}) != without(
                    following, {'updated_at', 'status', 'path', 'lifecycle_stage'}):
                raise ValueError('registry_scope')
        def parts(body):
            meta, text = frontmatter(body)
            rows, rest = [], []
            for line in text.splitlines():
                (rows if re.match(r'^\|\s*' + re.escape(oid) + r'\s*\|', line) else rest).append(line)
            return without(meta, {'updated_at'}), rest, rows
        a, b = parts(before[index]), parts(after[index])
        if (a[:2] != b[:2] or len(a[2]) != 1 or len(b[2]) != 1 or destination not in b[2][0]
                or result not in [cell.strip() for cell in b[2][0].split('|')]):
            raise ValueError('index')
        cells = [cell.strip() for cell in b[2][0].strip().strip('|').split('|')]
        if len(cells) == 10:
            expected_next = (f'`/sprint-propose --{"bug" if bug else "req"} {oid}`'
                             if result == 'approved' else '无')
            if cells[4 if bug else 3] != stage or cells[8] != expected_next:
                raise ValueError('index')
        files = []
        manifest = {}
        for path in sorted(changed):
            old_body, new_body = before.get(path), after.get(path)
            files.append({'path': path,
                'before_sha256': hashlib.sha256(old_body).hexdigest() if old_body is not None else None,
                'after_sha256': hashlib.sha256(new_body).hexdigest() if new_body is not None else None,
                'diff': ''.join(difflib.unified_diff((old_body or b'').decode().splitlines(True),
                    (new_body or b'').decode().splitlines(True), fromfile=path, tofile=path))})
            # Explicit tombstones must hash differently from empty files.
            manifest[path] = b'deleted' if new_body is None else b'file\0' + new_body
        return {'files': files, 'manifest_hash': digest(manifest)}
    except (ValueError, KeyError, TypeError, UnicodeError, yaml.YAMLError) as error:
        reason = str(error) if isinstance(error, ValueError) and str(error) in REVIEW_REASONS else 'document_format'
        raise ChatError(2604, '评审成果未通过结论、迁移范围或事实源一致性校验，已保留成果',
                        409, kind='governance_validation_failed', details={'reason': reason}) from None
