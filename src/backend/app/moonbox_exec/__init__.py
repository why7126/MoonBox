"""moonbox-exec: noninteractive adapter using a server-authenticated actor, never a browser role."""
from app.moonbox_core import service


def workspace_operation(db, actor, operation, *, space_id, repository_id, **payload):
    if operation == 'workspace.list':
        return service.list_workspaces(db, actor, space_id, repository_id)
    if operation == 'workspace.register_main':
        return service.register_main(db, actor, space_id, repository_id)
    if operation == 'workspace.create_development':
        return service.create_development(db, actor, space_id, repository_id, payload['change_id'])
    if operation == 'workspace.create_session':
        return service.new_session(db, actor, space_id, repository_id, **payload)
    if operation == 'workspace.cleanup':
        from app.moonbox_core.lifecycle import remove
        return remove(db, actor, space_id, repository_id, **payload)
    if operation == 'recovery.preflight':
        from app.moonbox_rollout.restore import preview
        return preview(db, actor, space_id, repository_id, **payload)
    if operation == 'merge.prepare':
        from app.moonbox_core.integration import prepare
        return prepare(db, actor, space_id, repository_id, **payload)
    if operation == 'merge.confirm':
        from app.moonbox_core.integration import confirm
        return confirm(db, actor, space_id, repository_id, **payload)
    raise ValueError('unsupported_workspace_operation')


def acceptance_operation(db, factory, actor, operation, **payload):
    """Use the same authorization and state guards as HTTP; no caller commands or paths."""
    from app.verification import acceptance_service
    if operation == 'acceptance.create':
        return acceptance_service.create(db,factory,actor,payload['conversation_id'],payload['source_turn_id'],
            payload['change_id'],payload['client_request_id'])
    if operation == 'acceptance.read':
        return acceptance_service.read(db,factory,actor,payload['operation_id'])
    if operation == 'acceptance.stop':
        return acceptance_service.stop(db,factory,actor,payload['operation_id'],payload['version'])
    if operation in {'acceptance.resume','acceptance.cleanup-retries'}:
        return acceptance_service.action(db,factory,actor,payload['operation_id'],payload['version'],operation.split('.',1)[1])
    raise ValueError('unsupported_acceptance_operation')
