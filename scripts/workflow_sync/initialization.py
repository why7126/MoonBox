"""Initialize proposal facts without fabricating execution history."""
import re
import yaml
from .collect import read_text, parse_frontmatter_yaml
from .execution import atomic_write
from .shared import execution_metadata, change_state
from .timefmt import now_shanghai


def initialize(root, record, *, write=False):
    cid = record.change_id
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", cid):
        raise ValueError("Invalid Change ID")
    directory = root / "openspec/changes" / cid
    path = directory / "trace.md"
    if record.location != "active" or directory.is_symlink() or path.is_symlink() or directory.resolve() != directory.absolute():
        raise ValueError("Proposal requires a local active Change")
    original = read_text(path) if path.exists() else ""
    if path.exists():
        trace = parse_frontmatter_yaml(original)
        trace.update(execution_metadata(original))
        # The legacy lightweight parser does not support nested assessment maps.
        front = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", original, re.S)
        try:
            metadata = yaml.safe_load(front.group(1)) if front else {}
        except yaml.YAMLError as exc:
            raise ValueError("Invalid Change classification metadata") from exc
        if isinstance(metadata, dict) and 'classification' in metadata:
            trace['classification'] = metadata['classification']
        if trace.get("change_id", cid) != cid:
            raise ValueError("Change trace identity mismatch")
        if trace.get("status") not in {"proposed", "in_progress", "applied"}:
            raise ValueError("Change trace status missing or invalid; reconcile existing facts")
        execution = trace.get("execution")
        if execution is not None:
            required = {"schema_version", "started_at", "completed_at", "last_event"}
            if not isinstance(execution, dict) or not required <= execution.keys():
                raise ValueError("Incomplete Change execution schema")
            if trace["status"] != change_state(trace, 0, 0):
                raise ValueError("Change status conflicts with execution facts")
        return trace
    if record.tasks.done:
        raise ValueError("Missing trace with task progress; reconcile history before initialization")
    now = now_shanghai()
    title = "变更初始状态记录"
    text = (f"---\ntitle: {title}\nchange_id: {cid}\nstatus: proposed\n"
            f"created_at: {now}\nupdated_at: {now}\nexecution:\n"
            "  schema_version: 1\n  started_at: null\n  completed_at: null\n"
            f"  last_event: opsx.propose\n---\n# {title}\n\n"
            "## 登记说明\n本记录时间为状态登记时间，不代表原提案创建或历史执行时间。\n")
    if write:
        atomic_write(path, text, original)
    trace = parse_frontmatter_yaml(text)
    trace.update(execution_metadata(text))
    return trace
