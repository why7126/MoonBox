"""Resolve an authenticated object to the common trusted archive coordinators."""
import json
import re
from uuid import uuid5,NAMESPACE_URL
from sqlalchemy import select
from . import scope,replacement_signer
from .reader import ProjectReader
from .archive_admission import linked_changes
from .candidates import frontmatter
from .replacement_schema import proposals,activations,archive_operations
from .replacement_proof import parse
from .replacement_inputs import validate
from .replacement_trust import load
from .controlled_successor import authority


def changes_for_object(db,project,actor,object_id):
    reader=ProjectReader(db,actor,project);snapshot=reader.snapshot()
    if object_id.startswith(('REQ-','BUG-')):
        entry=reader.authorize_object(snapshot,object_id,write=True)[0]
        trace,_=frontmatter(snapshot.files[entry['path'].rstrip('/')+'/trace.md'])
        changes=linked_changes(entry,trace)
    else:
        reader.authorize_object(snapshot,object_id,change=True,root=project.root,write=True)
        changes=[object_id]
    if not changes:raise ValueError('archive_change_missing')
    return sorted(set(changes))


def execute_change(db,project,actor,change,*,request_id=None):
    rows=list(db.execute(select(proposals).where(proposals.c.scope_key==project.key,
        proposals.c.change_id==change,proposals.c.state.in_(('claimed','completed')))).mappings())
    candidates=[]
    for row in rows:
        if row['state'] in {'claimed','completed'}:
            candidates.append(row)
        else:
            try:validate(project,parse(row['body'].encode()),load(project.root))
            except (ValueError,OSError,KeyError,TypeError):continue
            candidates.append(row)
    if len(candidates)>1:raise ValueError('replacement_candidate_ambiguous')
    if candidates:
        row=candidates[0]
        receipt=json.loads(row['receipt'])
        operation_id=row['operation_id'] or str(uuid5(NAMESPACE_URL,'controlled-command:'+project.key+':'+row['digest']))
        from .replacement_coordinator import execute
        return execute(db,actor=actor,space_id=project.space_id,repository_id=project.repository_id,
            proposal_id=row['id'],operation_id=operation_id,expected_revision=receipt['payload']['revision'],
            proposal_digest=row['digest'],sign=replacement_signer.sign,request_id=request_id)
    existing=db.execute(select(archive_operations).where(archive_operations.c.scope_key==project.key,
        archive_operations.c.change_id==change)).mappings().first()
    operation_id=existing['id'] if existing else str(uuid5(NAMESPACE_URL,'archive-command:'+project.key+':'+project.binding_revision+':'+change))
    from .archive_coordinator import execute
    return execute(db,actor=actor,space_id=project.space_id,repository_id=project.repository_id,
        change=change,operation_id=operation_id)


def execute_object(db,*,actor,space_id,repository_id,object_id,request_id=None):
    project=scope.authorize(db,actor,space_id,repository_id,write=True)
    if re.fullmatch(r'sprint-\d{3}',object_id):
        from app.chat.relations import _authorize_object
        _authorize_object(db,actor,project.space_id,project.repository_id,object_id)
        from .sprint_archive_coordinator import execute
        operation_id=str(uuid5(NAMESPACE_URL,'sprint-close:'+project.key+':'+project.binding_revision+':'+object_id))
        result=execute(db,actor=actor,space_id=space_id,repository_id=repository_id,sprint=object_id,operation_id=operation_id)
        return {'stage':'completed','operations':[result]}
    with authority(db,project,actor):
        changes=changes_for_object(db,project,actor,object_id)
    results=[]
    for change in changes:
        results.append(execute_change(db,project,actor,change,request_id=request_id))
    return {'stage':'completed','operations':results}
