"""Lock current authority rows through each controlled file-write boundary."""
from datetime import datetime,timezone
from sqlalchemy import table,column,select
from .scope import authorize


def authorize_write(db,project,actor,*,expected_owner=None,lock=True):
    spaces=table('admin_spaces',*[column(name) for name in ('id','owner_id','status','deleted_at','expires_at')])
    users=table('admin_users',*[column(name) for name in ('id','status','deleted_at')])
    members=table('admin_space_members',*[column(name) for name in ('space_id','user_id','role')])
    def current_row(query):
        return db.execute(query.with_for_update() if lock else query).mappings().first()
    user=current_row(select(users).where(users.c.id==actor))
    space=current_row(select(spaces).where(spaces.c.id==project.space_id))
    if not user or user['status']!='正常' or user['deleted_at'] or not space or space['status']!='ACTIVE' or space['deleted_at']:
        raise ValueError('archive_actor_unavailable')
    if expected_owner is not None and space['owner_id']!=expected_owner:
        raise ValueError('archive_owner_changed')
    if space['expires_at']:
        expiry=datetime.fromisoformat(str(space['expires_at']).replace('Z','+00:00'))
        if expiry.tzinfo is None:expiry=expiry.replace(tzinfo=timezone.utc)
        if expiry<=datetime.now(timezone.utc):raise ValueError('archive_space_expired')
    if actor!=space['owner_id']:
        member=current_row(select(members).where(members.c.space_id==project.space_id,members.c.user_id==actor))
        if not member or member['role'] not in {'管理员','编辑者'}:raise ValueError('archive_actor_not_writer')
    current=authorize(db,actor,project.space_id,project.repository_id,write=True)
    if current.binding_revision!=project.binding_revision:raise ValueError('archive_binding_changed')
    return current
