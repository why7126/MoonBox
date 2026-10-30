"""Fault injection around real SQL/file checkpoints; tool and admission are doubles.

These tests prove orchestration, not independent acceptance or deployed CLI trust.
"""
import json
from pathlib import Path
from types import SimpleNamespace
from contextlib import nullcontext
import pytest
from sqlalchemy import delete, insert, select, text, update
from app.chat.schema import governance_project_locks as locks
from app.chat.service import identity
from app.governance import replacement_coordinator as coordinator
from app.governance import controlled_successor, scope
from app.governance.replacement_schema import TABLES, commits, proposals, activations
from app.governance.replacement_proof import canonical, digest
from app.governance.replacement_inputs import replacement_delivery_hash
from app.governance.archive_recovery import tree_hash
from test_controlled_successor import scene, put


def test_controlled_document_gate_resume_and_replay(orchestration,monkeypatch):
    from app.governance import archive_finalization as gate
    c=orchestration;checks=[];original=gate.require_finalized
    def check(root,change):
        checks.append(change)
        return original(root,change)
    monkeypatch.setattr(gate,'require_finalized',check)
    doc=c.project.root/'issues/bugs/archive/BUG-0001-sample/bug.md'
    put(doc,'---\nstatus: done\n---\nfix-sample\n当前交付状态：pending。')
    with pytest.raises(ValueError,match='archive_finalization_blocked'):c.execute()
    c.db.rollback();doc.write_text('---\nstatus: done\n---\nfix-sample\n')
    assert c.execute()['stage']=='completed'
    assert c.execute()['replayed']
    assert len(checks)==3 and c.calls==['merge','move','sync']
    doc.write_text('---\nstatus: done\n---\nfix-sample\n[证据](missing.md)')
    with pytest.raises(ValueError,match='archive_finalization_blocked'):c.execute()


def test_moved_edge_is_visible_only_to_original_fenced_operation(orchestration):
    c=orchestration;c.fault['at']='sign'
    with pytest.raises(OSError):c.execute()
    operation=c.db.execute(select(commits)).mappings().one()
    folder=list((c.project.root/'openspec/archive').glob('*-fix-sample'))[0]
    args=(c.project.root,'fix-sample',folder,('archive','安全归档'),c.value['before'],c.value['after'])
    with controlled_successor.authority(c.db,c.project,'owner'):
        with pytest.raises(ValueError):controlled_successor.verify(*args)
    with controlled_successor.authority(c.db,c.project,'owner',operation['id'],operation['fence']):
        proof=controlled_successor.verify(*args)
        assert proof['controlled']['claimed'] and not proof['controlled']['historical']
    with controlled_successor.authority(c.db,c.project,'owner',operation['id'],operation['fence']+1):
        with pytest.raises(ValueError,match='stale_archive_executor'):controlled_successor.verify(*args)


@pytest.fixture
def orchestration(tmp_path, monkeypatch):
    value, archived, project, proof, db = scene(tmp_path, monkeypatch)
    project.space_id = 'space'; project.repository_id = 'repo'; project.source_root = None
    trust = controlled_successor.load(tmp_path)
    certificate = json.loads(proof.read_bytes())
    proof.unlink()
    active = tmp_path/'openspec/changes/fix-sample'
    active.parent.mkdir(parents=True)
    archived.rename(active)
    active.joinpath('trace.md').write_text(active.joinpath('trace.md').read_text().replace('status: archived', 'status: applied'))
    assert replacement_delivery_hash(active) == value['delivery_sha256']
    spec = tmp_path/'openspec/specs/archive/spec.md'
    put(spec, '# 归档\n\n### Requirement: 安全归档\n'+value['before']+'\n')
    old_spec = spec.read_bytes()
    put(spec, '# 归档\n\n### Requirement: 安全归档\n'+value['after']+'\n')
    expected = tree_hash(tmp_path/'openspec/specs')
    spec.write_bytes(old_spec)
    for table in TABLES: table.create(db.get_bind(), checkfirst=True)
    locks.create(db.get_bind(), checkfirst=True)
    db.execute(delete(commits))
    db.execute(text('CREATE TABLE admin_spaces (id VARCHAR(64), owner_id VARCHAR(64))'))
    db.execute(text("INSERT INTO admin_spaces VALUES ('space','owner')"))
    receipt = certificate['authorization']
    db.execute(insert(proposals).values(**(identity()|{'id':'proposal'}),scope_key=project.key,
        space_id='space',repository_id='repo',binding_revision=project.binding_revision,change_id='fix-sample',
        digest=digest(value),body=canonical(value).decode(),prepared_by='owner',revision=2,state='approved',
        owner_id='owner',expires_at=receipt['payload']['expires_at'],receipt=canonical(receipt).decode()))
    db.execute(insert(activations).values(**identity(),scope_key=project.key,binding_revision=project.binding_revision,
        policy_version=trust.policy_version,state='active',manifest_hash='d'*64,manifest='{}',revision=1))
    db.commit()
    monkeypatch.setattr(scope,'authorize',lambda *args,**kwargs:project)
    monkeypatch.setattr(coordinator,'load',lambda root:trust)
    monkeypatch.setattr(coordinator,'project_lock',lambda p:nullcontext())
    monkeypatch.setattr(coordinator,'authorize_write',lambda *args,**kwargs:project)
    monkeypatch.setattr(coordinator,'validate',lambda *args:None)
    monkeypatch.setattr(coordinator,'change_acceptance',lambda *args,**kwargs:{'ready':True})
    calls=[]
    fault={'at':None}
    class Driver:
        def __init__(self, project): pass
        def validate_static(self, change): pass
        def recheck_tools(self): pass
        def prepare(self, change): return expected
        def merge_and_move(self, change, *, move_only=False):
            if not move_only:
                calls.append('merge')
                put(spec,'# 归档\n\n### Requirement: 安全归档\n'+value['after']+'\n')
                if fault['at']=='merge': raise OSError('injected interruption')
            calls.append('move');active.rename(archived)
            if fault['at']=='move':raise OSError('injected interruption')
        def finalize(self, change):
            calls.append('sync')
            trace=archived/'trace.md'
            trace.write_text(trace.read_text().replace('status: applied','status: archived'))
            if fault['at']=='sync':raise OSError('injected interruption')
    def sign(payload):
        if fault['at']=='sign':raise OSError('signer unavailable')
        # The historical fixture signed the same immutable commit bindings.
        assert all(certificate['commit']['payload'].get(key)==value for key,value in payload.items()
                   if key not in {'issued_at','expires_at'})
        return certificate['commit']
    def execute():
        return coordinator.execute(db,actor='owner',space_id='space',repository_id='repo',proposal_id='proposal',
            operation_id='operation',expected_revision=2,proposal_digest=digest(value),sign=sign,driver_type=Driver)
    yield SimpleNamespace(db=db,project=project,proof=proof,active=active,archived=archived,
        execute=execute,calls=calls,fault=fault,spec=spec,value=value,driver=Driver)
    db.close();db.get_bind().dispose()


