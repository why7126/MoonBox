from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "git-check.py"
SPEC = importlib.util.spec_from_file_location("git_check", MODULE_PATH)
git_check = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules["git_check"] = git_check
SPEC.loader.exec_module(git_check)


def test_forbidden_paths_are_errors(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("APP_SECRET_KEY=real-secret", encoding="utf-8")
    (tmp_path / "data" / "runtime").mkdir(parents=True)
    (tmp_path / "data" / "runtime" / "app.db").write_text("db", encoding="utf-8")
    (tmp_path / "data" / "s3").mkdir(parents=True)
    (tmp_path / "data" / "s3" / "xl.meta").write_text("object storage", encoding="utf-8")

    findings = git_check.scan_paths({".env", "data/runtime/app.db", "data/s3/xl.meta"}, root=tmp_path)

    assert {finding.rule for finding in findings} == {"forbidden-path"}
    assert all(finding.severity == "error" for finding in findings)


def test_placeholder_values_do_not_error() -> None:
    content = """
Authorization: Bearer <access_token>
APP_SECRET_KEY=change-me-in-local-env
DATABASE_URL=mysql://example:example@localhost:3306/example
"""

    findings = git_check.scan_text_content("docs/example.md", content)

    assert findings == []


def test_real_authorization_header_is_redacted() -> None:
    token = "abcd1234" + "efgh5678ijkl9012mnop3456"
    findings = git_check.scan_text_content("docs/leak.md", f"Authorization: Bearer {token}\n")

    assert len(findings) == 1
    finding = findings[0]
    assert finding.severity == "error"
    assert finding.rule == "authorization-header"
    assert token not in finding.snippet
    assert "abcd" in finding.snippet
    assert "3456" in finding.snippet


def test_database_url_is_detected_and_redacted() -> None:
    url = "mysql://" + "moonbox:secret-password" + "@db.internal:3306/moonbox"
    findings = git_check.scan_text_content("docs/deploy.md", f"DATABASE_URL={url}\n")

    assert len(findings) == 1
    assert findings[0].rule == "database-url"
    assert url not in findings[0].snippet


def test_privacy_patterns_are_warnings() -> None:
    findings = git_check.scan_text_content("tests/fixture.txt", "user " + "alice" + "@private.test phone " + "138" + "00138000\n")

    assert {finding.rule for finding in findings} == {"privacy-email", "privacy-phone"}
    assert all(finding.severity == "warning" for finding in findings)


def test_local_absolute_path_is_error() -> None:
    findings = git_check.scan_text_content("docs/context.md", "local path /" + "Users/alice/project/file.md\n")

    assert len(findings) == 1
    assert findings[0].rule == "local-absolute-path"
    assert findings[0].severity == "error"


def test_directory_prefix_regex_is_not_a_user_path() -> None:
    content = "re.search(r'(?:/" + "Users/|/" + "home/|Authorization:|Bearer )', value)"
    assert git_check.scan_text_content("src/filter.py", content) == []


def test_concrete_paths_inside_regex_and_test_files_still_error() -> None:
    for root in ("Users", "home"):
        concrete = "/" + root + "/alice/project"
        for path, content in (
            ("src/filter.py", "re.search(r'" + concrete + "|other)', value)"),
            ("tests/test_private.py", concrete),
            ("docs/context.md", concrete),
        ):
            findings = git_check.scan_text_content(path, content)
            assert len(findings) == 1
            assert findings[0].rule == "local-absolute-path"
            assert findings[0].severity == "error"
            assert concrete not in findings[0].snippet


def test_explicit_example_path_uses_existing_placeholder_policy() -> None:
    content = "/" + "Users/example/secret"
    assert git_check.scan_text_content("tests/test_fixture.py", content) == []


PHONE = '138' + '00138000'
EMAIL = 'alice' + '@private.test'


def test_context_noise_is_suppressed_without_directory_exclusions() -> None:
    digest = 'a' * 25 + PHONE + 'b' * 28
    cases = [
        ('data/evidence.json', '{"fingerprint": "' + digest + '"}'),
        ('data/evidence.json', '{"wall_ms": 42.' + PHONE + '}'),
        ('data/evidence.jsonl', '{"wall_ms": 42.' + PHONE + '}'),
        ('src/fixture.py', r'"\n@app.get("/health")"'),
        ('src/git.py', "'user.email=" + 'integration@' + "moonbox.invalid'"),
    ]
    for path, content in cases:
        assert git_check.scan_text_content(path, content) == [], (path, content)


def test_privacy_survives_urls_hashes_and_test_directories() -> None:
    digest = 'a' * 25 + PHONE + 'b' * 28
    for path in ('tests/test_fixture.py', 'docs/example.md', 'data/evidence.json'):
        for content, rule in [
            ('https://example.org contact ' + EMAIL, 'privacy-email'),
            ('https://host.test/?email=' + EMAIL, 'privacy-email'),
            ('myexample' + '@private.test', 'privacy-email'),
            ('alice' + '@example.com.attacker.test', 'privacy-email'),
            (digest + ' phone=' + PHONE, 'privacy-phone'),
            ('{"phone": "42.' + PHONE + '"}', 'privacy-phone'),
            ('{"phone": ' + PHONE + '.0}', 'privacy-phone'),
            ('{"phone": ' + PHONE + '}', 'privacy-phone'),
            ('customer' + PHONE + 'xyz', 'privacy-phone'),
        ]:
            assert rule in {f.rule for f in git_check.scan_text_content(path, content)}, content


def test_placeholder_substrings_never_hide_credentials() -> None:
    for value in ('real-example-secret-123', 'real-localhost-secret-123',
                  'real-change-me-secret-123', 'real-replace-with-secret-123',
                  'real-secret?12345678', '${SECRET}real-secret-123'):
        findings = git_check.scan_text_content('docs/example.md', 'token = "' + value + '"')
        assert any(f.rule == 'assigned-secret' for f in findings), value
        url = 'mysql://' + 'admin:' + value + '@localhost:3306/db'
        assert any(f.rule == 'database-url' for f in git_check.scan_text_content('docs/example.md', url)), value


def test_exact_placeholder_forms_are_supported() -> None:
    for value in ('${ACCESS_TOKEN}', '<access_token>', 'replace-with-secret-key'):
        assert git_check.scan_text_content('docs/example.md', 'token = "' + value + '"') == []


def test_placeholder_username_is_not_a_substring_exemption() -> None:
    for name in ('alice-example', 'localhost-user', 'real?name'):
        content = '/' + 'Users/' + name + '/project'
        assert any(f.rule == 'local-absolute-path' for f in git_check.scan_text_content('docs/example.md', content))


def test_storage_templates_require_complete_safe_values() -> None:
    for value in ('${MINIO_SECRET_KEY}', '${MINIO_SECRET_KEY:-change-me}',
                  'replace-with-external-minio-secret-key'):
        assert git_check.scan_text_content('deploy/compose.yml', 'MINIO_SECRET_KEY: ' + value) == []
    for value in ('${MINIO_SECRET_KEY:-real-secret-value}', '${MINIO_SECRET_KEY}real-secret-value',
                  'real-example-secret-123', 'real-secret?12345'):
        assert any(f.rule == 'object-storage-credential' for f in git_check.scan_text_content(
            'deploy/compose.yml', 'MINIO_SECRET_KEY: ' + value)), value


def test_pypi_hash_exception_is_limited_to_digest_span() -> None:
    digest = 'a' * 25 + PHONE + 'b' * 24
    url = 'https://files.pythonhosted.org/packages/aa/bb/' + digest + '/package.whl'
    assert git_check.scan_text_content('uv.lock', url) == []
    assert any(f.rule == 'privacy-phone' for f in git_check.scan_text_content('uv.lock', url + '?phone=' + PHONE))
    assert any(f.rule == 'privacy-phone' for f in git_check.scan_text_content('uv.lock', url.replace('pythonhosted.org', 'attacker.test')))


def test_safe_value_does_not_hide_adjacent_secret_in_report() -> None:
    content = 'contact ' + EMAIL + ' token = "' + 'real-secret?123456789' + '"'
    findings = git_check.scan_text_content('docs/example.md', content)
    assert len(findings) == 2
    assert all(EMAIL not in f.snippet and 'real-secret?123456789' not in f.snippet for f in findings)


def test_decimal_string_and_python_literals_are_not_measurements() -> None:
    for path, content in [('evidence.json', '{"value": "escaped \\"42.' + PHONE + '"}'),
                          ('tests/fixture.py', 'value = 42.' + PHONE)]:
        assert any(f.rule == 'privacy-phone' for f in git_check.scan_text_content(path, content))


def test_compose_required_variable_and_unsafe_default() -> None:
    assert git_check.scan_text_content('deploy/compose.yml',
        'MINIO_SECRET_KEY: ${MINIO_SECRET_KEY:?Set external secret key}') == []
    for value in ('${ACCESS_TOKEN:-real-secret-value}', '<access_token>real-secret',
                  'replace-with-secret-key-real', 'secret?example.localhost'):
        assert any(f.rule == 'assigned-secret' for f in git_check.scan_text_content(
            'docs/example.md', 'token = "' + value + '"'))


def test_url_and_phone_exceptions_do_not_suppress_other_rules() -> None:
    token = 'a' * 25 + PHONE + 'b' * 28
    for content, rule in [
        ('Authorization: Bearer ' + token, 'authorization-header'),
        ('Cookie: sid=' + token, 'cookie-header'),
        ('token = "' + token + '"', 'assigned-secret'),
        ('mysql://' + 'example:real-password-123@localhost/db', 'database-url'),
    ]:
        assert any(f.rule == rule for f in git_check.scan_text_content('docs/example.md', content))
