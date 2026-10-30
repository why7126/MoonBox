#!/usr/bin/env python3
"""Pre-push safety checks for staged/tracked Git content."""

from __future__ import annotations

import argparse
import fnmatch
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAX_FILE_SIZE_MB = 10
TEXT_READ_LIMIT_BYTES = 1024 * 1024

PLACEHOLDER_VALUES = {
    "<access_token>",
    "<token>",
    "<secret>",
    "<password>",
    "<api_key>",
    "<api-key>",
    "change-me",
    "change-me-in-local-env",
    "example",
    "example.com",
    "localhost",
    "127.0.0.1",
    "replace-with-example-key",
    "replace-with-access-key",
    "replace-with-secret-key",
    "replace-with-s3-access-key",
    "replace-with-s3-secret-key",
    "replace-with-external-minio-access-key",
    "replace-with-external-minio-secret-key",
}

SAFE_PATH_PATTERNS = [
    ".env.example",
    "**/.env.example",
    "deploy/**/*.env.example",
    "scripts/build-images.env.example",
]

FORBIDDEN_PATH_PATTERNS = [
    ".env",
    ".env.*",
    "deploy/**/*.env",
    "scripts/build-images.env",
    "*.sqlite",
    "*.sqlite3",
    "*.db",
    "data/runtime/**",
    "data/sqlite/**",
    "data/uploads/**",
    "data/processed/**",
    "data/tmp/**",
    "data/minio/**",
    "data/s3/**",
    "data/mysql/**",
    "mintlify/.mintlify/**",
    "mintlify/dist/**",
    "mintlify/build/**",
    "dist/**",
    "build/**",
    "coverage/**",
    ".pytest_cache/**",
    "__pycache__/**",
    "*.pyc",
    ".DS_Store",
    "*.zip",
]

BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".gz",
    ".tar",
    ".tgz",
    ".sqlite",
    ".sqlite3",
    ".db",
}


@dataclass(frozen=True)
class Finding:
    severity: str
    rule: str
    path: str
    line: int | None
    message: str
    snippet: str | None = None


def run_git(args: list[str], root: Path = ROOT) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def staged_files(root: Path = ROOT) -> set[str]:
    return set(run_git(["diff", "--cached", "--name-only", "--diff-filter=ACMR"], root))


def tracked_files(root: Path = ROOT) -> set[str]:
    return set(run_git(["ls-files"], root))


def all_files(root: Path = ROOT) -> set[str]:
    files: set[str] = set()
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith(".git/") or "/.git/" in rel:
            continue
        files.add(rel)
    return files


def collect_scan_files(scan_all: bool, root: Path = ROOT) -> tuple[str, set[str]]:
    if scan_all:
        return "all", all_files(root)
    return "staged+tracked", staged_files(root) | tracked_files(root)


def path_matches(path: str, pattern: str) -> bool:
    if pattern.endswith("/**"):
        prefix = pattern[:-3]
        return path == prefix or path.startswith(f"{prefix}/")
    return fnmatch.fnmatch(path, pattern)


def is_forbidden_path(path: str) -> str | None:
    if any(path_matches(path, pattern) for pattern in SAFE_PATH_PATTERNS):
        return None
    for pattern in FORBIDDEN_PATH_PATTERNS:
        if path_matches(path, pattern):
            return pattern
    return None


def scan_paths(paths: set[str], root: Path = ROOT, max_file_size_mb: int = DEFAULT_MAX_FILE_SIZE_MB) -> list[Finding]:
    findings: list[Finding] = []
    max_bytes = max_file_size_mb * 1024 * 1024
    for path in sorted(paths):
        forbidden_pattern = is_forbidden_path(path)
        if forbidden_pattern:
            findings.append(
                Finding(
                    severity="error",
                    rule="forbidden-path",
                    path=path,
                    line=None,
                    message=f"路径匹配禁止提交规则: {forbidden_pattern}",
                )
            )

        full_path = root / path
        if full_path.exists() and full_path.is_file():
            try:
                size = full_path.stat().st_size
            except OSError:
                continue
            if size > max_bytes:
                severity = "error" if full_path.suffix.lower() in BINARY_EXTENSIONS else "warning"
                findings.append(
                    Finding(
                        severity=severity,
                        rule="large-file",
                        path=path,
                        line=None,
                        message=f"文件超过阈值 {max_file_size_mb}MB",
                    )
                )
    return findings


