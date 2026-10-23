"""Read-only object-scoped explanation of narrowly supported rule edits."""
from __future__ import annotations
from typing import Literal
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session
from app.api.v1.admin_auth import require_session_user
from app.chat.service import ChatError
from app.db.session import get_db
from app.schemas.common import ApiResponse
from . import scope
from .replacement_api import object_access
from .replacement_observability import ReplacementRoute
from .replacement_proof import digest
from .rule_change import conflicts

router = APIRouter(prefix='/api/v1/chat/rule-changes', tags=['Governance'], route_class=ReplacementRoute)


class Decision(BaseModel):
    """Retained only to reject old clients without accepting a new approval."""
    model_config = ConfigDict(extra='forbid')
    space_id: str = Field(min_length=1, max_length=64)
    repository_id: str = Field(min_length=1, max_length=64)
    change_id: str = Field(pattern=r'^[a-z0-9][a-z0-9-]{0,100}$')
    content_digest: str = Field(pattern=r'^[a-f0-9]{64}$')
    action: Literal['confirm', 'reject', 'revoke']
    reason: str = Field(default='', max_length=500)
    request_key: str = Field(pattern=r'^[A-Za-z0-9_-]{1,64}$')


def describe(db, project, user, change_id):
    try:
        matches = conflicts(project, change_id)
    except (ValueError, OSError, KeyError, TypeError):
        raise ChatError(2606, '规则差异或历史证据无法安全读取，请重新检查归档', 409,
                        kind='rule_change_unavailable') from None
    if not matches:
        raise ChatError(2606, '当前对象没有需要查看的历史规则修改', 404,
                        kind='rule_change_not_applicable')
    first = matches[0]
    from .archive_admission import change_acceptance
    from .archive_recovery import recovery_admission
    from .controlled_successor import authority
    acceptance = change_acceptance(project.root, change_id, source_root=project.source_root)
    with authority(db, project, user['id']):
        archive = recovery_admission(project.root, change_id, source_root=project.source_root)
    ready = acceptance['ready'] and archive['ready']
    return {'change_id': change_id, 'content_digest': digest(matches),
            'capability': first['key'][0], 'requirement': first['key'][1],
            'before': first['before'], 'after': first['after'],
            'protected_changes': sorted({owner for item in matches for owner in item['protected_changes']}),
            'affected_requirements': [item['key'][1] for item in matches],
            'state': 'ready' if ready else 'blocked',
            'review_reason': None, 'acceptance_ready': acceptance['ready'],
            'acceptance_blockers': acceptance.get('blockers', []) or ([acceptance['reason']] if acceptance.get('reason') else []),
            'archive_ready': ready, 'archive_reason': None if ready else acceptance.get('reason') or archive.get('reason')}


@router.get('', response_model=ApiResponse[dict], summary='查看对象规则修改及检查状态')
def read(space_id: str, repository_id: str, change_id: str, request: Request,
         user=Depends(require_session_user), db: Session=Depends(get_db)):
    request.state.chat_actor = user['id']
    project = scope.authorize(db, user['id'], space_id, repository_id)
    object_access(db, user, project, change_id)
    return ApiResponse(data=describe(db, project, user, change_id))


@router.post('/decision', response_model=ApiResponse[dict], summary='旧规则修改确认入口已停用')
def decide(payload: Decision, request: Request, user=Depends(require_session_user)):
    request.state.chat_actor = user['id']
    raise ChatError(2606, '规则修改无需额外确认；请查看差异并重新检查归档', 409,
                    kind='rule_change_decision_retired')
