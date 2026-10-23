"""Deployment signer restart and purpose restrictions fail closed."""
import json
import socket
import tempfile
from pathlib import Path
import pytest
from app.governance.replacement_signing_service import purposes,remove_stale_socket,ALLOWED


def test_signer_purpose_subset_never_includes_operations_role(monkeypatch):
    monkeypatch.delenv('MOONBOX_AUTHORIZATION_PURPOSES',raising=False)
    assert purposes()==ALLOWED
    monkeypatch.setenv('MOONBOX_AUTHORIZATION_PURPOSES','["bootstrap.owner"]')
    assert purposes()=={'bootstrap.owner'}
    for value in ([],['bootstrap.ops'],['bootstrap.owner','bootstrap.owner'],True,{'bootstrap.owner':True}):
        monkeypatch.setenv('MOONBOX_AUTHORIZATION_PURPOSES',json.dumps(value))
        with pytest.raises(ValueError):purposes()


def test_owned_dead_socket_can_restart_but_live_socket_is_preserved(tmp_path):
    # macOS Unix socket addresses are limited to 104 bytes.
    with tempfile.TemporaryDirectory(prefix='mb-sign-',dir='/tmp') as directory:
        path=Path(directory).resolve()/'sign.sock'
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as server:
            server.bind(str(path));server.listen(1)
            with pytest.raises(ValueError,match='already active'):remove_stale_socket(str(path))
            assert path.exists()
        remove_stale_socket(str(path))
        assert not path.exists()


def test_non_socket_and_symlink_are_never_removed(tmp_path):
    path=tmp_path/'key';path.write_text('protected')
    with pytest.raises(ValueError,match='foreign'):remove_stale_socket(str(path))
    link=tmp_path/'sign.sock';link.symlink_to(path)
    with pytest.raises(ValueError,match='unsafe'):remove_stale_socket(str(link))
    assert path.read_text()=='protected'
