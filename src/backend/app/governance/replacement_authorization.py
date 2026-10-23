"""Transactional owner decisions. Event insert and state CAS commit together.

The API supplies an authenticated session and a deployment signing service;
worker-generated actor strings are never accepted as human authentication.
"""
from datetime import datetime, timedelta, timezone
import json
from sqlalchemy import insert, select, update, text
from .replacement_schema import proposals, events, activations
from .replacement_proof import canonical, digest
from app.chat.service import identity, ChatError
from . import scope


def require_owner(db, user, project):
    if not user.get('session_id'):
        raise ChatError(2601, '此操作需要空间所有者登录确认', 403)
    # Revalidate session at the decision boundary, not merely at route entry.
    active = db.execute(text('''SELECT s.user_id, s.expires_at, s.revoked_at FROM admin_sessions s
        JOIN admin_users u ON u.id=s.user_id
        WHERE s.id=:id AND u.status='正常' AND u.deleted_at IS NULL'''),
                        {'id': user['session_id']}).mappings().first()
    now = datetime.now(timezone.utc)
    if not active or active['user_id'] != user['id'] or active['revoked_at']:
        raise ChatError(2601, '登录态已失效', 403)
    expiry = datetime.fromisoformat(str(active['expires_at']).replace('Z', '+00:00'))
    if expiry.tzinfo is None: expiry = expiry.replace(tzinfo=timezone.utc)
    if expiry <= now:
        raise ChatError(2601, '登录态已失效', 403)
    current = scope.authorize(db, user['id'], project.space_id, project.repository_id, write=True)
    owner = db.scalar(text('SELECT owner_id FROM admin_spaces WHERE id=:space'), {'space': project.space_id})
    if owner != user['id'] or current.binding_revision != project.binding_revision:
        raise ChatError(2601, '仅当前空间所有者可批准，项目绑定必须保持一致', 403)
    from .replacement_permissions import authorize_write
    try:
        authorize_write(db,project,user['id'],expected_owner=user['id'])
    except ValueError:
        raise ChatError(2601,'当前所有者权限已变化，请重新读取',403) from None
    return owner


def decide(db, *, project, proposal_id, actor_id, action, expected_revision, proposal_digest,
           request_key, sign, trust, reason='', now=None):
    """Called only after authenticated owner authorization; no internal commit.

    Caller commits once; any signing/CAS/audit failure rolls back the decision.
    """
    if action not in {'approve', 'reject', 'revoke'} or (action == 'reject' and not reason.strip()):
        raise ValueError('invalid_decision')
    request_hash = digest({'id': proposal_id, 'actor': actor_id, 'action': action,
                           'revision': expected_revision, 'digest': proposal_digest, 'reason': reason})
    previous = db.execute(select(events).where(events.c.scope_key == project.key,
                                               events.c.request_key == request_key)).mappings().first()
    if previous:
        if previous['request_hash'] != request_hash:
            raise ChatError(2606, '幂等标识已用于其他内容', 409)
        return {'revision': previous['revision'], 'receipt': json.loads(previous['receipt']), 'replayed': True}
    row = db.execute(select(proposals).where(proposals.c.id == proposal_id,
        proposals.c.scope_key == project.key)).mappings().first()
    if not row:
        raise ChatError(2601, '提案不存在或无权访问', 404)
    if row['state'] in {'claimed', 'completed'}:
        raise ChatError(2606, '归档操作已领取，请检查原操作；撤销不能回滚已开始的归档', 409, kind='operation_started')
    allowed = {'approve': {'prepared'}, 'reject': {'prepared'}, 'revoke': {'approved'}}[action]
    if row['revision'] != expected_revision or row['digest'] != proposal_digest or row['state'] not in allowed:
        raise ChatError(2606, '提案版本或状态已变化，请重新读取', 409)
    if row['binding_revision'] != project.binding_revision:
        raise ChatError(2606, '项目绑定已变化', 409)
    if action == 'approve':
        policy = db.execute(select(activations).where(activations.c.scope_key == project.key)).mappings().first()
        if (not policy or policy['state'] != 'active' or policy['policy_version'] != trust.policy_version
                or policy['binding_revision'] != project.binding_revision):
            raise ValueError('policy_not_active')
    current = now or datetime.now(timezone.utc)
    issued = current.isoformat(timespec='seconds')
    expires = (current + timedelta(hours=24)).isoformat(timespec='seconds')
    bindings = {'project_id': project.key, 'binding_revision': project.binding_revision,
                'proposal_id': proposal_id, 'proposal_digest': proposal_digest,
                'revision': expected_revision + 1, 'actor_id': actor_id,
                'policy_version': trust.policy_version, 'release_digest': trust.release_digest}
    payload = {**bindings, 'schema_version': 1, 'purpose': 'replacement.' + action,
               'issued_at': issued, 'expires_at': expires}
    receipt = sign(payload)
    trust.verify(receipt, purpose=payload['purpose'], bindings=bindings, now=current)
    state = {'approve': 'approved', 'reject': 'rejected', 'revoke': 'revoked'}[action]
    changed = db.execute(update(proposals).where(proposals.c.id == proposal_id,
        proposals.c.revision == expected_revision, proposals.c.state == row['state']).values(
            revision=expected_revision+1, state=state, owner_id=actor_id, expires_at=expires,
            receipt=canonical(receipt).decode(), updated_at=issued)).rowcount
    if changed != 1:
        raise ChatError(2606, '提案状态发生并发变化，请重新读取', 409)
    db.execute(insert(events).values(**identity(), scope_key=project.key, proposal_id=proposal_id,
        actor_id=actor_id, purpose=payload['purpose'], request_key=request_key,
        request_hash=request_hash, revision=expected_revision+1, receipt=canonical(receipt).decode()))
    return {'revision': expected_revision+1, 'receipt': receipt, 'replayed': False}
