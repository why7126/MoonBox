"""Deployment-only context for trusted validation and workflow subprocesses.

The pipe transports correlation, never approval or credentials. The child uses
the backend's private database access and reauthorizes the actor and fence. This
launcher and database environment must not be exposed to Agent containers.
"""
import os
from pathlib import Path
import runpy
import stat
import sys
from .replacement_proof import strict_json

SCRIPTS = frozenset({
    'validate-change-delivery-evidence.py', 'validate-change-identity.py',
    'validate-directory-structure.py', 'validate-openspec-language.py',
    'validate-env-ignore-policy.py', 'sync-workflow-status.py',
    'promote-issues-for-archive.py',
    'validate-sprint-archive-readiness.py', 'check-sprint-close-stale-scan.py',
})


def read_context(fd):
    if not stat.S_ISFIFO(os.fstat(fd).st_mode):
        raise ValueError('tool_context_requires_pipe')
    with os.fdopen(fd, 'rb') as stream:
        value = strict_json(stream.read(8193))
    if (set(value) != {'actor', 'space_id', 'repository_id', 'binding_revision', 'operation_id', 'fence'}
            or any(not isinstance(value[k], str) or not value[k] or len(value[k]) > 128
                   for k in ('actor', 'space_id', 'repository_id', 'binding_revision'))
            or (value['operation_id'] is None) != (value['fence'] is None)
            or value['operation_id'] is not None and (
                not isinstance(value['operation_id'], str) or not value['operation_id'] or len(value['operation_id']) > 128
                or type(value['fence']) is not int or value['fence'] < 1)):
        raise ValueError('invalid_tool_context')
    return value


def main():
    if len(sys.argv) < 3 or sys.argv[2] not in SCRIPTS:
        raise ValueError('untrusted_tool_entry')
    context = read_context(int(sys.argv[1]))
    from app.db.session import get_session_factory
    from .scope import authorize
    from .replacement_executor import ArchiveDriver
    from .controlled_successor import authority
    with get_session_factory()() as db:
        project = authorize(db, context['actor'], context['space_id'], context['repository_id'], write=True)
        if project.root.resolve() != Path.cwd().resolve() or project.binding_revision != context['binding_revision']:
            raise ValueError('tool_project_changed')
        # The trusted subprocess validates the current actor and fence. A
        # retired per-project installation record is not an archive gate.
        ArchiveDriver._trusted(project.root / 'scripts')
        if context['operation_id']:
            from sqlalchemy import select
            from .replacement_schema import commits
            operation = db.execute(select(commits).where(commits.c.id == context['operation_id'])).mappings().first()
            if operation:
                if operation['scope_key'] != project.key or operation['actor_id'] != context['actor']:
                    raise ValueError('tool_operation_changed')
                from .replacement_commit import assert_fence
                assert_fence(db, context['operation_id'], context['fence'])
            else:
                from .replacement_schema import archive_operations
                ordinary = db.execute(select(archive_operations).where(
                    archive_operations.c.id == context['operation_id'])).mappings().first()
                if ordinary:
                    if ordinary['scope_key'] != project.key or ordinary['actor_id'] != context['actor']:
                        raise ValueError('tool_operation_changed')
                    from .archive_coordinator import assert_fence
                else:
                    from .replacement_bootstrap_commit import assert_fence
                assert_fence(db, project, context['operation_id'], context['fence'])
        script = project.root / 'scripts' / sys.argv[2]
        sys.argv = [str(script), *sys.argv[3:]]
        sys.path.insert(0, str(script.parent))
        with authority(db, project, context['actor'], context['operation_id'], context['fence']):
            runpy.run_path(str(script), run_name='__main__')


if __name__ == '__main__':
    main()
