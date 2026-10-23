"""Opt-in isolated real worker with a bounded post-model/pre-terminal barrier.

This does not fabricate a model outcome: it delays recording an actual terminal
notification so browser assertions can observe already-written source files.
"""
import json
import os
from pathlib import Path
import time


def main():
    root = Path(os.environ['MOONBOX_GOVERNANCE_STATE_ROOT']).resolve().parent
    if os.environ.get('GOVERNANCE_TAIL_PROBE') != '1' or root.parent != Path('/private/tmp') or not root.name.startswith('moonbox-governance-live-'):
        raise RuntimeError('isolated explicit opt-in required')
    from app.governance import direct_command_journal as journal
    original = journal.terminal

    def delayed(conversation_id, client_id, status, workspace):
        from app.governance import store
        from app.chat.workspace import WorkspaceError
        try:
            record = store.read(journal.record_id(conversation_id, client_id), 'operation')
        except (FileNotFoundError, WorkspaceError):
            return original(conversation_id, client_id, status, workspace)
        already_terminal = record.get('phase') == 'terminal'
        result = original(conversation_id, client_id, status, workspace)
        if status == 'completed' and not already_terminal:
            (root / 'tail-observed.json').write_text(json.dumps({
                'conversation_id': conversation_id, 'status': status,
                'observed_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'barrier_seconds': 45,
            }))
            time.sleep(45)
        return result

    journal.terminal = delayed
    from app.chat.platform_worker import main as worker_main
    worker_main()


if __name__ == '__main__':
    main()
