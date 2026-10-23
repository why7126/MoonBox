"""Historical signed replacement edge; no source IDs receive special treatment."""
import base64
import hashlib
import json
from datetime import datetime,timedelta,timezone
from types import SimpleNamespace
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from test_replacement_proof import fixture
from app.governance import controlled_successor as controlled
from app.governance import replacement_inputs as inputs
from app.governance.replacement_proof import Proposal,canonical,digest
from app.governance.replacement_trust import Trust
from app.governance.archive_recovery import tree_hash
from app.governance.compatible_successor import acceptance_binding,recheck
from app.governance.acceptance_evidence import fingerprint


def put(path,body):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(body)


def scene(tmp_path,monkeypatch,*,prior_append=False):
    value,profiles=fixture();root=tmp_path
    if prior_append:
        addition=' #### Scenario: 前置兼容场景 - **WHEN** 新的调用 - **THEN** 保留原约束'
        for name in ('before','after'):
            value[name]+=addition
            profiles['append-v1'][name+'_sha256']=hashlib.sha256(value[name].encode()).hexdigest()
        value['predecessors'].append('origin-sample')
    folder=root/'openspec/archive/2026-10-22-fix-sample'
    put(folder/'specs/archive/spec.md','## MODIFIED Requirements\n### Requirement: 安全归档\n'+value['after']+'\n')
    put(folder/'trace.md','---\nstatus: archived\nexecution:\n  schema_version: 1\n  started_at: 2026-10-22T01:00:00Z\n  completed_at: 2026-10-22T02:00:00Z\n---\n')
    artifact=folder/'evidence/acceptance/run/result.txt';put(artifact,'passed')
    put(root/'rules/global.md','isolated evidence')
    plan={'schema_version':1,'change_id':'fix-sample','checks':[{'id':'AC-001','kind':'command','argv':['true'],'inputs':['rules/global.md'],'artifacts':[artifact.relative_to(root).as_posix()]}]}
    put(folder/'acceptance-plan.json',json.dumps(plan))
    manifest={'schema_version':1,'run_id':'run','status':'passed','checks':[{'id':'AC-001','status':'passed','fingerprint':fingerprint(root,plan['checks'][0]),'artifacts':[{'path':artifact.relative_to(root).as_posix(),'sha256':hashlib.sha256(b'passed').hexdigest()}]}]}
    put(folder/'evidence/acceptance/run/manifest.json',json.dumps(manifest))
    protected=root/'openspec/specs/protection/spec.md';put(protected,'\n'.join(o['before'] for o in value['obligations']))
    for obligation in value['obligations']:obligation['source']['sha256']=hashlib.sha256(protected.read_bytes()).hexdigest()
    profiles['append-v1']['obligations_sha256']=digest({'obligations':value['obligations']})
    prior=root/'openspec/archive/2026-10-21-prior-sample'
    put(prior/'trace.md','---\nstatus: archived\n---\n')
    put(prior/'specs/archive/spec.md','## ADDED Requirements\n### Requirement: 安全归档\n'+value['before']+'\n')
    current=root/'openspec/specs/archive/spec.md'
    put(current,'# 归档\n\n### Requirement: 安全归档\n'+value['before']+'\n')
    baseline=tree_hash(root/'openspec/specs')
    put(current,'# 归档\n\n### Requirement: 安全归档\n'+value['after']+'\n')
    from app.governance.archive_recovery import delivery_input_hash,journal_path
    put(journal_path(root,'fix-sample'),json.dumps({'schema_version':4,'input_projection':1,
        'change_id':'fix-sample','archive_date':'2026-10-22','delta_hash':tree_hash(folder/'specs'),
        'active_change_hash':tree_hash(folder),'delivery_input_hash':delivery_input_hash(folder),
        'baseline_spec_hash':baseline,'expected_spec_hash':tree_hash(root/'openspec/specs')}))
    value.update(delta_sha256=tree_hash(folder/'specs'),delivery_sha256=inputs.replacement_delivery_hash(folder),acceptance_sha256=acceptance_binding(root,folder))
    for name in ('review','regression'):
        path=root/f'openspec/proof-evidence/{name}.json'
        body={'status':'passed','proposal_content_sha256':inputs.content_digest(Proposal.model_validate(value)),
              'checks':['destructive_changes','broken_chain','concurrent_change','protected_obligations','exact_mapping'],
              'reviewer':'isolated-reviewer','contradictions':[]}
        put(path,json.dumps(body));value[name]={'path':path.relative_to(root).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    key=Ed25519PrivateKey.generate()
    public=base64.b64encode(key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)).decode()
    trust=Trust({'key':public},frozenset(),profiles,'policy-v1','f'*64,{'replacement.approve':['key'],'replacement.commit':['key']})
    monkeypatch.setattr(controlled,'load',lambda root:trust)
    now=datetime.now(timezone.utc).replace(microsecond=0)
    def sign(payload):
        payload={**payload,'schema_version':1,'issued_at':now.isoformat(),'expires_at':(now+timedelta(hours=24)).isoformat()}
        return {'key_id':'key','payload':payload,'signature':base64.b64encode(key.sign(canonical(payload))).decode()}
    bindings={'actor_id':'owner','release_digest':'f'*64,'project_id':value['project_id'],'binding_revision':value['binding_revision'],'proposal_digest':digest(value),'policy_version':'policy-v1'}
    approval=sign({**bindings,'purpose':'replacement.approve','proposal_id':'proposal','revision':2})
    from app.governance.replacement_commit_evidence import bindings as journal_bindings
    commit=sign({**bindings,**journal_bindings(root,'fix-sample'),'purpose':'replacement.commit','operation_id':'operation','authorization_sha256':digest(approval),
        'archive_identity':folder.name,'delta_sha256':value['delta_sha256'],'acceptance_sha256':value['acceptance_sha256']})
    path=controlled.proof_path(root,'fix-sample',('archive','安全归档'))
    put(path,json.dumps({'schema_version':1,'proposal':value,'authorization':approval,'commit':commit}))
    project=SimpleNamespace(root=root,key=value['project_id'],binding_revision=value['binding_revision'])
    from sqlalchemy import create_engine,insert
    from sqlalchemy.orm import Session
    from app.governance.replacement_schema import commits
    from app.chat.service import identity
    engine=create_engine('sqlite:///'+str(root/'authority.sqlite'));commits.create(engine)
    db=Session(engine)
    db.execute(insert(commits).values(**(identity()|{'id':'operation'}),scope_key=project.key,proposal_id='proposal',actor_id='owner',stage='completed',fence=1,lease_until=now.isoformat(),input_hash='a'*64,expected_hash='b'*64,revision=5));db.commit()
    return value,folder,project,path,db


