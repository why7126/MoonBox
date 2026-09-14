"""Capture deployment preflight is read-only until explicitly prepared."""
import pytest
from app.governance.deployment import prepare


def test_private_directory_check_and_prepare(tmp_path, monkeypatch):
    root=tmp_path/'private'
    monkeypatch.setenv('MOONBOX_GOVERNANCE_HOST_STATE_ROOT',str(root))
    monkeypatch.setenv('MOONBOX_GOVERNANCE_CAPTURE_MODE','continuous')
    prepare();assert not root.exists()
    prepare(True);assert root.stat().st_mode & 0o777 == 0o700
    prepare()


@pytest.mark.parametrize('invalid',['mode','permissions','symlink'])
def test_preflight_rejects_unsafe_configuration(tmp_path,monkeypatch,invalid):
    root=tmp_path/'private';root.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_HOST_STATE_ROOT',str(root))
    monkeypatch.setenv('MOONBOX_GOVERNANCE_CAPTURE_MODE','continuous')
    if invalid=='mode': monkeypatch.setenv('MOONBOX_GOVERNANCE_CAPTURE_MODE','typo')
    if invalid=='permissions': root.chmod(0o755)
    if invalid=='symlink':
        link=tmp_path/'link';link.symlink_to(root);monkeypatch.setenv('MOONBOX_GOVERNANCE_HOST_STATE_ROOT',str(link))
    with pytest.raises(ValueError): prepare(True)
