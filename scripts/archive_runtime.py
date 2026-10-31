"""Separate deployment imports from the business repository for routed tools."""
from pathlib import Path
import sys

TOOL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOL_ROOT / 'src/backend'))
from app.governance.archive_tools import business_root


def repository_root(default):
    return business_root(default)
