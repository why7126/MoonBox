"""Fail-closed write eligibility from current server-side space and governance facts."""
import re
import yaml
from sqlalchemy import select, text
from app.chat import service
from app.chat.schema import relations
from app.chat.relations import resolve_object, _entries, _read_file


def write_allowed(db, actor, parent):
    service.authorize_space(db,actor,parent['space_id'])
    row=db.execute(text('''SELECT s.owner_id,m.role FROM admin_spaces s LEFT JOIN admin_space_members m
        ON m.space_id=s.id AND m.user_id=:actor WHERE s.id=:space'''),{'actor':actor,'space':parent['space_id']}).first()
    if not row or (row.owner_id!=actor and row.role not in ('管理员','编辑者')):return False
    oid=db.scalar(select(relations.c.object_id).where(relations.c.conversation_id==parent['id'],relations.c.role=='primary'))
    if not oid:return False
    # Captured requirements may edit only their isolated prepared workspace.
    # The trusted collector still validates the full workspace and exact four-file result.
    from app.governance.preparation import for_conversation
    candidate=for_conversation(db,parent['id'])
    if candidate:
        try:
            from app.governance import scope
            project=scope.authorize(db,actor,parent['space_id'],parent['repository_id'],write=True)
            return (candidate['actor_id']==actor and candidate['object_id']==oid
                and candidate['action']=='req-generate' and candidate['state']=='running'
                and candidate['binding_revision']==project.binding_revision
                and scope.visible(db,actor,project,oid))
        except service.ChatError:return False
    try:
        item=resolve_object(db,actor,parent['space_id'],parent['repository_id'],oid)
        entry=next(row for row in _entries(item['root']) if row['id']==item['id'])
        if entry.get('status')!='in_sprint':return False
        change=entry.get('related_change');sprint=entry.get('iteration')
        if not isinstance(change,str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,100}',change):return False
        if not isinstance(sprint,str) or not re.fullmatch(r'sprint-\d{3}',sprint):return False
        source=_read_file(item['root'],f'openspec/changes/{change}/trace.md')
        if not source.startswith('---\n'):return False
        trace=yaml.safe_load(source.split('---',2)[1])
        plan=yaml.safe_load(_read_file(item['root'],f'iterations/change/{sprint}/sprint.yaml'))
        if not isinstance(trace,dict) or not isinstance(plan,dict):return False
        return (trace.get('status') in ('proposed','in_progress') and trace.get('sprint')==sprint
                and (trace.get('requirement')==oid or trace.get('bug')==oid)
                and change in plan.get('changes',[]) and oid in plan.get('requirements',[])+plan.get('bugs',[]))
    except (service.ChatError,ValueError,TypeError,KeyError,IndexError,StopIteration,yaml.YAMLError):return False
