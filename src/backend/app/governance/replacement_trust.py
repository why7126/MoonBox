"""Ed25519 receipts with externally mounted public trust and isolated signing.

No private key is loaded into an Agent/controller process. The auth service
receives a signing implementation from its deployment boundary. Missing trust
always fails closed; repository certificates cannot install a trust root.
"""
from __future__ import annotations
import base64
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import stat
import re
from typing import Callable
from .replacement_proof import canonical, strict_json


@dataclass(frozen=True)
class Trust:
    keys: dict[str, str]
    revoked: frozenset[str]
    profiles: dict
    policy_version: str
    release_digest: str
    purpose_keys: dict[str, list[str]]

    def independent_bootstrap(self) -> bool:
        # Key aliases must not turn one signer into two independent authorities.
        try:
            groups = [{base64.b64decode(self.keys[kid], validate=True)
                       for kid in self.purpose_keys.get(purpose, [])}
                      for purpose in ('bootstrap.ops', 'bootstrap.owner')]
            return bool(all(groups) and not groups[0].intersection(groups[1]))
        except (ValueError, KeyError, TypeError):
            return False

    def verify(self, receipt: dict, *, purpose: str, bindings: dict, historical=False, now=None) -> dict:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.exceptions import InvalidSignature
        try:
            if set(receipt) != {'key_id', 'payload', 'signature'}:
                raise ValueError()
            kid = receipt['key_id']
            if kid in self.revoked or kid not in self.keys or kid not in self.purpose_keys.get(purpose, []):
                raise ValueError()
            payload = receipt['payload']
            if not isinstance(payload, dict): raise ValueError()
            if not isinstance(payload.get('actor_id'), str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', payload['actor_id']):
                raise ValueError()
            for name in ('project_id', 'binding_revision', 'release_digest'):
                if not isinstance(payload.get(name), str) or not re.fullmatch(r'[a-f0-9]{64}', payload[name]):
                    raise ValueError()
            if purpose.startswith('replacement.'):
                if not isinstance(payload.get('policy_version'), str): raise ValueError()
                if not re.fullmatch(r'[a-f0-9]{64}', payload.get('proposal_digest', '')): raise ValueError()
            if purpose in {'replacement.approve', 'replacement.reject', 'replacement.revoke'}:
                if type(payload.get('revision')) is not int or payload['revision'] < 1 or not payload.get('proposal_id'):
                    raise ValueError()
            if purpose in {'bootstrap.ops', 'bootstrap.owner', 'bootstrap.commit', 'replacement.commit'} and not payload.get('operation_id'):
                raise ValueError()
            if payload['purpose'] != purpose or type(payload['schema_version']) is not int or payload['schema_version'] != 1:
                raise ValueError()
            if any(payload.get(k) != v for k, v in bindings.items()):
                raise ValueError()
            key = Ed25519PublicKey.from_public_bytes(base64.b64decode(self.keys[kid], validate=True))
            key.verify(base64.b64decode(receipt['signature'], validate=True), canonical(payload))
            issued = datetime.fromisoformat(payload['issued_at'])
            expires = datetime.fromisoformat(payload['expires_at'])
            current = now or datetime.now(timezone.utc)
            if issued.tzinfo is None or expires.tzinfo is None or (expires-issued).total_seconds() != 86400:
                raise ValueError()
            if not historical and not issued <= current < expires:
                raise ValueError()
            return payload
        except (ValueError, KeyError, TypeError, InvalidSignature):
            raise ValueError('authorization_untrusted') from None


def load(repository: Path) -> Trust:
    """Deployment mount must be outside repo, symlink-free and not writable here."""
    value = os.environ.get('MOONBOX_REPLACEMENT_TRUST_FILE')
    if not value:
        raise ValueError('policy_not_trusted')
    path = Path(value)
    try:
        if not path.is_absolute() or path.resolve().is_relative_to(repository.resolve()):
            raise ValueError()
        if any(p.is_symlink() for p in (path, *path.parents)):
            raise ValueError()
        if any(os.access(item, os.W_OK) for item in (path, *path.parents)):
            raise ValueError()
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, 'rb') as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > 256*1024 or info.st_nlink != 1:
                raise ValueError()
            data = strict_json(stream.read(256*1024+1))
        return parse(data)
    except (OSError, ValueError, TypeError, KeyError):
        raise ValueError('policy_not_trusted') from None


def parse(data) -> Trust:
    """Validate public trust identically at host preflight and mounted runtime."""
    if (set(data) != {'schema_version', 'keys', 'revoked', 'profiles', 'policy_version', 'release_digest', 'purpose_keys'}
            or type(data['schema_version']) is not int or data['schema_version'] != 1):
        raise ValueError()
    purposes={'replacement.approve','replacement.reject','replacement.revoke','replacement.commit',
              'bootstrap.ops','bootstrap.owner','bootstrap.commit'}
    if (not isinstance(data['keys'],dict) or not data['keys'] or not isinstance(data['profiles'],dict)
            or not isinstance(data['purpose_keys'],dict) or set(data['purpose_keys'])-purposes
            or not isinstance(data['revoked'],list) or not all(isinstance(k,str) for k in data['revoked'])
            or len(set(data['revoked']))!=len(data['revoked'])
            or not isinstance(data['release_digest'],str) or not re.fullmatch('[a-f0-9]{64}',data['release_digest'])
            or not isinstance(data['policy_version'],str) or not re.fullmatch('[a-z0-9][a-z0-9-]{0,100}',data['policy_version'])):
        raise ValueError()
    for kid,key in data['keys'].items():
        if not re.fullmatch('[A-Za-z0-9_-]{1,128}',kid) or not isinstance(key,str) or len(base64.b64decode(key,validate=True))!=32:
            raise ValueError()
    for assigned in data['purpose_keys'].values():
        if (not isinstance(assigned,list) or not assigned or not all(isinstance(k,str) and k in data['keys'] for k in assigned)
                or len(set(assigned))!=len(assigned)):
            raise ValueError()
    trust = Trust(data['keys'], frozenset(data['revoked']), data['profiles'], data['policy_version'], data['release_digest'], data['purpose_keys'])
    if not trust.independent_bootstrap():
        raise ValueError()
    return trust
