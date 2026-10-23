"""Reapproval replaces only authenticated, unclaimed older public receipts."""
import json
import pytest
from sqlalchemy import select,update
from test_replacement_authorization import context,decision
from app.governance.replacement_schema import proposals
from app.governance.replacement_coordinator import prepare_proof
from app.governance.replacement_proof import canonical


def records(context,tmp_path):
    db,project,trust,_=context
    old=decision(context)['receipt'];db.commit()
    decision(context,action='revoke',expected_revision=2,request_key='revoke');db.commit()
    db.execute(update(proposals).values(state='prepared',revision=4,receipt=None,owner_id=None,expires_at=None));db.commit()
    new=decision(context,expected_revision=4,request_key='new')['receipt'];db.commit()
    row=db.execute(select(proposals)).mappings().one()
    value={'schema_version':1,'proposal':{'policy_version':'policy-v1'},'authorization':old,'commit':None}
    path=tmp_path/'proof.json';path.write_bytes(canonical(value))
    return path,value,{**value,'authorization':new},row


def test_reapproval_refresh_keeps_old_immutable_event(context,tmp_path):
    db,project,trust,_=context
    path,old,new,row=records(context,tmp_path)
    prepare_proof(db,path,new,row,trust,project)
    assert json.loads(path.read_bytes())==new
    from app.governance.replacement_schema import events
    assert len(db.execute(select(events)).all())==3


@pytest.mark.parametrize('damage',['signature','commit','claimed','proposal'])
def test_never_overwrites_claimed_forged_or_other_proof(context,tmp_path,damage):
    db,project,trust,_=context
    path,old,new,row=records(context,tmp_path)
    if damage=='signature':old['authorization']['signature']='eA=='
    if damage=='commit':old['commit']={'untrusted':'commit'}
    if damage=='claimed':row={**row,'operation_id':'claimed-operation'}
    if damage=='proposal':old['proposal']['policy_version']='other'
    path.write_bytes(canonical(old));before=path.read_bytes()
    with pytest.raises(ValueError):prepare_proof(db,path,new,row,trust,project)
    assert path.read_bytes()==before


@pytest.mark.parametrize('damage',[None,'journal','archive','binding','forged'])
def test_corrected_candidate_requires_new_approval_and_unclaimed_history(context,tmp_path,damage):
    from sqlalchemy import insert
    from app.chat.service import identity
    from app.governance.replacement_proof import digest
    from app.governance.archive_recovery import journal_path
    db,project,trust,_=context
    project.root=tmp_path
    old_body={'policy_version':'policy-v1','project_id':project.key,'binding_revision':project.binding_revision,
              'successor':'sample','capability':'archive','requirement':'safe','delta_sha256':'1'*64}
    db.execute(update(proposals).values(body=canonical(old_body).decode(),digest=digest(old_body)))
    old_receipt=decision(context,proposal_digest=digest(old_body))['receipt'];db.commit()
    new_body={**old_body,'delta_sha256':'2'*64}
    db.execute(insert(proposals).values(**(identity()|{'id':'corrected'}),scope_key=project.key,space_id='space',
        repository_id='repo',binding_revision=project.binding_revision,change_id='sample',digest=digest(new_body),
        body=canonical(new_body).decode(),prepared_by='owner',revision=1,state='prepared'))
    new_receipt=decision(context,proposal_id='corrected',proposal_digest=digest(new_body),request_key='corrected')['receipt'];db.commit()
    old={'schema_version':1,'proposal':old_body,'authorization':old_receipt,'commit':None}
    new={**old,'proposal':new_body,'authorization':new_receipt}
    row=db.execute(select(proposals).where(proposals.c.id=='corrected')).mappings().one()
    if damage=='journal':
        journal=journal_path(tmp_path,'sample');journal.parent.mkdir(parents=True);journal.write_text('{}')
    if damage=='archive':(tmp_path/'openspec/archive/2026-10-22-sample').mkdir(parents=True)
    if damage=='binding':db.execute(update(proposals).where(proposals.c.id=='proposal').values(binding_revision='x'*64));db.commit()
    if damage=='forged':old['authorization']['signature']='eA=='
    path=tmp_path/'proof.json';path.write_bytes(canonical(old));before=path.read_bytes()
    if damage:
        with pytest.raises(ValueError):prepare_proof(db,path,new,row,trust,project)
        assert path.read_bytes()==before
    else:
        prepare_proof(db,path,new,row,trust,project)
        assert json.loads(path.read_bytes())==new
        from app.governance.replacement_schema import events
        assert len(db.execute(select(events)).all())==2
