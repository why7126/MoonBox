---
bug_id: BUG-0053-deployed-acceptance-input-resolution
title: 部署态验收输入解析不完整导致纯 Change 归档误阻塞验收标准
created_at: '2026-10-20 18:56:49'
updated_at: 2026-10-21 19:17:30
owner: 产品团队
severity: high
acceptance_status: passed
---

# 部署态验收输入解析不完整导致纯 Change 归档误阻塞验收标准

## 验收范围

以下为修复交付门禁，已按本次证据逐项验证；根因确认与缺陷文档校验不能算作修复通过。两条关联 BUG 分别验收，保留原有 Change、Sprint 与归档门禁。

### AC-001 本地与部署指纹一致

- [x] AC-001：同一合法绑定、同一验收计划及相同输入内容下，本地和部署态 readiness 一致；覆盖 src、scripts、tests、AGENTS.md、.gitignore 及合法目录输入。
- 验证方式与证据：聚焦自动测试、逐输入来源与指纹对照；差异数为 0。
- 当前结果：通过；命令回归、真实部署与浏览器证据见关联 Change verification.md。

### AC-002 复现样本恢复

- [x] AC-002：修复部署后重新核对 optimize-governance-feedback-loop；当当前输入仍匹配有效证据时，AC-001/002/004 不再因误缺失失效，卡片 ready 且完成/归档可用。若输入已变则先重新验收。
- 验证方式与证据：真实部署结果、run_id、浏览器刷新截图及按钮 disabled 状态；不能只交本地测试。
- 当前结果：通过；命令回归、真实部署与浏览器证据见关联 Change verification.md。

### AC-003 真实失效仍阻断

- [x] AC-003：分别删除输入和修改输入内容，readiness 均 blocked，受影响 AC 正确，完成/归档禁用。
- 验证方式与证据：隔离样本的负向自动测试；不得修改真实验收证据。
- 当前结果：通过；命令回归、真实部署与浏览器证据见关联 Change verification.md。

### AC-004 可信来源与安全边界

- [x] AC-004：没有绑定、不可访问绑定、越界路径与符号链接逃逸不会读取未授权内容；治理事实不无条件回退到另一工作副本。
- 验证方式与证据：安全负向测试及来源规则说明；越界成功读取次数为 0。
- 当前结果：通过；命令回归、真实部署与浏览器证据见关联 Change verification.md。

### AC-005 部署版本与回归可追溯

- [x] AC-005：记录运行版本、代码版本和绑定模式；保留纯 Change 与既有 REQ/BUG 门禁回归证据，不覆盖并行修复。
- 验证方式与证据：部署版本记录与相关回归结果；原有正确性门禁全部通过。
- 当前结果：通过；命令回归、真实部署与浏览器证据见关联 Change verification.md。

## 量化记录

记录每项 AC 的通过/失败、首次执行与复验耗时、总命令耗时、工具失败次数、修复前后误阻塞或无详情样本数。Token 仅使用可归属的实际采集值；缺失标记 unavailable，不估算。无既有性能基线，不虚设改善百分比；固定样本与环境后对照。修复效果以全部 AC 通过和真实部署观察为准。

## 观测与安全边界

product_data_collection_observability: N/A，本次仅制定验收文档，无新产品采集。affected_layers: 治理验收读取、归档准入、需求中心卡片。validation: 根因证据与中文标题校验、Workflow Sync；修复执行时重新判断 API/UI/部署/安全及客户端生成影响。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-21 19:17:30
accepted_by: workflow-sync
source_change: fix-deployed-acceptance-input-resolution
source_sprint: sprint-011
evidence: [openspec/archive/2026-10-20-fix-deployed-acceptance-input-resolution/evidence/acceptance/20261020192401275374-6b50a718/summary.md]
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

