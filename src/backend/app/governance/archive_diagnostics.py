"""Stable public archive diagnostics shared by API and the online CLI."""

ARCHIVE_FAILURES = {
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
    'archive_requirement_conflict': ('本次修改删除或改写了已归档规则的原约束，请先调整规则及验收证据。', 'review_rule_change'),
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
