from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "validate-openspec-language.py"


def write_change(
    root: Path,
    change_id: str,
    proposal: str = "# 背景\n\n中文内容\n",
    tasks: str = "- [ ] 中文任务\n",
) -> None:
    change_dir = root / "openspec" / "changes" / change_id
    change_dir.mkdir(parents=True)
    (change_dir / "proposal.md").write_text(proposal, encoding="utf-8")
    (change_dir / "tasks.md").write_text(tasks, encoding="utf-8")


def run_validator(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def test_focused_change_failure_blocks_current_change(tmp_path: Path) -> None:
    write_change(tmp_path, "target", proposal="# Why\n\nEnglish scaffold\n")
    write_change(tmp_path, "other")

    result = run_validator(tmp_path, "--change", "target", "--residual-report")

    assert result.returncode == 1
    assert "OpenSpec 当前 Change 中文校验失败" in result.stdout
    assert "openspec/changes/target/proposal.md" in result.stdout
    assert "openspec/changes/other" not in result.stdout


def test_residual_report_does_not_block_focused_success(tmp_path: Path) -> None:
    write_change(tmp_path, "target")
    write_change(tmp_path, "other", proposal="# Why\n\nEnglish scaffold\n")

    result = run_validator(tmp_path, "--change", "target", "--residual-report")

    assert result.returncode == 0
    assert "OpenSpec 当前 Change 中文校验通过：target" in result.stdout
    assert "全仓残留分离报告" in result.stdout
    assert "非当前 Change 中文残留：1 项" in result.stdout
    assert "openspec/changes/other/proposal.md" in result.stdout


def test_missing_focused_change_is_an_error(tmp_path: Path) -> None:
    result = run_validator(tmp_path, "--change", "missing", "--residual-report")

    assert result.returncode == 2
    assert "未找到 Change：missing" in result.stdout
