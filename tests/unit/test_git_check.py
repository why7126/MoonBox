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
    token = "abcd1234efgh5678ijkl9012mnop3456"
    findings = git_check.scan_text_content("docs/leak.md", f"Authorization: Bearer {token}\n")

    assert len(findings) == 1
    finding = findings[0]
    assert finding.severity == "error"
    assert finding.rule == "authorization-header"
    assert token not in finding.snippet
    assert "abcd" in finding.snippet
    assert "3456" in finding.snippet


def test_database_url_is_detected_and_redacted() -> None:
    url = "mysql://moonbox:secret-password@db.internal:3306/moonbox"
    findings = git_check.scan_text_content("docs/deploy.md", f"DATABASE_URL={url}\n")

    assert len(findings) == 1
    assert findings[0].rule == "database-url"
    assert url not in findings[0].snippet


def test_privacy_patterns_are_warnings() -> None:
    findings = git_check.scan_text_content("tests/fixture.txt", "user alice@private.test phone 13800138000\n")

    assert {finding.rule for finding in findings} == {"privacy-email", "privacy-phone"}
    assert all(finding.severity == "warning" for finding in findings)


def test_local_absolute_path_is_error() -> None:
    findings = git_check.scan_text_content("docs/context.md", "local path /Users/alice/project/file.md\n")

    assert len(findings) == 1
    assert findings[0].rule == "local-absolute-path"
    assert findings[0].severity == "error"
