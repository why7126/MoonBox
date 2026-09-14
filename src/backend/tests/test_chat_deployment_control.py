from pathlib import Path
import pytest
from app.chat.deployment import private_root, existing, stop


def test_control_directory_rejects_symlink_and_public_permissions(tmp_path):
    root=tmp_path/'control';root.mkdir(mode=0o755)
    with pytest.raises(RuntimeError):private_root(root)
    root.chmod(0o700);private_root(root)
    link=tmp_path/'alias';link.symlink_to(root,target_is_directory=True)
    with pytest.raises(RuntimeError):private_root(link)


def test_lost_control_endpoint_is_preserved(tmp_path):
    root=tmp_path/'control';root.mkdir(mode=0o700)
    endpoint=root/'control.sock';endpoint.write_text('stale record')
    with pytest.raises(RuntimeError):existing(root)
    assert endpoint.read_text()=='stale record'


def test_starting_marker_is_not_silently_overwritten(tmp_path):
    root=tmp_path/'control';root.mkdir(mode=0o700)
    (root/'starting').write_text('starting')
    with pytest.raises(RuntimeError):existing(root)


def test_stop_without_instance_is_idempotent(tmp_path):
    root=tmp_path/'control';root.mkdir(mode=0o700)
    assert stop(root)=={'stopped':True,'already_stopped':True}
    assert stop(root)=={'stopped':True,'already_stopped':True}


def test_stop_waits_for_cleanup_and_removes_exported_web_cache(tmp_path, monkeypatch):
    from app.chat import deployment
    root=tmp_path/'control';root.mkdir(mode=0o700)
    endpoint=root/'control.sock';endpoint.touch()
    dist=root/'web-dist';dist.mkdir();(dist/'index.html').write_text('test')
    data=tmp_path/'test-data';data.mkdir()
    monkeypatch.setattr(deployment,'existing',lambda _: {'root':str(data)})
    def cleanup(selected, action):
        assert selected==root and action=='cleanup'
        data.rmdir();endpoint.unlink()
        return {'stopping':True}
    monkeypatch.setattr(deployment,'request',cleanup)
    assert stop(root)=={'stopped':True,'test_data_removed':True}
    assert not dist.exists()
