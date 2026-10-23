"""Deployment-side signing daemon. Never mount its key/socket into an Agent.

Run as a dedicated identity; an OS group grants only the authenticated backend
access to this socket. Operations release signatures use a separate offline key.
"""
import base64
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
import json
import os
from pathlib import Path
import socketserver
import socket
import errno
import stat
from cryptography.hazmat.primitives import serialization
from .replacement_proof import canonical,strict_json

ALLOWED = {'replacement.approve', 'replacement.reject', 'replacement.revoke', 'replacement.commit', 'bootstrap.owner', 'bootstrap.commit'}


def purposes():
    raw=os.environ.get('MOONBOX_AUTHORIZATION_PURPOSES')
    if raw is None:return ALLOWED
    value=json.loads(raw)
    if (not isinstance(value,list) or not value or not all(isinstance(x,str) and x in ALLOWED for x in value)
            or len(set(value))!=len(value)):
        raise ValueError('invalid signing purposes')
    return frozenset(value)


def remove_stale_socket(address):
    """Restart only our dead socket; a live or foreign endpoint is never replaced."""
    path=Path(address)
    if not path.is_absolute() or any(p.is_symlink() for p in (path,*path.parents)):
        raise ValueError('unsafe signing socket')
    try:info=path.lstat()
    except FileNotFoundError:return
    if not stat.S_ISSOCK(info.st_mode) or info.st_uid!=os.getuid():raise ValueError('foreign signing socket')
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as probe:
        probe.settimeout(1)
        try:probe.connect(address)
        except OSError as error:
            if error.errno not in {errno.ECONNREFUSED,errno.ENOENT}:raise ValueError('signing socket unavailable') from None
        else:raise ValueError('signing socket already active')
    try:current=path.lstat()
    except FileNotFoundError:return
    if (current.st_dev,current.st_ino)!=(info.st_dev,info.st_ino):raise ValueError('signing socket changed')
    path.unlink()


def main():
    path = Path(os.environ['MOONBOX_AUTHORIZATION_PRIVATE_KEY'])
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('unsafe signing key')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077 or info.st_size > 4096 or info.st_nlink!=1:
            raise ValueError('unsafe signing key')
        key = serialization.load_pem_private_key(stream.read(), password=None)
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    if not isinstance(key, Ed25519PrivateKey): raise ValueError('unsupported signing key')
    kid = os.environ['MOONBOX_AUTHORIZATION_KEY_ID']
    address = os.environ['MOONBOX_REPLACEMENT_SIGNER_SOCKET']
    allowed=purposes()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_): pass
        def do_POST(self):
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if self.path != '/sign' or not 0 < length <= 16384: raise ValueError()
                value = strict_json(self.rfile.read(length))
                issued = datetime.fromisoformat(value['issued_at'])
                expiry = datetime.fromisoformat(value['expires_at'])
                if (value['purpose'] not in allowed or type(value['schema_version']) is not int or value['schema_version'] != 1
                        or abs((datetime.now(timezone.utc)-issued).total_seconds()) > 30
                        or (expiry-issued).total_seconds() != 86400): raise ValueError()
                result = canonical({'key_id': kid, 'payload': value,
                    'signature': base64.b64encode(key.sign(canonical(value))).decode()})
            except (ValueError, KeyError, TypeError):
                self.send_error(400, 'invalid authorization payload'); return
            self.send_response(200); self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(result))); self.end_headers(); self.wfile.write(result)
    remove_stale_socket(address)
    with socketserver.UnixStreamServer(address, Handler) as server:
        os.chmod(address, 0o660)
        server.serve_forever()


if __name__ == '__main__': main()
