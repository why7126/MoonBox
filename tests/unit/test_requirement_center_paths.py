from pathlib import Path

from app.services import requirement_center


def test_requirement_center_root_prefers_env_for_shallow_container_path(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("MOONBOX_GOVERNANCE_ROOT", str(tmp_path))

    resolved = requirement_center._resolve_governance_root(Path("/app/app/services/requirement_center.py"))

    assert resolved == tmp_path.resolve()


def test_requirement_center_root_fallback_handles_shallow_container_path(monkeypatch) -> None:
    monkeypatch.delenv("MOONBOX_GOVERNANCE_ROOT", raising=False)

    resolved = requirement_center._resolve_governance_root(Path("/app/app/services/requirement_center.py"))

    assert resolved.is_absolute()
