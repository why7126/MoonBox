"""Bootstrap orchestration failure windows, with real crypto/SQL and file effects.

Tool execution, input classification and independent signoff are isolated doubles.
"""
import base64
import hashlib
import json
from datetime import datetime,timedelta,timezone
from pathlib import Path
import pytest
from sqlalchemy import select,update
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from test_replacement_coordinator import orchestration
from app.governance import replacement_bootstrap_executor as executor,controlled_successor
from app.governance.replacement_bootstrap import Installation
from app.governance.replacement_proof import PROTECTED,canonical,digest
from app.governance.replacement_schema import activations
from app.governance.replacement_trust import Trust
from app.governance.archive_recovery import journal_path
from app.chat.schema import governance_project_locks as locks


def test_bootstrap_document_gate_resume_and_replay(bootstrap,monkeypatch):
    from app.governance import archive_finalization as gate
    c=bootstrap;checks=[];original=gate.require_finalized
    def check(root,change):
        checks.append(change)
        return original(root,change)
    monkeypatch.setattr(gate,'require_finalized',check)
    doc=c.project.root/'issues/bugs/archive/BUG-0001-sample/bug.md'
    doc.parent.mkdir(parents=True)
    doc.write_text('---\nstatus: done\n---\nfix-sample\n当前交付状态：pending。')
    with pytest.raises(ValueError,match='archive_finalization_blocked'):c.execute()
    c.db.rollback();doc.write_text('---\nstatus: done\n---\nfix-sample\n')
    assert c.execute()['state']=='active'
    assert c.execute()['state']=='active'
    assert len(checks)==3 and c.calls==['merge','move','sync']
    doc.write_text('---\nstatus: done\n---\nfix-sample\n[证据](missing.md)')
    with pytest.raises(ValueError,match='archive_finalization_blocked'):c.execute()


@pytest.fixture
def bootstrap(orchestration,monkeypatch):
    c=orchestration;value=c.value
    keys={name:Ed25519PrivateKey.generate() for name in ('ops','owner')}
    public={name:base64.b64encode(key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)).decode() for name,key in keys.items()}
    trust=Trust(public,frozenset(),{},'policy-v1','f'*64,{'bootstrap.ops':['ops'],'bootstrap.owner':['owner'],'bootstrap.commit':['owner']})
    journal=json.loads(journal_path(c.project.root,'fix-sample').read_bytes())
    manifest=Installation(schema_version=1,kind='policy_installation',project_id=c.project.key,
        binding_revision=c.project.binding_revision,mechanism_change='fix-sample',from_policy='legacy-v1',to_policy='policy-v1',
        release_digest='f'*64,verifier_digest='d'*64,delta_digest=value['delta_sha256'],acceptance_digest=value['acceptance_sha256'],
        delivery_digest=value['delivery_sha256'],baseline_digest=journal['baseline_spec_hash'],expected_digest=journal['expected_spec_hash'],
        protected_obligations=sorted(PROTECTED),operation_id='install-operation',transitions=[{'capability':'archive',
            'requirement':'安全归档','before_sha256':hashlib.sha256(value['before'].encode()).hexdigest(),
            'after_sha256':hashlib.sha256(value['after'].encode()).hexdigest()}])
    stamp=datetime.now(timezone.utc).replace(microsecond=0)
    def receipt(payload,key='owner'):
        payload={**payload,'schema_version':1,'issued_at':stamp.isoformat(),'expires_at':(stamp+timedelta(hours=24)).isoformat()}
        return {'key_id':key,'payload':payload,'signature':base64.b64encode(keys[key].sign(canonical(payload))).decode()}
    bindings={'actor_id':'owner','project_id':c.project.key,'binding_revision':c.project.binding_revision,
        'installation_digest':digest(manifest.model_dump()),'release_digest':'f'*64,'operation_id':'install-operation'}
    ops=receipt({**bindings,'purpose':'bootstrap.ops'},'ops');owner=receipt({**bindings,'purpose':'bootstrap.owner'})
    c.db.execute(update(activations).values(state='authorized',revision=2,operation_id='install-operation',
        manifest_hash=digest(manifest.model_dump()),manifest=canonical(manifest.model_dump()).decode(),
        ops_receipt=canonical(ops).decode(),owner_receipt=canonical(owner).decode()));c.db.commit()
    monkeypatch.setattr(executor,'load',lambda root:trust)
    monkeypatch.setattr(controlled_successor,'load',lambda root:trust)
    monkeypatch.setattr(executor,'project_lock',lambda project:__import__('contextlib').nullcontext())
    monkeypatch.setattr(executor,'authorize_write',lambda *args,**kwargs:c.project)
    monkeypatch.setattr(executor,'inputs',lambda *args:None)
    monkeypatch.setattr(executor,'change_acceptance',lambda *args,**kwargs:{'ready':True})
    def sign(payload):
        if c.fault['at']=='sign':raise OSError('signer unavailable')
        return receipt(payload)
    def run():return executor.execute(c.db,actor='owner',space_id='space',repository_id='repo',
        manifest_hash=digest(manifest.model_dump()),sign=sign,driver_type=c.driver)
    c.execute=run
    return c


def test_bootstrap_publishes_active_after_committed_observation(bootstrap):
    c=bootstrap
    assert c.execute()['state']=='active'
    assert c.db.scalar(select(activations.c.stage))=='completed'
    assert c.db.scalar(select(locks.c.operation_id)) is None
    assert c.execute()['state']=='active'
    assert c.calls==['merge','move','sync']


@pytest.mark.parametrize('point',['merge','move','sync','sign'])
def test_bootstrap_resume_never_activates_early_or_replays_merge(bootstrap,point):
    c=bootstrap;c.fault['at']=point
    with pytest.raises(OSError):c.execute()
    c.db.rollback()
    assert c.db.scalar(select(activations.c.state))=='activating'
    c.fault['at']=None
    assert c.execute()['state']=='active'
    assert c.calls==['merge','move','sync']
    assert c.db.scalar(select(activations.c.fence))==2


def test_bootstrap_changed_commit_proof_blocks_active(bootstrap):
    c=bootstrap;c.fault['at']='sign'
    with pytest.raises(OSError):c.execute()
    c.db.rollback();c.fault['at']=None
    record=json.loads(c.proof.read_bytes());record['owner_receipt']['signature']='eA=='
    c.proof.write_bytes(canonical(record))
    with pytest.raises(ValueError,match='bootstrap_proof_changed'):c.execute()
    c.db.rollback()
    assert c.db.scalar(select(activations.c.state))=='activating'


def test_installation_edge_is_not_history_until_commit(bootstrap):
    c=bootstrap;c.fault['at']='sign'
    with pytest.raises(OSError):c.execute()
    c.db.rollback()
    row=c.db.execute(select(activations)).mappings().one()
    args=(c.project.root,'fix-sample',c.archived,('archive','安全归档'),c.value['before'],c.value['after'])
    with controlled_successor.authority(c.db,c.project,'owner'):
        with pytest.raises(ValueError,match='installation_not_completed'):controlled_successor.verify(*args)
    with controlled_successor.authority(c.db,c.project,'owner',row['operation_id'],row['fence']):
        proof=controlled_successor.verify(*args)
        assert proof['bootstrap']['claimed'] and not proof['bootstrap']['historical']
    with controlled_successor.authority(c.db,c.project,'owner',row['operation_id'],row['fence']+1):
        with pytest.raises(ValueError,match='stale_bootstrap_executor'):controlled_successor.verify(*args)
