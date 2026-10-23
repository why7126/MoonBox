"""Host opt-in validation; never create keys, grant trust or activate a project."""
import os
from pathlib import Path
import stat
import json
from .replacement_proof import strict_json


def check(root):
    paths={}
    for name in ('MOONBOX_REPLACEMENT_TRUST_SOURCE','MOONBOX_AUTHORIZATION_KEY_SOURCE','MOONBOX_REPLACEMENT_SOCKET_ROOT'):
        value=os.environ.get(name,'');p=Path(value)
        if not value or not p.is_absolute() or p.resolve().is_relative_to(root.resolve()) or any(x.is_symlink() for x in (p,*p.parents)):
            raise ValueError('external_replacement_paths_required')
        info=p.stat()
        if name.endswith('SOCKET_ROOT'):
            if not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.getuid() or info.st_mode&0o007 or not os.access(p,os.W_OK):raise ValueError('private_socket_directory_required')
        elif not stat.S_ISREG(info.st_mode) or info.st_nlink!=1:
            raise ValueError('regular_replacement_file_required')
        elif name=='MOONBOX_AUTHORIZATION_KEY_SOURCE' and (info.st_mode&0o077 or info.st_uid!=os.getuid()):
            raise ValueError('private_online_key_required')
        paths[name]=p
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    import base64
    if paths['MOONBOX_AUTHORIZATION_KEY_SOURCE'].stat().st_size>4096:raise ValueError('key_too_large')
    key=serialization.load_pem_private_key(paths['MOONBOX_AUTHORIZATION_KEY_SOURCE'].read_bytes(),password=None)
    if not isinstance(key,Ed25519PrivateKey):raise ValueError('invalid_online_key')
    if paths['MOONBOX_REPLACEMENT_TRUST_SOURCE'].stat().st_size>256*1024:raise ValueError('trust_too_large')
    data=strict_json(paths['MOONBOX_REPLACEMENT_TRUST_SOURCE'].read_bytes());kid=os.environ.get('MOONBOX_AUTHORIZATION_KEY_ID','')
    public=base64.b64encode(key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)).decode()
    from .replacement_trust import parse
    trust=parse(data)
    if not trust.independent_bootstrap() or data['keys'].get(kid)!=public or kid in trust.revoked or kid in trust.purpose_keys.get('bootstrap.ops',[]):raise ValueError('independent_online_key_required')
    if any(kid not in trust.purpose_keys.get(purpose,[]) for purpose in ('bootstrap.owner','bootstrap.commit','replacement.approve','replacement.reject','replacement.revoke','replacement.commit')):raise ValueError('online_key_purposes_missing')
    for name in ('issues','openspec','iterations'):
        if not (root/name).is_dir() or not os.access(root/name,os.W_OK):raise ValueError('governance_writes_unavailable')
    return {'status':'passed','policy_activated':False,'operations_key_mounted':False}


def main():
    try:print(json.dumps(check(Path.cwd())))
    except (ValueError,OSError,KeyError,TypeError):
        print(json.dumps({'status':'blocked','reason':'独立可信配置、在线密钥用途、私有socket目录或治理写入条件不满足；未启动服务。'},ensure_ascii=False));return 1
    return 0


if __name__=='__main__':raise SystemExit(main())
