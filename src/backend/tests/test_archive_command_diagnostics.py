"""The archive entry keeps safe failure reasons across its trusted subprocess."""
import os
from io import BytesIO
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from urllib.error import HTTPError

import pytest

from app.governance import replacement_executor
from app.chat.service import ChatError
from app.governance import replacement_archive_api
from app.governance import replacement_cli
from app.governance.replacement_archive_api import archive_failure


def _driver(tmp_path, monkeypatch):
    driver = replacement_executor.ArchiveDriver.__new__(replacement_executor.ArchiveDriver)
    driver.project = SimpleNamespace(root=tmp_path, key='test-scope', space_id='space', repository_id='repo',
                                     binding_revision='test-revision')
    driver.scripts = tmp_path / 'scripts'
    driver.scripts.mkdir()
    monkeypatch.setattr(driver, 'recheck_tools', lambda: None)
    return driver


def test_trusted_subprocess_can_import_backend_from_project_directory(tmp_path, monkeypatch):
    driver = _driver(tmp_path, monkeypatch)
    captured = {}
    real_run = subprocess.run

    def run(args, **kwargs):
        captured.update(args=args, **kwargs)
        return SimpleNamespace(returncode=0, stdout='', stderr='')

    monkeypatch.setattr(replacement_executor.subprocess, 'run', run)
    driver._run([sys.executable, str(driver.scripts / 'validate-change-identity.py')], tmp_path)
    assert captured['cwd'] == tmp_path
    assert captured['env']['PYTHONPATH'].split(os.pathsep)[0] == str(Path(replacement_executor.__file__).resolve().parents[2])
    imported = real_run([sys.executable, '-c', 'import app.governance.replacement_tool_context'],
                        cwd=tmp_path, env=captured['env'], capture_output=True, text=True)
    assert imported.returncode == 0, imported.stderr


@pytest.mark.parametrize(('stderr', 'expected'), [
    ("ModuleNotFoundError: No module named 'app'", 'archive_tool_runtime_unavailable'),
    ('', 'archive_check_failed_validate_change_delivery_evidence'),
])
def test_validator_failure_has_stable_safe_reason(tmp_path, monkeypatch, stderr, expected):
    driver = _driver(tmp_path, monkeypatch)
    monkeypatch.setattr(replacement_executor.subprocess, 'run', lambda *a, **k:
                        SimpleNamespace(returncode=1, stdout='', stderr=stderr))
    with pytest.raises(ValueError, match=f'^{expected}$'):
        driver._run([sys.executable, str(driver.scripts / 'validate-change-delivery-evidence.py')], tmp_path)


def test_public_archive_reason_is_allowlisted_without_internal_paths():
    message, details = archive_failure(ValueError('archive_check_failed_validate_change_delivery_evidence'))
    assert '交付证据' in message
    assert details['reason'] == 'archive_check_failed_validate_change_delivery_evidence'
    unknown_message, unknown_details = archive_failure(ValueError('secret /private/tmp/customer-data'))
    assert 'customer-data' not in unknown_message + str(unknown_details)
    assert unknown_details['reason'] == 'archive_failure_unclassified'


@pytest.mark.parametrize('reason', ('archive_tools_not_trusted', 'archive_tool_timeout',
                                   'archive_history_changed', 'original_operation_required'))
def test_common_archive_blockers_keep_stable_reason(reason):
    message, details = archive_failure(ValueError(reason))
    assert message
    assert details['reason'] == reason
    assert details['suggested_action']


def test_archive_command_preserves_safe_reason_in_response(monkeypatch):
    def fail(*a, **k):
        raise ValueError('archive_check_failed_validate_change_delivery_evidence')

    from app.governance import archive_dispatch
    monkeypatch.setattr(archive_dispatch, 'execute_object', fail)
    db = SimpleNamespace(rollback=lambda: None)
    request = SimpleNamespace(state=SimpleNamespace(chat_request_id='test-request'))
    payload = replacement_archive_api.ArchiveObjectRequest(
        space_id='space', repository_id='repo', object_id='isolated-standalone', confirmed=True)
    with pytest.raises(ChatError) as caught:
        replacement_archive_api.command(payload, request, {'id': 'alice'}, db)
    assert caught.value.status == 409
    assert caught.value.kind == 'archive_command_unverified'
    assert caught.value.details['reason'] == 'archive_check_failed_validate_change_delivery_evidence'
    assert '交付证据' in caught.value.message


def test_cli_keeps_only_allowlisted_online_archive_reason(monkeypatch):
    class Opener:
        def __init__(self, reason):
            self.reason = reason

        def open(self, *a, **k):
            body = ('{"data":{"reason":"' + self.reason + '"}}').encode()
            raise HTTPError('http://localhost', 409, 'Conflict', {}, BytesIO(body))

    import urllib.request
    monkeypatch.setattr(urllib.request, 'build_opener', lambda *a: Opener(
        'archive_check_failed_validate_change_delivery_evidence'))
    with pytest.raises(ValueError, match='^archive_check_failed_validate_change_delivery_evidence$'):
        replacement_cli.request({'base_url': 'http://localhost', 'access_token': 'test'}, 'archive-commands', {})
    monkeypatch.setattr(urllib.request, 'build_opener', lambda *a: Opener('secret_internal_path'))
    with pytest.raises(ValueError, match='^online_authority_unavailable_or_request_unverified$'):
        replacement_cli.request({'base_url': 'http://localhost', 'access_token': 'test'}, 'archive-commands', {})