SECRET_PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    (
        "authorization-header",
        re.compile(r"\bAuthorization\s*:\s*Bearer\s+([A-Za-z0-9._~+/=-]{16,})", re.IGNORECASE),
        "error",
    ),
    (
        "cookie-header",
        re.compile(r"\bCookie\s*:\s*([^;\s=]+=[^;\s]{12,})", re.IGNORECASE),
        "error",
    ),
    (
        "assigned-secret",
        re.compile(
            r"\b(api[_-]?key|access[_-]?key|secret[_-]?key|secret|token|password)\b\s*[:=]\s*[\"']([^\"']{12,})[\"']",
            re.IGNORECASE,
        ),
        "error",
    ),
    (
        "database-url",
        re.compile(r"\b(?:mysql|postgresql|postgres):\/\/[^\s\"']{12,}", re.IGNORECASE),
        "error",
    ),
    (
        "object-storage-credential",
        re.compile(r"(?<![\w${])(?:MINIO|S3|OBJECT_STORAGE)_[A-Z0-9_]*(?:KEY|SECRET|TOKEN)\b\s*[:=]\s*[\"']?(\$\{[^}\n]+\}[^\"'\s,}]*|[^\"'\s}]{12,})"),
        "error",
    ),
    (
        "local-absolute-path",
        re.compile(r"(?<![\w.-])(?:/" + r"Users/(?!\|)[^ \t\n\"'`]+|/" + r"home/(?!\|)[^ \t\n\"'`]+)"),
        "error",
    ),
    (
        "privacy-email",
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "warning",
    ),
    ("privacy-phone", re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"), "warning"),
]


def is_placeholder(value: str) -> bool:
    """Only complete, documented template values are safe; substrings are not."""
    return value.lower() in PLACEHOLDER_VALUES or bool(
        re.fullmatch(r"\$\{[A-Z_][A-Z0-9_]*(?::-change-me|:\?[^{}\n]+)?\}", value)
    )


def is_safe_match(rule: str, value: str, line: str, match: re.Match[str]) -> bool:
    if rule == "privacy-email":
        domain = value.rsplit("@", 1)[-1].lower()
        if domain in {"example.com", "example.org", "example.invalid"}:
            return True
        # Reserved integration identity only in Git's explicit author setting.
        if value == "integration@" + "moonbox.invalid" and line[max(0, match.start()-11):match.start()] == "user.email=":
            return True
        # An escaped source newline before a Python HTTP decorator is not email.
        return bool(re.fullmatch(r"[nr]@[A-Za-z_]\w*\.(?:get|post|put|patch|delete|head|options)", value)
                    and match.start() > 0 and line[match.start()-1] == "\\"
                    and line[match.end():].lstrip().startswith("("))
    if rule == "local-absolute-path":
        username = value.split("/", 3)[2]
        return username in {"example", "<name>", "<local-project>"}
    if rule == "database-url":
        try:
            parsed = urlsplit(value)
            return (parsed.username is not None and parsed.password is not None
                    and is_placeholder(parsed.username) and is_placeholder(parsed.password)
                    and not parsed.query and not parsed.fragment)
        except ValueError:
            return False
    return is_placeholder(value)


def phone_noise_spans(path: str, line: str) -> list[tuple[int, int]]:
    """Bound exceptions to a complete hash or the fractional part of a JSON number."""
    spans = []
    for token in re.finditer(r"(?<![\w-])[a-fA-F0-9]{64}(?![\w-])", line):
        if re.search(r"[a-fA-F]", token.group()):
            spans.append(token.span())
    # PyPI artifact paths split the SHA256 into 2/2/60 hexadecimal digits.
    for token in re.finditer(r"https://files\.pythonhosted\.org/packages/[a-f0-9]{2}/[a-f0-9]{2}/([a-f0-9]{60})/", line):
        spans.append(token.span(1))
    if Path(path).suffix.lower() in {".json", ".jsonl"}:
        # Consume quoted strings first so a string containing digits stays visible.
        for token in re.finditer(r'"(?:\\.|[^"\\])*"|(?<![\w.])-?\d+\.\d+(?:[eE][+-]?\d+)?(?![\w.])', line):
            value = token.group()
            if not value.startswith('"'):
                spans.append((token.start() + value.index(".") + 1, token.end()))
    return spans


def redact(value: str) -> str:
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}...{value[-4:]}"


def redacted_line(line: str, match: re.Match[str]) -> str:
    groups = [group for group in match.groups() if group]
    target = groups[-1] if groups else match.group(0)
    redacted = redact(target)
    if len(redacted) > 180:
        return f"{redacted[:177]}..."
    return redacted


