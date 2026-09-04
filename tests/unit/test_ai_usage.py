from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import ai_usage


def write_jsonl(path: Path, rows: list[dict], *, malformed: bool = False) -> None:
    lines = [json.dumps(row, ensure_ascii=False) for row in rows]
    if malformed:
        lines.append("{not-json")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_post_command_hook_auto_discovers_session_by_workflow_context(tmp_path, monkeypatch) -> None:
    sessions_dir = tmp_path / "sessions"
    sessions_dir.mkdir()
    write_jsonl(
        sessions_dir / "unrelated.jsonl",
        [
            {"type": "user_message", "text": "/req-capture REQ-0001"},
            {"payload": {"type": "token_count", "last_token_usage": {"total_tokens": 1}}},
        ],
    )
    write_jsonl(
        sessions_dir / "target.jsonl",
        [
            {"type": "user_message", "text": "/sprint-propose REQ-0038 sprint-007 add-demo-change"},
            {"payload": {"type": "token_count", "last_token_usage": {"input_tokens": 30, "output_tokens": 4, "total_tokens": 34}}},
        ],
    )
    monkeypatch.setenv("AI_USAGE_SESSIONS_DIR", str(sessions_dir))

    summary = ai_usage.post_command_hook(
        session_jsonl=None,
        out_dir=tmp_path / "ai-usage",
        workflow_event="sprint.propose",
        requirements=["REQ-0038-demo"],
        changes=["add-demo-change"],
        sprint_id="sprint-007",
    )

    assert summary["status"] == "ok"
    assert summary["usage_mode"] == "actual"
    assert summary["command_run_count"] == 1
    assert summary["session_input"] == "auto"
    assert summary["sprint_snapshot"]["status"] == "refreshed"
    assert str(tmp_path) not in json.dumps(summary)


def test_missing_session_recommends_default_discovery_locations(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("AI_USAGE_SESSIONS_DIR", str(tmp_path / "missing-sessions"))
    monkeypatch.delenv("AI_USAGE_SESSION_JSONL", raising=False)
    monkeypatch.delenv("CODEX_SESSION_JSONL", raising=False)

    summary = ai_usage.post_command_hook(
        session_jsonl=None,
        out_dir=tmp_path / "ai-usage",
        workflow_event="opsx.apply",
        changes=["apply-local-session-jsonl-governance"],
        sprint_id="sprint-004",
    )

    assert summary["status"] == "skipped"
    assert summary["usage_mode"] == "unavailable"
    assert "AI_USAGE_SESSIONS_DIR" in summary["recommended_action"]
    assert "~/.codex/sessions" in summary["recommended_action"]


def test_token_count_missing_recommends_auto_discovery_and_explicit_session(tmp_path) -> None:
    session = tmp_path / "session.jsonl"
    write_jsonl(session, [{"type": "user_message", "text": "/opsx-archive apply-local-session-jsonl-governance"}])

    summary = ai_usage.post_command_hook(
        session_jsonl=session,
        out_dir=tmp_path / "ai-usage",
        workflow_event="opsx.archive",
        changes=["apply-local-session-jsonl-governance"],
        sprint_id="sprint-004",
    )

    assert summary["status"] == "warning"
    assert summary["usage_mode"] == "estimated_fallback"
    assert "token-count-missing" in summary["warnings"]
    assert "AI_USAGE_SESSIONS_DIR" in summary["recommended_action"]
    assert "--session-jsonl" in summary["recommended_action"]


def test_post_command_hook_skips_unsafe_records_without_crashing(tmp_path) -> None:
    session = tmp_path / "session.jsonl"
    write_jsonl(
        session,
        [
            {"type": "user_message", "text": "/opsx-apply apply-local-session-jsonl-governance"},
            {"payload": {"type": "token_count", "last_token_usage": {"total_tokens": 10}}},
        ],
    )

    summary = ai_usage.post_command_hook(
        session_jsonl=session,
        out_dir=tmp_path / "ai-usage",
        workflow_event="opsx.apply",
        changes=["/Users/example/unsafe-change"],
        sprint_id="sprint-004",
    )

    assert summary["status"] == "warning"
    assert summary["usage_mode"] == "unavailable"
    assert summary["command_run_count"] == 0
    assert "unsafe-records-skipped:1" in summary["warnings"]
    assert "no-safe-command-runs" in summary["warnings"]
