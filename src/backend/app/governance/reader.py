"""Adapters for the existing parser operating on an authorized stable snapshot."""
import hashlib
import json
import logging
from time import perf_counter
from urllib.parse import urlencode
import yaml
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
        result = stable(self.scope.root)
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
                if not linked:
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
            self.timings = dict(timings)
            logging.getLogger("moonbox.requirement_center").info("requirement_center.read_timing %s", json.dumps({
                "request_id": getattr(self, "request_id", ""), "operation": name,
                "success": success, "timings": timings,
            }))

    def _call(self, name, args, kwargs, timings):
        start = perf_counter()
        snapshot=self.snapshot()
        timings["snapshot_and_fences_ms"] = round((perf_counter() - start) * 1000, 2)
        if name.startswith('update_'):
            if self.scope.readonly: raise ChatError(2601,'当前空间只读',403)
            # Every old write entrance fails closed until the trusted writer is installed.
            raise ChatError(2605,'受控写入服务尚未就绪，文档保持只读',503)
        files=dict(snapshot.files)
        start = perf_counter()
        with cached_materialize(Snapshot(files,snapshot.revision), (str(self.scope.root), self.scope.binding_revision)) as root, legacy.using_governance_root(root, immutable=True):
            timings["materialize_ms"] = round((perf_counter() - start) * 1000, 2)
            start = perf_counter()
            if name != 'build_requirement_center_context':
                entries = self.authorize_object(snapshot, args[0], change='change_document' in name, root=root)
                if 'change_document' not in name: args = (entries[0]['id'], *args[1:])
            timings["object_authorization_ms"] = round((perf_counter() - start) * 1000, 2)
            start = perf_counter()
            if name == 'build_requirement_center_context':
                kwargs = {**kwargs, 'visibility': lambda oid: scopes.visible(self.db, self.actor, self.scope, oid)}
            result=getattr(legacy,name)(*args,**kwargs)
            timings["parse_ms"] = round((perf_counter() - start) * 1000, 2)
            start = perf_counter()
        timings["cleanup_ms"] = round((perf_counter() - start) * 1000, 2)
        if name == 'build_requirement_center_context':
            result.selected_workspace_id=self.scope.space_id
            result.repository_id=self.scope.repository_id
            result.snapshot_revision=snapshot.revision
            result.sync_status='ready'
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
        return result


def version(content):
    return hashlib.sha256(content.encode()).hexdigest()
