"""Adapters for the existing parser operating on an authorized stable snapshot."""
import hashlib
import json
import logging
from time import perf_counter
from urllib.parse import urlencode
import yaml
from sqlalchemy import select
from app.chat.service import ChatError
from app.governance import scope as scopes
from app.governance.snapshot import stable, materialize, cached_materialize, safe_load, Snapshot
from app.services import requirement_center as legacy


class ProjectReader:
    def __init__(self, db, actor, scope):
        self.db, self.actor, self.scope = db, actor, scope

    def snapshot(self):
        from app.governance.writer import assert_readable, epoch
        before_epoch = epoch(self.db, self.scope)
        assert_readable(self.db, self.scope)
        from app.governance.read_snapshot import stable_read
        snapshot_start = perf_counter()
        result = stable_read(self.scope.root, self.scope.binding_revision)
        self.snapshot_ms = (perf_counter() - snapshot_start) * 1000
        # End the read transaction so MySQL REPEATABLE READ cannot hide a writer
        # that started after the first fence check. No writes are pending here.
        self.db.commit()
        assert_readable(self.db, self.scope)
        if before_epoch != epoch(self.db, self.scope):
            raise ChatError(2603, "项目写入版本已推进，请重新读取完整快照", 503)
        current = scopes.authorize(self.db, self.actor, self.scope.space_id, self.scope.repository_id)
        if current.binding_revision != self.scope.binding_revision:
            raise ChatError(2606, "项目绑定已变化，请重新读取", 409)
        return result

    def entries(self, snapshot):
        index = getattr(self, '_identities', None)
        if index is not None and index.snapshot is snapshot:
            return [entry for folder in ('requirements', 'bugs') for entry in index.registry(folder)['entries']]
        return [entry for folder in ('requirements','bugs')
                for entry in safe_load(snapshot.files[f'issues/{folder}/_registry.yaml'])['entries']]

    def authorize_object(self, snapshot, object_id, change=False, root=None, write=False):
        entries = self.entries(snapshot)
        if change:
            if root is None:
                with materialize(snapshot) as root, legacy.using_governance_root(root):
                    return self.authorize_object(snapshot, object_id, change=True, root=root, write=write)
            from app.governance.change_index import ChangeIndex
            index = ChangeIndex(root)
            record = index.records.get(object_id)
            if not record or not record.visible(lambda oid: scopes.visible(self.db, self.actor, self.scope, oid)):
                raise ChatError(2601, '对象不存在或无权访问', 403)
            if not record.directory:
                raise FileNotFoundError('Change 不存在或归档版本不唯一')
            linked = [index.entries[oid][1] for oid in sorted(record.issue_ids)]
            if write:
                # New read-only source associations do not expand legacy writes.
                linked = [entry for entry in linked if object_id in legacy._linked_changes(entry,
                    legacy._frontmatter(root / entry['path'] / 'trace.md'))]
                if record.issue_ids and not linked:
                    raise ChatError(2601, '该 Change 入口仅支持读取', 403)
            return linked
        else:
            entries = [entry for entry in entries if entry['id']==object_id or '-'.join(entry['id'].split('-')[:2])==object_id]
        if not entries or (not change and len(entries)!=1) or any(not scopes.visible(self.db,self.actor,self.scope,e['id']) for e in entries):
            raise ChatError(2601,'对象不存在或无权访问',403)
        return entries

    def call(self, name, *args, **kwargs):
        timings = {}
        start = perf_counter()
        success = False
        try:
            result = self._call(name, args, kwargs, timings)
            success = True
            return result
        finally:
            timings["total_ms"] = round((perf_counter() - start) * 1000, 2)
            exclusive = ('snapshot_and_fences_ms', 'materialize_ms', 'object_authorization_ms',
                         'parse_ms', 'cleanup_ms', 'reconcile_ms', 'external_reconcile_ms',
                         'card_projection_exclusive_ms', 'projection_commit_ms', 'document_projection_ms')
            timings['reader_orchestration_ms'] = round(max(0, timings['total_ms'] -
                sum(timings.get(key, 0) for key in exclusive)), 2)
            self.timings = dict(timings)
            logging.getLogger("moonbox.requirement_center").info("requirement_center.read_timing %s", json.dumps({
                "request_id": getattr(self, "request_id", ""), "operation": name,
                "success": success, "timings": timings,
            }))

    def _call(self, name, args, kwargs, timings):
        start = perf_counter()
        snapshot=self.snapshot()
        timings["snapshot_and_fences_ms"] = round((perf_counter() - start) * 1000, 2)
        if hasattr(self, 'snapshot_ms'):
            timings['snapshot_ms'] = round(self.snapshot_ms, 2)
            timings['fences_exclusive_ms'] = round(max(0, timings['snapshot_and_fences_ms'] - self.snapshot_ms), 2)
        if name.startswith('update_'):
            if self.scope.readonly: raise ChatError(2601,'当前空间只读',403)
            # Every old write entrance fails closed until the trusted writer is installed.
            raise ChatError(2605,'受控写入服务尚未就绪，文档保持只读',503)
        files=dict(snapshot.files)
        from app.governance.execution_context import IdentityIndex
        self._identities = IdentityIndex(snapshot)
        start = perf_counter()
        with cached_materialize(Snapshot(files,snapshot.revision), (str(self.scope.root), self.scope.binding_revision)) as root, legacy.using_governance_root(root, immutable=True, evidence_root=self.scope.root, evidence_source_root=getattr(self.scope, "source_root", None), registry_index=self._identities, shared_memo=True):
            timings["materialize_ms"] = round((perf_counter() - start) * 1000, 2)
            start = perf_counter()
            if name != 'build_requirement_center_context':
                entries = self.authorize_object(snapshot, args[0], change='change_document' in name, root=root)
                if 'change_document' not in name: args = (entries[0]['id'], *args[1:])
            timings["object_authorization_ms"] = round((perf_counter() - start) * 1000, 2)
            start = perf_counter()
            if name == 'build_requirement_center_context':
                visibility = scopes.RequestVisibility(self.db, self.actor, self.scope)
                kwargs = {**kwargs, 'owner_space_id': self.scope.space_id,
                          'visibility': visibility.visible}
            from .controlled_successor import authority
            with authority(self.db, self.scope, self.actor):
                result=getattr(legacy,name)(*args,**kwargs)
            timings["parse_ms"] = round((perf_counter() - start) * 1000, 2)
            start = perf_counter()
        timings["cleanup_ms"] = round((perf_counter() - start) * 1000, 2)
        if name == 'build_requirement_center_context':
            result.selected_workspace_id=self.scope.space_id
            result.repository_id=self.scope.repository_id
            result.snapshot_revision=snapshot.revision
            result.sync_status='ready'
            for sprint in result.current_iteration_capacity:
                if self.scope.readonly or not scopes.visible(self.db, self.actor, self.scope, sprint.sprint_id):
                    sprint.archive_readiness.can_enter_confirmation = False
                    sprint.archive_readiness.display_mode = 'disabled'
                    sprint.archive_readiness.reason_code = 'permission_denied'
                    sprint.archive_readiness.safe_summary = '当前用户无权发起迭代归档。'
                    sprint.archive_readiness.blockers = []
            from app.governance.execution_context import reconcile, visible_states, canonical_id, reconcile_external_batch, IdentityIndex
            identities = self._identities
            start = perf_counter()
            reconcile(self.db, self.actor, self.scope, snapshot=snapshot)
            timings['reconcile_ms'] = round((perf_counter() - start) * 1000, 2)
            start = perf_counter()
            external_start = perf_counter()
            reconcile_external_batch(self.db, self.scope,
                [(canonical_id(snapshot, card.id, identities), card.stage) for card in result.issues],
                snapshot, actor=self.actor)
            external_seconds = perf_counter() - external_start
            states = visible_states(self.db, self.actor, self.scope,
                                    [canonical_id(snapshot, card.id, identities) for card in result.issues])
            for card in result.issues:
                object_id = canonical_id(snapshot, card.id, identities)
                if card.type == 'change' and card.stage == 'acceptance':
                    from app.governance.archive_admission import change_acceptance
                    admission = change_acceptance(self.scope.root, object_id, source_root=getattr(self.scope, "source_root", None))
                    if not admission['ready']:
                        card.acceptance_blocked_reason = admission.get('reason') or '验收证据尚未就绪'
                        card.blocked = card.acceptance_blocked_reason
                        if card.action:
                            card.action.disabled_reason = card.acceptance_blocked_reason
                guard, state = states[object_id]
                card.execution_state = state['execution_state']
                card.can_send = state['can_send']
                card.execution_reason = state.get('reason_code')
                card.view_conversation_id = state.get('view_conversation_id')
                if guard and card.view_conversation_id:
                    from app.governance.recovery_schema import operations
                    card.view_turn_id = guard['operation_id']
                    card.verification_operation_id = self.db.scalar(select(operations.c.id).where(operations.c.origin_turn_id == guard['operation_id']))
                from app.governance.completion_handoff import status as completion_status
                completion = completion_status(self.db, self.actor, self.scope, guard)
                card.historical_result = completion['historical_result']
                card.last_checked_at = completion['last_checked_at']
                card.verification_reason = completion['verification_reason']
                card.verification_actions = completion['verification_actions']
                card.verification_differences = completion['verification_differences']
                if guard and not state['can_send']:
                    # Startup is immediate only when the lifecycle projection itself proves it.
                    started = guard['action'] in ('opsx-apply', 'opsx-modify') and card.stage == 'development'
                    # A terminated apply may have a verified CLI successor. Keep
                    # the current lifecycle projection while blocking its action;
                    # the old execution's stage is historical, not a rollback.
                    continuation = guard['action'] in ('opsx-apply', 'opsx-modify') and guard['state'] != 'running'
                    if not started and not continuation and guard['confirmed_stage'] and guard['confirmed_stage'] != 'unknown' and card.historical_result != 'verified':
                        card.stage = guard['confirmed_stage']
                    if card.action and card.stage != 'development':
                        card.action.disabled_reason = '执行中，请查看原执行' if guard['state'] == 'running' else '结果待核对'
            timings['external_reconcile_ms'] = round(external_seconds * 1000, 2)
            timings['card_projection_exclusive_ms'] = round((perf_counter() - start - external_seconds) * 1000, 2)
            start = perf_counter()
            self.db.commit()
            visibility.assert_current(self.db)
            timings['projection_commit_ms'] = round((perf_counter() - start) * 1000, 2)
            start = perf_counter()
            query=urlencode({'space_id':self.scope.space_id,'repository_id':self.scope.repository_id})
            for issue in result.issues:
                if issue.type == 'change' and issue.action and issue.stage != 'development' and self.scope.readonly:
                    issue.action.disabled_reason = '当前空间只读' + ('；' + issue.action.disabled_reason if issue.action.disabled_reason else '')
                documents = list(issue.document_entries)
                for change in issue.related_changes:
                    documents.extend(change.document_entries)
                if issue.current_change:
                    documents.extend(issue.current_change.document_entries)
                for doc in documents:
                    if doc.url: doc.url += ('&' if '?' in doc.url else '?')+query
                    if self.scope.readonly:
                        doc.editable=False
                        doc.capability.human_editable=False
                        doc.capability.task_toggle_only=False
                        doc.capability.ai_mutable=False
                        doc.capability.reason='当前空间只读'
            timings['document_projection_ms'] = round((perf_counter() - start) * 1000, 2)
        return result


def version(content):
    return hashlib.sha256(content.encode()).hexdigest()