def test_historical_replacement_and_final_dependency_reread(tmp_path,monkeypatch):
    value,folder,project,path,db=scene(tmp_path,monkeypatch)
    with controlled.authority(db,project,'actor'):
        proof=controlled.verify(tmp_path,'fix-sample',folder,('archive','安全归档'),value['before'],value['after'])
        recheck(tmp_path,proof)
        path.write_text('{}')
        with pytest.raises(ValueError):recheck(tmp_path,proof)


def test_absent_authority_cannot_consume_repo_certificate(tmp_path,monkeypatch):
    value,folder,project,path,db=scene(tmp_path,monkeypatch)
    with pytest.raises(ValueError,match='authority_unavailable'):
        controlled.verify(tmp_path,'fix-sample',folder,('archive','安全归档'),value['before'],value['after'])


def test_historical_rotation_retains_old_key_but_revocation_blocks(tmp_path,monkeypatch):
    from dataclasses import replace
    value,folder,project,path,db=scene(tmp_path,monkeypatch)
    old=controlled.load(tmp_path)
    newer=Ed25519PrivateKey.generate().public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
    rotated=replace(old,keys={**old.keys,'new-key':base64.b64encode(newer).decode()})
    monkeypatch.setattr(controlled,'load',lambda root:rotated)
    with controlled.authority(db,project,'different-current-owner'):
        proof=controlled.verify(tmp_path,'fix-sample',folder,('archive','安全归档'),value['before'],value['after'])
        recheck(tmp_path,proof)
        revoked=replace(rotated,revoked=frozenset({'key'}))
        monkeypatch.setattr(controlled,'load',lambda root:revoked)
        with pytest.raises(ValueError):recheck(tmp_path,proof)


