"""Backend-only signer client. The socket is never mounted into Agent runtimes."""
import http.client
import json
import os
import socket
from .replacement_proof import canonical


def sign(payload):
    address = os.environ.get('MOONBOX_REPLACEMENT_SIGNER_SOCKET')
    if not address or not os.path.isabs(address):
        raise ValueError('authorization_service_unavailable')
    class Connection(http.client.HTTPConnection):
        def connect(self):
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.settimeout(5)
            self.sock.connect(address)
    try:
        connection = Connection('localhost', timeout=5)
        connection.request('POST', '/sign', body=canonical(payload), headers={'Content-Type': 'application/json'})
        response = connection.getresponse()
        raw = response.read(16385)
        if response.status != 200 or len(raw) > 16384:
            raise ValueError()
        return json.loads(raw)
    except (OSError, ValueError, http.client.HTTPException):
        raise ValueError('authorization_service_unavailable') from None
    finally:
        if 'connection' in locals(): connection.close()
