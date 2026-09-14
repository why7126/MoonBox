"""Resolve opaque project identities; never accept client filesystem paths."""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from sqlalchemy import select, text
from app.chat.schema import object_access
from app.chat.settings import repository_binding, repository_catalog
from app.chat.workspace import trusted_directory, WorkspaceError
from app.chat.service import ChatError


@dataclass(frozen=True)
class ProjectScope:
    space_id: str
    repository_id: str
    root: Path
    binding_revision: str
    readonly: bool

    @property
    def key(self):
        return hashlib.sha256(f'{self.space_id}\0{self.repository_id}'.encode()).hexdigest()


def authorize(db, actor, space_id, repository_id, *, write=False):
    row = db.execute(text('''SELECT s.status, s.expires_at FROM admin_spaces s
      WHERE s.id=:space AND s.deleted_at IS NULL AND s.status IN ('ACTIVE','FROZEN')
      AND (s.owner_id=:actor OR EXISTS (SELECT 1 FROM admin_space_members m
      WHERE m.space_id=s.id AND m.user_id=:actor))'''), {'space':space_id,'actor':actor}).first()
    if not row:
        raise ChatError(2601, '项目不存在或无权访问', 403)
    if row.expires_at:
        try:
            expiry = datetime.fromisoformat(str(row.expires_at).replace('Z','+00:00'))
            if expiry.tzinfo is None: expiry = expiry.replace(tzinfo=timezone.utc)
            if expiry <= datetime.now(timezone.utc): raise ValueError()
        except ValueError: raise ChatError(2601, '空间已到期或有效期不可确认', 403)
    if write and row.status != 'ACTIVE':
        raise ChatError(2601, '当前空间只读', 403)
    writable=db.scalar(text("""SELECT s.id FROM admin_spaces s WHERE s.id=:space
          AND (s.owner_id=:actor OR EXISTS (SELECT 1 FROM admin_space_members m
          WHERE m.space_id=s.id AND m.user_id=:actor AND m.role IN ('管理员','编辑者')))"""), {'space':space_id,'actor':actor})
    if write and not writable: raise ChatError(2601, '当前成员仅有项目读取权限', 403)
    binding = repository_binding(repository_id, space_id)
    if not binding:
        raise ChatError(2602, '项目尚未连接治理目录', 503)
    try:
        root = trusted_directory(binding['governance_root'])
    except (WorkspaceError, KeyError):
        raise ChatError(2602, '项目治理目录不可用', 503)
    revision = hashlib.sha256(json.dumps(binding, sort_keys=True).encode()).hexdigest()
    return ProjectScope(space_id, repository_id, root, revision, row.status != 'ACTIVE' or not writable)


def visible(db, actor, scope, full_id):
    grants = db.execute(select(object_access).where(object_access.c.space_id == scope.space_id,
        object_access.c.repository_id == scope.repository_id, object_access.c.object_id == full_id)).mappings().all()
    return not grants or any(row['user_id'] == actor and row['can_read'] for row in grants)


def projects(db, actor):
    items=[]
    for entry in repository_catalog():
        try:
            scope = authorize(db, actor, entry['space_id'], entry['id'])
        except ChatError as error:
            if error.status == 403: continue
            # Unavailable roots remain selectable for a currently authorized member.
            # authorize checks membership before revealing binding availability.
            items.append({'space_id':entry['space_id'], 'repository_id':entry['id'],
                          'status':'unavailable','readonly':True})
        else:
            items.append({'space_id':scope.space_id,'repository_id':scope.repository_id,
                          'status':'connected','readonly':scope.readonly})
    return items
