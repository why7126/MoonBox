## 背景与约束

当前扫描器逐行匹配 `pending`、`applied` 等词。Issue 的验收和排障文档常保存历史轮次、样本状态、命令输出与阶段性结论，这些不是当前 Issue 状态。当前状态已有 Frontmatter 和 YAML 状态字段作为事实入口。

## 目标与边界

将 Issue 子文档的状态阻塞限定在 Frontmatter 与 fenced YAML 中的当前状态字段；继续检查已归档 Change 的证据链接。Sprint 四件套原有当前态检查保持原样。历史正文不改写。

## 技术决定

逐文件先识别开头 Frontmatter 与 fenced YAML 的行范围，再将这些范围传给 Issue 状态扫描；仅在范围内匹配 `status`、`acceptance_status`、`review_status`、`workflow_status` 等结构化字段及未关闭值。路径检查独立执行。这样能避免正文中的示例 YAML、历史表格和技术字段触发假阳性，同时保留可检出的当前态残留。

## 风险与验证

自由正文中的无结构化当前结论不会由 Issue 子文档状态扫描发现；该类结论仍由 Sprint 四件套和验收门禁复核。用合成文档验证历史记录放行、Frontmatter/fenced YAML 中间态阻断、失效链接阻断，并用 sprint-008 实际扫描回归。

## 迁移与回退

无需数据迁移。回退治理脚本后原扫描行为恢复；已修复的归档证据链接保持有效。
