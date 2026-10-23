"""Purpose-separated bootstrap must not be signed by the new policy itself."""
import base64
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from app.governance.replacement_bootstrap import Installation, verify_installation
from app.governance.replacement_trust import Trust
from app.governance.replacement_proof import PROTECTED, canonical, digest


def sample():
    keys = {name: Ed25519PrivateKey.generate() for name in ('ops', 'owner')}
    public = {name: base64.b64encode(key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)).decode() for name,key in keys.items()}
    trust = Trust(public, frozenset(), {}, 'policy-v2', 'c'*64, {'bootstrap.ops':['ops'], 'bootstrap.owner':['owner']})
    project = SimpleNamespace(key='a'*64, binding_revision='b'*64)
    manifest = Installation(schema_version=1, kind='policy_installation', project_id=project.key,
        binding_revision=project.binding_revision, mechanism_change='install-policy', from_policy='policy-v1', to_policy='policy-v2',
        release_digest='c'*64, verifier_digest='d'*64, delta_digest='e'*64, acceptance_digest='f'*64, delivery_digest='a'*64,
        baseline_digest='1'*64, expected_digest='2'*64, protected_obligations=sorted(PROTECTED), operation_id='install-operation',
        transitions=[{'capability':'governance-command-durable-recovery','requirement':'归档连续证明的条文冲突范围','before_sha256':'3'*64,'after_sha256':'4'*64}])
    now=datetime.now(timezone.utc).replace(microsecond=0)
    receipts={}
    for name,key in keys.items():
        payload={'schema_version':1,'actor_id':name,'purpose':'bootstrap.'+name,'project_id':project.key,
            'binding_revision':project.binding_revision,'installation_digest':digest(manifest.model_dump()),
            'operation_id':manifest.operation_id,'release_digest':trust.release_digest,
            'issued_at':now.isoformat(),'expires_at':(now+timedelta(hours=24)).isoformat()}
        receipts[name]={'key_id':name,'payload':payload,'signature':base64.b64encode(key.sign(canonical(payload))).decode()}
    return manifest,trust,dict(ops_receipt=receipts['ops'],owner_receipt=receipts['owner'],project=project,
        current_policy='policy-v1',release_digest='c'*64,verifier_digest='d'*64,now=now)


def test_exact_independent_bootstrap():
    manifest,trust,args=sample(); assert verify_installation(manifest,trust,**args)['installation_digest']==digest(manifest.model_dump())


@pytest.mark.parametrize('damage',['self','missing','role','release','verifier','project','protections','signature'])
def test_bootstrap_rejects_untrusted_installation(damage):
    manifest,trust,args=sample()
    if damage=='self': args['current_policy']='policy-v2'
    if damage=='missing': args['ops_receipt']={}
    if damage=='role': args['ops_receipt']=args['owner_receipt']
    if damage=='release': args['release_digest']='0'*64
    if damage=='verifier': args['verifier_digest']='0'*64
    if damage=='project': args['project']=SimpleNamespace(key='0'*64,binding_revision='b'*64)
    if damage=='protections': manifest=manifest.model_copy(update={'protected_obligations':['history']})
    if damage=='signature': args['owner_receipt']['signature']='eA=='
    with pytest.raises(ValueError): verify_installation(manifest,trust,**args)


def test_key_alias_does_not_supply_independent_deployment_authority():
    manifest,trust,args=sample()
    aliased=Trust({**trust.keys,'ops':trust.keys['owner']},trust.revoked,trust.profiles,
        trust.policy_version,trust.release_digest,trust.purpose_keys)
    assert not aliased.independent_bootstrap()
    with pytest.raises(ValueError,match='bootstrap_roles_not_independent'):
        verify_installation(manifest,aliased,**args)
