"""Independent operations review/signing. Never activates policy or calls the API."""
import argparse
import base64
from datetime import datetime,timedelta,timezone
import json
import os
from pathlib import Path
import re
import stat
from .replacement_proof import canonical,strict_json
from .replacement_installation import validate_bundle
from .replacement_trust import load


def private_key(path, repository):
    path=Path(path)
    if not path.is_absolute() or path.resolve().is_relative_to(repository.resolve()) or any(p.is_symlink() for p in (path,*path.parents)):
        raise ValueError('private_operations_key_required')
    with os.fdopen(os.open(path,os.O_RDONLY|os.O_NOFOLLOW),'rb') as stream:
        info=os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077 or info.st_nlink!=1 or info.st_uid!=os.getuid() or info.st_size>4096:
            raise ValueError('private_operations_key_required')
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        key=serialization.load_pem_private_key(stream.read(),password=None)
        if not isinstance(key,Ed25519PrivateKey):raise ValueError('invalid_operations_key')
        return key


def sign_bundle(bundle,trust,key,kid,actor,approved_digest):
    manifest=validate_bundle(bundle)
    if not trust.independent_bootstrap() or approved_digest!=bundle['manifest_hash'] or manifest.release_digest!=trust.release_digest or manifest.to_policy!=trust.policy_version:
        raise ValueError('operations_review_binding_mismatch')
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,128}',actor):raise ValueError('invalid_operations_actor')
    now=datetime.now(timezone.utc).replace(microsecond=0)
    payload={'schema_version':1,'purpose':'bootstrap.ops','actor_id':actor,'project_id':manifest.project_id,
        'binding_revision':manifest.binding_revision,'installation_digest':bundle['manifest_hash'],
        'operation_id':manifest.operation_id,'release_digest':manifest.release_digest,
        'issued_at':now.isoformat(),'expires_at':(now+timedelta(hours=24)).isoformat()}
    receipt={'key_id':kid,'payload':payload,'signature':base64.b64encode(key.sign(canonical(payload))).decode()}
    trust.verify(receipt,purpose='bootstrap.ops',bindings=payload)
    return receipt


def main(argv=None):
    parser=argparse.ArgumentParser(description='独立运维审阅/签发精确策略转换授权，不执行归档。')
    parser.add_argument('--bundle',required=True)
    parser.add_argument('--sign',action='store_true')
    parser.add_argument('--key-file');parser.add_argument('--key-id');parser.add_argument('--actor')
    parser.add_argument('--approved-manifest-sha256');parser.add_argument('--output')
    args=parser.parse_args(argv)
    try:
        path=Path(args.bundle)
        if path.is_symlink() or path.stat().st_size>256*1024:raise ValueError('invalid_review_bundle')
        bundle=strict_json(path.read_bytes());manifest=validate_bundle(bundle)
        if not args.sign:
            print(json.dumps({'manifest_hash':bundle['manifest_hash'],'mechanism_change':manifest.mechanism_change,
                'release_digest':manifest.release_digest,'transitions':bundle['transitions'],'evidence':bundle['evidence'],
                'next':'独立核验制品、差异和验收证据后，显式签发相同摘要；本次未签名或启用。'},ensure_ascii=False,indent=2));return 0
        if not all((args.key_file,args.key_id,args.actor,args.approved_manifest_sha256,args.output)):raise ValueError('explicit_operations_approval_required')
        receipt=sign_bundle(bundle,load(Path.cwd()),private_key(args.key_file,Path.cwd()),args.key_id,args.actor,args.approved_manifest_sha256)
        target=Path(args.output)
        if not target.is_absolute() or target.resolve().is_relative_to(Path.cwd().resolve()) or any(p.is_symlink() for p in (target,*target.parents)):
            raise ValueError('private_output_path_required')
        with os.fdopen(os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb') as stream:stream.write(canonical(receipt))
        print(json.dumps({'status':'signed','manifest_hash':bundle['manifest_hash'],'policy_activated':False}));return 0
    except (OSError,ValueError,KeyError,TypeError):
        print(json.dumps({'status':'blocked','reason':'清单、可信制品、独立密钥或显式审阅摘要未通过；未启用策略。'},ensure_ascii=False));return 1


if __name__=='__main__':raise SystemExit(main())
