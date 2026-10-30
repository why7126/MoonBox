"""Short-lived synthetic secrets on private media; database stores opaque refs only."""
import json
import os
from pathlib import Path
import secrets
import time
from uuid import uuid4
from sqlalchemy import insert, select, update
from app.chat.service import identity
from app.chat.workspace import trusted_directory
from app.verification.acceptance_schema import identities
from app.verification.acceptance_state import Conflict


class IdentityLease:
    def __init__(self, state, root, clock=time.time):
        self.state, self.clock = state, clock
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        trusted_directory(self.root)
        if self.root.stat().st_mode & 0o077:
            raise Conflict('identity_storage_untrusted')

    def issue(self, token, role, *, approved_roles):
        if role not in {'member', 'reader', 'admin'} or role not in approved_roles:
            raise Conflict('identity_role_not_approved')
        ref = uuid4().hex
        path = self.root / ref
        expires = min(int(self.clock()) + 900, token['expires_at'])
        if expires <= self.clock(): raise Conflict('identity_expired')
        payload = json.dumps({'username':'a' + ref[:31], 'password':secrets.token_urlsafe(32),
                              'role':role, 'expires_at':expires})
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        try:
            with os.fdopen(descriptor, 'w') as stream:
                stream.write(payload); stream.flush(); os.fsync(stream.fileno())
            with self.state.factory.begin() as db:
                row, attempt = self.state._fenced(db, token)
                self.state._cas(db, row)
                db.execute(insert(identities).values(**identity(), attempt_id=attempt['id'], identity_ref=ref,
                    role=role, expires_at=expires, revocation_state='active'))
        except BaseException:
            path.unlink(missing_ok=True)
            raise
        return {'identity_ref':ref, 'role':role, 'expires_at':expires}

    def revoke(self, attempt_id, *, revoke_application, isolate_network):
        """Callbacks use exact owned runtime identities; never broad network cleanup."""
        with self.state.factory() as db:
            rows = list(db.execute(select(identities).where(identities.c.attempt_id == attempt_id,
                identities.c.revocation_state != 'revoked')).mappings())
        complete = True
        for row in rows:
            ref = row['identity_ref']
            if len(ref) != 32 or any(c not in '0123456789abcdef' for c in ref):
                raise Conflict('identity_reference_invalid')
            try:
                try:
                    revoked = bool(revoke_application(ref))
                except Exception:
                    revoked = False
                isolated = False
                if not revoked:
                    complete = False
                    try:
                        isolated = bool(isolate_network())
                    except Exception:
                        pass
                with self.state.factory.begin() as db:
                    db.execute(update(identities).where(identities.c.id == row['id']).values(
                        revocation_state='revoked' if revoked else
                        ('isolated_pending' if isolated else 'revocation_failed')))
            finally:
                (self.root / ref).unlink(missing_ok=True)
        return complete


class CommandIdentityAdapter:
    """Approved application commands consume secrets through stdin inside the private app."""
    def __init__(self,state,template,root):
        self.leases=IdentityLease(state,root)
        self.template=template;self.engine=None;self.current=None;self.token=None

    def activate(self,token,role,engine):
        self.revoke_all()
        self.engine=engine;self.token=token
        self.current=self.leases.issue(token,role,approved_roles=self.template.data['roles'])
        payload=self.private_payload()
        self.engine.command(['exec','-i',engine.name+'-app',*self.template.data['identity_adapter']['issue']],
                            timeout=60,input=payload)

    def private_payload(self):
        if not self.current or self.current['expires_at']<=self.leases.clock():
            raise Conflict('identity_expired')
        return (self.leases.root/self.current['identity_ref']).read_text()

    def revoke_all(self):
        if not self.current:return True
        def revoke(ref):
            try:
                username=json.loads((self.leases.root/ref).read_text())['username']
                self.engine.command(['exec','-i',self.engine.name+'-app',*self.template.data['identity_adapter']['revoke']],
                    timeout=30,input=json.dumps({'identity_ref':ref,'username':username}))
                return True
            except Exception:return False
        clean=self.leases.revoke(self.token['attempt_id'],revoke_application=revoke,
                                 isolate_network=lambda:self.engine.cleanup())
        self.current=None
        if not clean:raise Conflict('identity_revocation_unconfirmed')
        return True