def test_observed_complete_and_replay_never_repeat_merge(orchestration):
    c=orchestration
    assert c.execute()['stage']=='completed'
    assert c.calls==['merge','move','sync']
    assert c.db.scalar(select(proposals.c.state))=='completed'
    assert c.db.scalar(select(locks.c.operation_id)) is None
    assert c.execute()['replayed'] is True
    assert c.calls==['merge','move','sync']


@pytest.mark.parametrize('point',['merge','move','sync','sign'])
def test_restart_observes_original_operation_without_repeating_mutations(orchestration,point):
    c=orchestration;c.fault['at']=point
    with pytest.raises(OSError):c.execute()
    c.db.rollback()
    assert c.db.scalar(select(proposals.c.state))=='claimed'
    assert c.db.scalar(select(locks.c.operation_id))=='operation'
    c.fault['at']=None
    assert c.execute()['stage']=='completed'
    assert c.calls.count('merge')==1 and c.calls.count('move')==1 and c.calls.count('sync')==1
    assert c.db.scalar(select(commits.c.fence))==2


def test_external_change_after_interruption_retains_fence(orchestration):
    c=orchestration;c.fault['at']='move'
    with pytest.raises(OSError):c.execute()
    c.db.rollback();c.fault['at']=None;c.spec.write_text('tampered')
    with pytest.raises(ValueError,match='archive_result_unknown'):c.execute()
    c.db.rollback()
    assert c.db.scalar(select(locks.c.operation_id))=='operation'
    assert 'sync' not in c.calls


def test_independent_signoff_blocks_before_claim(orchestration,monkeypatch):
    c=orchestration
    monkeypatch.setattr(coordinator,'change_acceptance',lambda *args,**kwargs:{'ready':False})
    with pytest.raises(ValueError,match='independent_archive_gate_blocked'):c.execute()
    c.db.rollback()
    assert not c.db.execute(select(commits)).first()
    assert c.calls==[] and c.active.exists()


def test_changed_public_proof_never_gets_commit_receipt(orchestration):
    c=orchestration;c.fault['at']='sign'
    with pytest.raises(OSError):c.execute()
    c.db.rollback();c.fault['at']=None
    record=json.loads(c.proof.read_bytes());record['proposal']['after']='forged'
    c.proof.write_bytes(canonical(record))
    with pytest.raises(ValueError,match='replacement_proof_changed'):c.execute()
    c.db.rollback()
    assert c.db.scalar(select(proposals.c.state))=='claimed'


def test_candidate_preflight_uses_authority_without_writing_proof(orchestration,monkeypatch):
    c=orchestration
    # This orchestration fixture moves a historical sample back to active.
    # Independent evidence freshness has its own real runtime acceptance test.
    monkeypatch.setattr(controlled_successor,'acceptance_binding',lambda *args,**kwargs:c.value['acceptance_sha256'])
    args=(c.project.root,'fix-sample',c.active,('archive','安全归档'),c.value['before'],c.value['after'])
    with controlled_successor.authority(c.db,c.project,'owner'):
        with pytest.raises(ValueError,match='legacy_replacement_candidate_retired'):
            controlled_successor.verify(*args)
    assert not c.proof.exists() and not c.db.execute(select(commits)).first()


def test_candidate_without_online_authority_never_uses_signed_file_alone(orchestration):
    c=orchestration
    with pytest.raises(ValueError,match='replacement_authority_unavailable'):
        controlled_successor.verify(c.project.root,'fix-sample',c.active,('archive','安全归档'),c.value['before'],c.value['after'])
