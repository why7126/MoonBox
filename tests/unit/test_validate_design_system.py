from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "validate-design-system.py"
SPEC = importlib.util.spec_from_file_location("validate_design_system", MODULE_PATH)
validate_design_system = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules["validate_design_system"] = validate_design_system
SPEC.loader.exec_module(validate_design_system)


def test_css_content_raw_non_ascii_is_rejected() -> None:
    assert validate_design_system.css_content_literal_uses_raw_non_ascii('content: "\u00b7";')
    assert validate_design_system.css_content_literal_uses_raw_non_ascii("content: '\u2713';")


def test_css_content_escape_and_ascii_literals_are_allowed() -> None:
    assert not validate_design_system.css_content_literal_uses_raw_non_ascii('content: "\\00B7";')
    assert not validate_design_system.css_content_literal_uses_raw_non_ascii('content: "\\2713";')
    assert not validate_design_system.css_content_literal_uses_raw_non_ascii('content: "*";')
    assert not validate_design_system.css_content_literal_uses_raw_non_ascii('content: "";')


def test_css_content_check_ignores_other_content_properties() -> None:
    assert not validate_design_system.css_content_literal_uses_raw_non_ascii("justify-content: center;")
    assert not validate_design_system.css_content_literal_uses_raw_non_ascii("align-content: start;")
