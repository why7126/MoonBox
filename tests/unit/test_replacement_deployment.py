import base64
import json
import os
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from app.governance.replacement_deployment import check
from app.governance.replacement_installation_cli import private_key

@pytest.fixture
def deployment(tmp_path,monkeypatch):
    root=tmp_path/'repo';root.mkdir()
    for name in ('issues','openspec','iterations'):(root/name).mkdir()
    key=Ed25519PrivateKey.generate();ops=Ed25519PrivateKey.generate()
    pub=lambda k:base64.b64encode(k.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)).decode()
    online=tmp_path/'online.pem';online.write_bytes(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()));online.chmod(0o600)
    trust={'schema_version':1,'keys':{'online':pub(key),'ops':pub(ops)},'revoked':[],'profiles':{},'policy_version':'controlled-v1','release_digest':'a'*64,'purpose_keys':{'bootstrap.ops':['ops'],**{p:['online'] for p in ('bootstrap.owner','bootstrap.commit','replacement.approve','replacement.reject','replacement.revoke','replacement.commit')}}}
    public=tmp_path/'trust.json';public.write_text(json.dumps(trust));sock=tmp_path/'socket';sock.mkdir(mode=0o700)
    for key,value in {'MOONBOX_REPLACEMENT_TRUST_SOURCE':str(public),'MOONBOX_AUTHORIZATION_KEY_SOURCE':str(online),'MOONBOX_REPLACEMENT_SOCKET_ROOT':str(sock),'MOONBOX_AUTHORIZATION_KEY_ID':'online'}.items():monkeypatch.setenv(key,value)
    return root,public,online,sock,trust


def test_valid_preflight_never_activates_or_creates_ops_key(deployment):
    root,_,_,_,_=deployment
    assert check(root)=={'status':'passed','policy_activated':False,'operations_key_mounted':False}
    assert not list(root.rglob('*.pem'))

@pytest.mark.parametrize('case',['shared','revoked','unknown','permissions','symlink','oversized'])
def test_invalid_deployment_fails_closed(deployment,case,monkeypatch):
    root,public,online,sock,trust=deployment
    if case=='shared':trust['keys']['ops']=trust['keys']['online']
    if case=='revoked':trust['revoked']=['online']
    if case=='unknown':trust['extra']=True
    if case=='permissions':online.chmod(0o644)
    if case=='symlink':
        link=online.parent/'link.pem';link.symlink_to(online);monkeypatch.setenv('MOONBOX_AUTHORIZATION_KEY_SOURCE',str(link))
    if case=='oversized':online.write_bytes(b'x'*4097)
    public.write_text(json.dumps(trust))
    with pytest.raises(ValueError):check(root)


def test_offline_private_key_rejects_repository_and_public_permissions(deployment):
    root,_,online,_,_=deployment
    assert private_key(online,root)
    online.chmod(0o644)
    with pytest.raises(ValueError):private_key(online,root)