def test_historical_ordinary_expiry_does_not_erase_completed_fact(tmp_path,monkeypatch):
    value,folder,project,path,db=scene(tmp_path,monkeypatch)
    original=Trust.verify
    def later(self,receipt,**kwargs):
        kwargs['now']=datetime.now(timezone.utc)+timedelta(days=10)
        return original(self,receipt,**kwargs)
    monkeypatch.setattr(Trust,'verify',later)
    with controlled.authority(db,project,'different-current-owner'):
        proof=controlled.verify(tmp_path,'fix-sample',folder,('archive','安全归档'),value['before'],value['after'])
        recheck(tmp_path,proof)


def test_complete_append_replacement_append_chain_and_missing_edge(tmp_path,monkeypatch):
    from app.governance import archive_recovery as recovery
    from test_compatible_successor import certificate,ADDITION
    value,folder,project,path,db=scene(tmp_path,monkeypatch,prior_append=True)
    current=tmp_path/'openspec/specs/archive/spec.md';final_text=current.read_text()
    prior=tmp_path/'openspec/archive/2026-10-21-prior-sample'
    origin=tmp_path/'openspec/archive/2026-10-20-origin-sample'
    base=value['before'].split(' #### Scenario: 前置兼容场景')[0]
    put(origin/'specs/archive/spec.md','## ADDED Requirements\n### Requirement: 安全归档\n'+base+'\n')
    put(origin/'trace.md','---\nstatus: archived\n---\n')
    put(current,'# 归档\n\n### Requirement: 安全归档\n'+base+'\n')
    origin_hash=tree_hash(tmp_path/'openspec/specs')
    put(current,'# 归档\n\n### Requirement: 安全归档\n'+value['before']+'\n')
    prior_hash=tree_hash(tmp_path/'openspec/specs')
    put(current,final_text)
    prior_spec=prior/'specs/archive/spec.md'
    prior_spec.write_text(prior_spec.read_text().replace('ADDED','MODIFIED'))
    put(recovery.journal_path(tmp_path,'origin-sample'),json.dumps({'change_id':'origin-sample','expected_spec_hash':origin_hash,'delta_hash':tree_hash(origin/'specs')}))
    put(recovery.journal_path(tmp_path,'prior-sample'),json.dumps({'change_id':'prior-sample','baseline_spec_hash':origin_hash,'expected_spec_hash':prior_hash,'delta_hash':tree_hash(prior/'specs')}))
    certificate(tmp_path,prior,base,value['before'],'prior-sample',key=('archive','安全归档'))
    last=tmp_path/'openspec/archive/2026-10-23-last-sample'
    put(last/'specs/archive/spec.md',(folder/'specs/archive/spec.md').read_text()+ADDITION)
    put(last/'trace.md','---\nstatus: archived\niteration: sprint-999\n---\n')
    baseline=tree_hash(tmp_path/'openspec/specs')
    put(current,final_text+ADDITION)
    put(recovery.journal_path(tmp_path,'last-sample'),json.dumps({'change_id':'last-sample','baseline_spec_hash':baseline,'expected_spec_hash':tree_hash(tmp_path/'openspec/specs'),'delta_hash':tree_hash(last/'specs')}))
    after=recovery.delta_operations(last)[('archive','安全归档')][1]
    certificate(tmp_path,last,value['after'],after,'last-sample',key=('archive','安全归档'))
    with controlled.authority(db,project,'actor'):
        result=recovery.recovery_admission(tmp_path,'origin-sample')
        assert result['ready'],result
        assert len(result['chain'])==3
        recovery.journal_path(tmp_path,'prior-sample').unlink()
        assert not recovery.recovery_admission(tmp_path,'origin-sample')['ready']
