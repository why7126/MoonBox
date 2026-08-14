#!/usr/bin/env python3
"""Verify Docker media upload using resolved ports and a disposable test user."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import mimetypes
import os
import secrets
import sqlite3
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

HASH_ITERATIONS = 120_000
DEFAULT_WEB_PORT = "18102"
DEFAULT_BACKEND_DB = Path("data/runtime/backend/sqlite/moonbox.db")
USERNAME_PREFIX = "media_probe_"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def resolved_value(key: str, default: str, env_file: Path) -> str:
    return os.environ.get(key) or read_env_file(env_file).get(key) or default


def web_base_url(env_file: Path) -> str:
    port = resolved_value("HOST_PORT_WEB", DEFAULT_WEB_PORT, env_file)
    return f"http://localhost:{port}"


def hash_password(password: str, *, salt: str | None = None) -> str:
    salt_value = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_value.encode("utf-8"), HASH_ITERATIONS)
    return f"pbkdf2_sha256${HASH_ITERATIONS}${salt_value}${digest.hex()}"


def verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False
    try:
        algorithm, iterations_text, salt, expected = password_hash.split("$", 3)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), int(iterations_text))
    return hmac.compare_digest(digest.hex(), expected)


def prepare_test_user(db_path: Path, username: str, password: str) -> None:
    if not db_path.exists():
        raise RuntimeError("runtime sqlite database is missing; start Docker backend before verification")
    now = _now()
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO admin_users (
                id, username, nickname, avatar_url, role, status, workspace_count,
                status_before_freeze, last_login_at, password_hash, is_system_superadmin,
                deleted_at, session_invalidated_at, created_at, updated_at
            ) VALUES (?, ?, ?, NULL, '前台用户', '正常', 0, NULL, NULL, ?, 0, NULL, NULL, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                nickname = excluded.nickname,
                avatar_url = NULL,
                role = '前台用户',
                status = '正常',
                status_before_freeze = NULL,
                password_hash = excluded.password_hash,
                session_invalidated_at = NULL,
                updated_at = excluded.updated_at
            """,
            (f"user_{uuid4().hex}", username, "Media Upload Probe", hash_password(password), now, now),
        )


def http_json(url: str, *, method: str = "GET", headers: dict[str, str] | None = None, payload: dict | None = None) -> dict:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request_headers = {"content-type": "application/json"}
    if headers:
        request_headers.update(headers)
    request = urllib.request.Request(url, data=body, headers=request_headers, method=method)
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def multipart_body(field: str, filename: str, content: bytes, content_type: str) -> tuple[bytes, str]:
    boundary = f"----MoonBoxBoundary{uuid4().hex}"
    lines = [
        f"--{boundary}\r\n".encode(),
        f'Content-Disposition: form-data; name="{field}"; filename="{filename}"\r\n'.encode(),
        f"Content-Type: {content_type}\r\n\r\n".encode(),
        content,
        b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    return b"".join(lines), boundary


def upload_avatar(base_url: str, token: str, file_path: Path) -> str:
    content = file_path.read_bytes()
    content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    body, boundary = multipart_body("file", file_path.name, content, content_type)
    request = urllib.request.Request(
        f"{base_url}/api/v1/auth/avatar",
        data=body,
        headers={"authorization": f"Bearer {token}", "content-type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload["data"]["url"]


def run_verification(env_file: Path, db_path: Path, file_path: Path) -> dict[str, object]:
    base_url = web_base_url(env_file)
    username = f"{USERNAME_PREFIX}{uuid4().hex[:10]}"
    password = f"Mb-Probe-{secrets.token_urlsafe(12)}1!"
    prepare_test_user(db_path, username, password)

    login = http_json(
        f"{base_url}/api/v1/auth/login",
        method="POST",
        payload={"username": username, "password": password, "remember_me": False},
    )
    token = login["data"]["access_token"]
    avatar_url = upload_avatar(base_url, token, file_path)
    media_request = urllib.request.Request(f"{base_url}{avatar_url}", headers={"authorization": f"Bearer {token}"})
    with urllib.request.urlopen(media_request, timeout=15) as media_response:
        media_bytes = media_response.read()
        media_status = media_response.status

    updated = http_json(
        f"{base_url}/api/v1/auth/me",
        method="PATCH",
        headers={"authorization": f"Bearer {token}"},
        payload={"nickname": "Media Upload Probe", "avatar_url": avatar_url},
    )
    echoed = updated["data"]["user"]["avatar_url"] == avatar_url
    return {
        "status": "passed",
        "web_port": urllib.parse.urlparse(base_url).port,
        "test_identity": "script-prepared-front-user",
        "username_prefix": USERNAME_PREFIX,
        "login": "passed",
        "upload": "passed",
        "protected_read": "passed" if media_status == 200 and media_bytes == file_path.read_bytes() else "failed",
        "profile_echo": "passed" if echoed else "failed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Docker media upload without fixed ports or default admin password.")
    parser.add_argument("--env-file", default=".env", help="Optional env file used to resolve HOST_PORT_WEB.")
    parser.add_argument("--db-path", default=str(DEFAULT_BACKEND_DB), help="Host SQLite database path for Docker local mode.")
    parser.add_argument("--file", required=True, help="Image file to upload.")
    args = parser.parse_args()

    try:
        result = run_verification(Path(args.env_file), Path(args.db_path), Path(args.file))
    except (RuntimeError, urllib.error.URLError, KeyError, sqlite3.Error) as exc:
        print(json.dumps({"status": "failed", "reason": str(exc).splitlines()[0]}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
