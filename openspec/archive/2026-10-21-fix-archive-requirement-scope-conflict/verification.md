---
title: 归档条文冲突修复验证记录
created_at: '2026-10-21 18:50:00'
updated_at: '2026-10-21 18:50:00'
---

# 归档条文冲突修复验证记录

## 结果

BUG-0062／sprint-012，任务11/11。源码稳定批次256项回归通过；逐AC完整清单11/11通过。视觉单项补验执行1条命令、复用10项；apply后最终验收执行0条命令、复用11项，失败0、阻塞0。临时副本归档预演通过，未修改正式specs、原归档或journal。opsx.apply与opsx.accept同步成功，最终共享准入ready。

## 实施范围

archive_recovery按模块与Requirement标题组合判冲突，保留哈希链、唯一归档、交付完整性与最终效果，复读拒绝并发变化。acceptance_evidence/archive_admission独立统计有效AC和恢复准入。sprint_archive_admission供产品、Sprint预检与Workflow Sync复用，同步写入前拒绝，force也不豁免深层阻塞。

当前Change新增条文范围定义，不改REQ-0046保护条文，已验证修复自身delta与原对象无交集，避免自身归档再次阻断。无ID特判。

## 验证入口与证据

| 层次 | 结果与证据 |
|---|---|
| 合成回归 | 256项通过，覆盖条文、解析、断链、重复身份、交付/附件篡改、并发及失败零写入；新增force拒绝及自身归档兼容用例 |
| 逐AC | [完整摘要](evidence/acceptance/20261021190708396912-c279401f/summary.md)；11项通过 |
| 真实仓库只读 | [现场核验](evidence/readonly-observation.json)：REQ-0046从0/36恢复36/36且ready；sprint-011预检pass、同步dry-run成功；原归档与journal哈希不变 |
| 部署产品 | [观察记录](evidence/product-observation.json)、[运行指纹](evidence/deployed-probe.json)：统一部署健康，5个代码文件与源码一致，运行中进度36/36，刷新两次后已完成且无恢复阻塞 |
| 视觉 | [1440px截图](evidence/product-1440.jpg)、[computed style](evidence/product-computed-style.json)：已完成卡片完整显示，selector明确，无溢出；没有新增UI动作、modal或样式 |
| 归档预演 | archive-recovery-guard.py --preview通过，仅临时副本；未执行正式归档 |

最初视觉计划缺少局部preflight声明，已补截图尺寸、附件可读性和部署代码指纹检查；失败诊断保留。其余10项复用当前有效证据，不重复完整测试。负例是隔离回归，没有篡改真实归档制造失败。

## 兼容与边界

需求中心沿用manual_acceptance_progress、acceptance_pending_count、acceptance_blocked_reason与Sprint blocker status/message；内部diagnostics不扩展公开schema。无需API/客户端重新生成、DB迁移、对象存储或权限变更。部署已通过授权统一入口完成。原执行终态和首次execution保留，不用修复覆盖旧历史。

sprint-011页面仍保留独立的验收sign-off门禁，这与修复后的恢复准入分别报告；本次未关闭Sprint。Agent依实际证据完成验收签认，依据opsx-acceptance标准，不冒充用户人工操作。

## 治理检查

根因8条证据、中文、标题、观测、目录、上下文预算、Scope及OpenSpec strict通过。目录仅存在既有legacy SQLite路径warning，未迁移或删除数据。admin-list/form/modal/media-upload与新原型不适用；复用S10-A002证据分层实践。部署等待在用户选择后解除，无剩余外部阻塞。
