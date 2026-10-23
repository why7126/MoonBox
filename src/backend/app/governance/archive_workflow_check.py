"""Read-only Workflow Sync check with narrowly scoped display-time compatibility."""
import re
import sys
from pathlib import Path


def timestamp_only_projection(path, root, change_id, before, after):
    """Ignore only this archived Change's derived display timestamp in Sprint prose."""
    try:
        relative = Path(path).relative_to(root).as_posix()
    except ValueError:
        return False
    if not re.fullmatch(r'iterations/(?:change|archive)/sprint-\d{3}/sprint\.md', relative):
        return False
    stamp = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
    pattern = rf'(archived `{re.escape(change_id)}`（){stamp}(）)'
    normalize = lambda value: re.sub(pattern, r'\1TIME\2', value)
    return before != after and normalize(before) == normalize(after)


def main(argv=None):
    root_arg, change_id = argv if argv is not None else sys.argv[1:]
    root = Path(root_arg).resolve()
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', change_id):
        return 2
    sys.path.insert(0, str(root / 'scripts'))
    from workflow_sync import patch
    from workflow_sync.engine import main as workflow_main
    original = patch.persist_markdown

    def readonly_projection(path, text, previous, write):
        if write:
            raise ValueError('archive_checker_write_forbidden')
        if timestamp_only_projection(path, root, change_id, previous, text):
            return False
        return original(path, text, previous, False)

    patch.persist_markdown = readonly_projection
    try:
        return workflow_main(['--event', 'opsx.archive', '--change', change_id,
                              '--sprint', 'auto', '--check'])
    finally:
        patch.persist_markdown = original


if __name__ == '__main__':
    raise SystemExit(main())
