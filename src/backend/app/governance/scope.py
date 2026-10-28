"""Resolve opaque project identities; never accept client filesystem paths."""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from sqlalchemy import select, text, func, case
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
    source_root: Path | None = None
    source_root_unavailable: bool = False

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
    source_root = None
    source_root_unavailable = False
    if isinstance(binding.get('source_root'), str) and binding.get('source_root'):
        try:
            source_root = trusted_directory(binding['source_root'])
        except WorkspaceError:
            source_root_unavailable = True
    revision = hashlib.sha256(json.dumps(binding, sort_keys=True).encode()).hexdigest()
    return ProjectScope(space_id, repository_id, root, revision, row.status != 'ACTIVE' or not writable,
                        source_root, source_root_unavailable)


def visible(db, actor, scope, full_id):
    grants = db.execute(select(object_access).where(object_access.c.space_id == scope.space_id,
        object_access.c.repository_id == scope.repository_id, object_access.c.object_id == full_id)).mappings().all()
    return not grants or any(row['user_id'] == actor and row['can_read'] for row in grants)


class RequestVisibility:
    """Batch one request's ACL reads, then reject changed permissions on return."""
    def __init__(self, db, actor, project):
        self.actor, self.project = actor, project
        self.permissions = self._read(db)

    def _read(self, db):
        grant = case(((object_access.c.user_id == self.actor) & (object_access.c.can_read != 0), 1), else_=0)
        return dict(db.execute(select(object_access.c.object_id, func.max(grant)).where(
            object_access.c.space_id == self.project.space_id,
            object_access.c.repository_id == self.project.repository_id).group_by(object_access.c.object_id)).all())

    def visible(self, oid):
        return bool(self.permissions.get(oid, True))

    def assert_current(self, db):
        # The reader commits before this check so MySQL repeatable-read cannot
        # hide a revocation. This object is never retained across requests.
        current = authorize(db, self.actor, self.project.space_id, self.project.repository_id)
        if (current.binding_revision != self.project.binding_revision
                or current.readonly != self.project.readonly):
            raise ChatError(2606, '项目绑定或权限已变化，请重新读取', 409)
        if self._read(db) != self.permissions:
            raise ChatError(2601, '对象访问权限已变化，请重新读取', 403)


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
