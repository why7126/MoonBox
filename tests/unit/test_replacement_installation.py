import copy
from types import SimpleNamespace
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from app.governance.replacement_installation import validate_bundle,content_hash,build,describe,KEY
from app.governance.replacement_installation_cli import sign_bundle
from app.governance.replacement_proof import digest,PROTECTED
from test_replacement_bootstrap import sample


def bundle():
    manifest,trust,_=sample();m=manifest.model_dump();m['transitions'][0].update(before_sha256=content_hash('旧约束'),after_sha256=content_hash('完整例外'))
    return {'manifest':m,'manifest_hash':digest(m),'transitions':[{**m['transitions'][0],'before':'旧约束','after':'完整例外'}],
            'protected_obligations':sorted(PROTECTED),'evidence':{'acceptance_digest':m['acceptance_digest'],'delivery_digest':m['delivery_digest'],'delta_digest':m['delta_digest']},'archive_identity':None},trust


@pytest.mark.parametrize('field',['text','hash','evidence','protected','extra','archived'])
def test_bundle_rejects_detached_review(field):
    value,_=bundle()
    if field=='text':value['transitions'][0]['before']='别的约束'
    if field=='hash':value['manifest']['release_digest']='9'*64
    if field=='evidence':value['evidence']['delivery_digest']='9'*64
    if field=='protected':value['protected_obligations']=[]
    if field=='extra':value['trusted']=True
    if field=='archived':value['archive_identity']='old'
    with pytest.raises(ValueError):validate_bundle(value)


def test_bundle_is_exact_but_not_authorization():
    value,_=bundle();assert validate_bundle(value).mechanism_change=='install-policy'


def test_ops_signing_requires_matching_key_trust_and_explicit_digest():
    value,trust=bundle();key=Ed25519PrivateKey.generate()
    with pytest.raises(ValueError):sign_bundle(value,trust,key,'ops','operator',value['manifest_hash'])
    with pytest.raises(ValueError):sign_bundle(value,trust,key,'ops','operator','0'*64)
    import base64
    from cryptography.hazmat.primitives import serialization
    trust.keys['ops']=base64.b64encode(key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)).decode()
    result=sign_bundle(value,trust,key,'ops','operator',value['manifest_hash'])
    assert result['payload']['purpose']=='bootstrap.ops'
    assert result['payload']['installation_digest']==value['manifest_hash']
    with pytest.raises(ValueError):trust.verify(result,purpose='bootstrap.owner',bindings={})


def test_preview_blocks_before_tool_or_write_when_acceptance_not_ready(tmp_path,monkeypatch):
    from app.governance import replacement_installation as module
    (tmp_path/'openspec/changes/install-policy').mkdir(parents=True)
    monkeypatch.setattr(module,'readiness',lambda *a,**k:{'status':'blocked'})
    project=SimpleNamespace(root=tmp_path,source_root=None)
    with pytest.raises(ValueError,match='acceptance_not_ready'):build(project,'install-policy',None,driver_type=lambda p:pytest.fail('must not run tool'))
    assert not (tmp_path/'openspec/archive').exists()


def test_preview_binds_current_inputs_and_does_not_write_journal(tmp_path,monkeypatch):
    from app.governance import replacement_installation as module,replacement_trust
    from app.governance.scope import ProjectScope
    from app.governance.archive_recovery import tree_hash
    _,trust=bundle()
    root=tmp_path/'repo';folder=root/'openspec/changes/install-policy'
    target=folder/'specs'/KEY[0]/'spec.md';target.parent.mkdir(parents=True)
    target.write_text('## MODIFIED Requirements\n\n### Requirement: '+KEY[1]+'\n新规则 SHALL 保留保护。\n')
    base=root/'openspec/specs'/KEY[0]/'spec.md';base.parent.mkdir(parents=True)
    base.write_text('### Requirement: '+KEY[1]+'\n原规则 SHALL 拒绝。\n')
    project=ProjectScope('space','repo',root,'b'*64,False)
    monkeypatch.setattr(module,'readiness',lambda *a,**k:{'status':'ready'})
    monkeypatch.setattr(module,'acceptance_binding',lambda *a,**k:'a'*64)
    from app.governance import replacement_activation
    monkeypatch.setattr(replacement_activation,'acceptance_binding',lambda *a,**k:'a'*64)
    class Driver:
        def __init__(self,p):pass
        def validate_static(self,c):pass
        def preview(self,c):return 'e'*64
    before=tree_hash(root)
    result=build(project,'install-policy',trust,driver_type=Driver)
    assert validate_bundle(result).project_id==project.key
    assert tree_hash(root)==before
    class Racing(Driver):
        def preview(self,c):
            base.write_text(base.read_text()+'并发变化\n');return 'e'*64
    with pytest.raises(ValueError,match='inputs_changed'):build(project,'install-policy',trust,driver_type=Racing)
