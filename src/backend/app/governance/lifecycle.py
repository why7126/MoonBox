"""Pure execution-state contract shared by governance readers and CLI writers."""
from __future__ import annotations

from collections.abc import Mapping
import re


def change_state(trace: Mapping, done: int, total: int, *, archived: bool = False) -> str:
    status = trace.get("status")
    if archived or status == "archived":
        return "archived"
    execution = trace.get("execution")
    if execution is not None:
        if not isinstance(execution, Mapping) or execution.get("schema_version") != 1:
            raise ValueError("Unsupported Change execution schema")
        if execution.get("completed_at"):
            if not execution.get("started_at"):
                raise ValueError("Completed execution has no start fact")
            return "applied"
        return "in_progress" if execution.get("started_at") else "proposed"
    # Legacy facts remain readable without inventing execution timestamps.
    if status == "applied":
        return "applied"
    if total > 0 and done >= total:
        return "applied"
    if status == "in_progress" or done > 0:
        return "in_progress"
    return "proposed"


def aggregate_states(states: list[str]) -> str | None:
    """Unfinished linked work prevents premature acceptance/closure."""
    if not states:
        return None
    for state in ("in_progress", "proposed", "applied", "archived"):
        if state in states:
            return state
    return None


def execution_metadata(text: str) -> dict:
    """Read the restricted flat execution block without a YAML dependency in CLI."""
    front = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not front:
        return {}
    match = re.search(r"^execution:\s*\n((?:[ \t]+[^\n]*(?:\n|$))*)", front.group(1), re.M)
    if not match:
        if re.search(r"^execution:", front.group(1), re.M):
            raise ValueError("Execution metadata must be a block mapping")
        return {}
    values = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.strip().partition(":")
        if not separator or key not in {"schema_version", "started_at", "completed_at", "last_event"}:
            raise ValueError("Invalid execution metadata field")
        value = value.strip().strip("\"'")
        values[key] = None if value in {"null", "~", ""} else (int(value) if key == "schema_version" and value.isdigit() else value)
    return {"execution": values}