def is_probably_binary(path: Path) -> bool:
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return True
    try:
        sample = path.read_bytes()[:1024]
    except OSError:
        return True
    return b"\0" in sample


def scan_text_content(path: str, content: str) -> list[Finding]:
    findings: list[Finding] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        noise_spans = phone_noise_spans(path, line)
        database_spans = [m.span() for name, pattern, _ in SECRET_PATTERNS if name == "database-url" for m in pattern.finditer(line)]
        for rule, pattern, severity in SECRET_PATTERNS:
            for match in pattern.finditer(line):
                if rule == "privacy-email" and any(start <= match.start() and match.end() <= end for start, end in database_spans):
                    continue
                value = next((group for group in reversed(match.groups()) if group), match.group(0))
                if rule == "privacy-phone" and any(start <= match.start() and match.end() <= end for start, end in noise_spans):
                    continue
                if is_safe_match(rule, value, line, match):
                    continue
                findings.append(
                    Finding(
                        severity=severity,
                        rule=rule,
                        path=path,
                        line=line_number,
                        message="检测到疑似敏感内容",
                        snippet=redacted_line(line, match),
                    )
                )
    return findings


def scan_file_contents(paths: set[str], root: Path = ROOT) -> list[Finding]:
    findings: list[Finding] = []
    for rel_path in sorted(paths):
        path = root / rel_path
        if not path.exists() or not path.is_file() or is_probably_binary(path):
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")[:TEXT_READ_LIMIT_BYTES]
        except OSError:
            continue
        findings.extend(scan_text_content(rel_path, content))
    return findings


def run_env_ignore_policy(root: Path = ROOT) -> list[Finding]:
    script = root / "scripts" / "validate-env-ignore-policy.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode == 0:
        return []
    output = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part)
    return [
        Finding(
            severity="error",
            rule="env-ignore-policy",
            path="scripts/validate-env-ignore-policy.py",
            line=None,
            message=output or "环境文件 ignore 策略校验失败",
        )
    ]


def format_finding(finding: Finding) -> str:
    location = finding.path if finding.line is None else f"{finding.path}:{finding.line}"
    suffix = f" | {finding.snippet}" if finding.snippet else ""
    return f"- [{finding.rule}] {location} — {finding.message}{suffix}"


def print_report(scan_scope: str, scanned_count: int, findings: list[Finding]) -> None:
    errors = [finding for finding in findings if finding.severity == "error"]
    warnings = [finding for finding in findings if finding.severity == "warning"]

    print("## Git Check Report")
    print()
    print(f"- scan_scope: {scan_scope}")
    print(f"- scanned_files: {scanned_count}")
    print(f"- errors: {len(errors)}")
    print(f"- warnings: {len(warnings)}")
    print()

    if errors:
        print("### Errors")
        for finding in errors:
            print(format_finding(finding))
        print()

    if warnings:
        print("### Warnings")
        for finding in warnings:
            print(format_finding(finding))
        print()

    if not findings:
        print("### Pass")
        print("- 未发现 staged/tracked 范围内的 Git 安全门禁问题。")
        print()

    print("### 修复建议")
    if errors:
        print("- 从 Git staged/tracked 范围移除真实环境文件、运行时数据、数据库文件和敏感内容。")
        print("- 将真实配置改放本地 `.env`，提交 `.env.example` 占位示例。")
        print("- 对文档、日志或测试 fixture 中的敏感内容做脱敏处理后重跑检查。")
    else:
        print("- 可继续后续提交或推送流程；如需深度复核可运行 `python scripts/git-check.py --all`。")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run pre-push Git safety checks; exact template values and bounded hash/JSON contexts only; URLs do not exempt a line.")
    parser.add_argument("--all", action="store_true", help="Scan all repository files instead of staged + tracked files.")
    parser.add_argument(
        "--max-file-size-mb",
        type=int,
        default=DEFAULT_MAX_FILE_SIZE_MB,
        help=f"Large-file warning/error threshold. Default: {DEFAULT_MAX_FILE_SIZE_MB}.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    scan_scope, paths = collect_scan_files(scan_all=args.all)
    findings: list[Finding] = []
    findings.extend(run_env_ignore_policy())
    findings.extend(scan_paths(paths, max_file_size_mb=args.max_file_size_mb))
    findings.extend(scan_file_contents(paths))
    print_report(scan_scope, len(paths), findings)
    return 1 if any(finding.severity == "error" for finding in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
