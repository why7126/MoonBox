"""Stable public archive diagnostics shared by API and the online CLI."""

ARCHIVE_FAILURES = {
    'replacement_candidate_ambiguous': ('归档操作关联不唯一，请核对原操作身份。', 'review_archive_history'),
    'archive_query_scope_too_large': ('当前对象关联范围较大，请按单个对象核对。', 'review_archive_blockers'),
    'archive_finalization_blocked': ('归档收尾发现当前文档或引用问题，请修复后回读原操作。', 'review_archive_blockers'),
    'archive_tool_unavailable': ('归档工具尚未就绪，请联系项目管理员。', 'contact_project_admin'),
    'archive_tools_not_trusted': ('归档工具或项目目录未达到可信运行要求，请联系项目管理员。', 'contact_project_admin'),
    'archive_tool_runtime_unavailable': ('归档检查工具无法启动，请联系项目管理员排查服务配置。', 'contact_project_admin'),
    'archive_tool_timeout': ('归档检查超时，请回读原操作后再处理。', 'retry_original_operation'),
    'archive_check_failed_validate_change_delivery_evidence': ('归档前的交付证据检查未通过，请查看当前 Change 的验收证据。', 'review_delivery_evidence'),
    'archive_check_failed_validate_change_identity': ('归档前的对象身份检查未通过，请核对 Change 与来源对象。', 'review_change_identity'),
    'archive_check_failed_validate_directory_structure': ('归档前的项目结构检查未通过，请核对项目文件。', 'review_project_structure'),
    'archive_check_failed_validate_openspec_language': ('归档前的规格文档检查未通过，请核对 Change 文档。', 'review_change_documents'),
    'archive_check_failed_validate_env_ignore_policy': ('归档前的环境文件检查未通过，请联系项目管理员。', 'contact_project_admin'),
    'independent_archive_gate_blocked': ('当前验收证据或归档历史未通过检查，请查看对象阻断项。', 'review_archive_blockers'),
    'archive_requirement_conflict': ('规则修改缺少当前有效的完整验收覆盖，或包含不支持的删除操作，请查看差异及验收证据。', 'review_rule_change'),
    'archive_inputs_changed': ('归档期间项目内容发生变化，请重新检查后再试。', 'refresh_archive_check'),
    'archive_history_changed': ('既有归档记录发生变化，请核对历史后再处理。', 'review_archive_history'),
    'archive_policy_changed': ('归档执行规则发生变化，请回读原操作并联系项目管理员。', 'contact_project_admin'),
    'archive_preview_ambiguous': ('归档预演结果不唯一，请核对 Change 目录与历史记录。', 'review_archive_preview'),
    'archive_result_unknown': ('归档结果尚不能确认，请回读原操作，避免重复执行。', 'retry_original_operation'),
    'archive_sync_unverified': ('归档后的状态同步未确认，请回读原操作。', 'retry_original_operation'),
    'original_operation_required': ('此对象已有归档操作，请使用原操作继续。', 'retry_original_operation'),
    'project_archive_busy': ('项目正在处理另一项归档，请稍后回读原操作。', 'retry_original_operation'),
    'controlled_proposal_required': ('此对象已有受控归档操作，请从原操作继续。', 'retry_original_operation'),
    'archive_tool_changed': ('归档检查工具在执行期间发生变化，请联系项目管理员。', 'contact_project_admin'),
    'archive_tool_failed': ('归档工具执行失败，请核对归档预演和项目文件。', 'review_archive_preview'),
}

SAFE_ARCHIVE_REASONS = frozenset(ARCHIVE_FAILURES) | {
    'archive_filesystem_unavailable', 'archive_storage_unavailable'}


def safe_diagnostics(value):
    """Allow only generated labels and repository-relative locations, never prose."""
    import re
    from pathlib import PurePosixPath
    result = {}
    if not isinstance(value, dict):
        return result
    oid = value.get('operation_id')
    if isinstance(oid, str) and re.fullmatch(r'[A-Za-z0-9_-]{1,64}', oid):
        result['operation_id'] = oid
    findings = []
    source = value.get('findings')
    for item in (source if isinstance(source, list) else [])[:30]:
        if not isinstance(item, dict):
            continue
        path = item.get('relative_path', item.get('file', ''))
        kind = item.get('kind', '')
        if (not isinstance(path, str) or len(path) > 500 or '\\' in path
                or not re.fullmatch(r'[\w./-]+', path)
                or PurePosixPath(path).is_absolute() or '..' in PurePosixPath(path).parts
                or path.split('/')[0] not in {'openspec', 'issues', 'iterations', 'docs'}
                or not isinstance(kind, str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,63}', kind)):
            continue
        line = item.get('line', 0)
        findings.append({'reason_code': 'archive_finalization_blocked', 'kind': kind,
                         'relative_path': path, 'line': line if type(line) is int and 0 <= line <= 1000000 else 0,
                         'message': '请核对当前文档与引用；历史过程保留。',
                         'requires_review': item.get('severity') == 'review' or item.get('requires_review') is True})
    if findings:
        result['findings'] = findings
    return result


class ArchiveDiagnosticError(ValueError):
    def __init__(self, reason, details=None):
        super().__init__(reason)
        self.details = safe_diagnostics(details)
