---
title: 同条文兼容追加与显式替代边界
created_at: '2026-10-22'
source_bug: BUG-0063-compatible-requirement-successor-blocked
---

# 同条文兼容追加与显式替代边界

BUG-0061 对 BUG-0060 的三项要求保留正文和原场景，仅增加场景；旧恢复门禁只按相同标题冲突拒绝。证明现场与合成负例分别留存在 `openspec/changes/fix-compatible-requirement-successor/evidence/`。

支持的兼容追加要求原正文、原场景身份和内容保持，新增场景通过独立审查与回归证明；证明绑定旧新正文、增量、验收和附件哈希。完整归档链逐边验证，最终规格与最新保护视图一致；候选不能成为已归档事实。写入前预检及最终复读继续拒绝破坏、断链、篡改和并发变化。

独立证明追加保存，不重写历史 manifest、journal 或首次执行事实。结构相容不等于语义相容，模型意见或文本包含不能单独放行。未支持语法与不确定情况继续阻断。

Chat 诊断逐项给出对象、条文及步骤，签署作为独立门禁。真实错误页面与合成测试分开记账，正向模型轮次未完成时不得宣称完整验收。

本修复自身替代 BUG-0062 的原正文，不属于兼容追加。用户选择保留此归档阻断，显式替代另行处理。不得通过改标题、白名单或改写历史证明自我放行；未自动新建后续 Issue。

持续检查入口：`tests/unit/test_compatible_successor.py`、`test_archive_requirement_scope.py`、`test_archive_baseline_transition.py`、后端诊断测试与 `src/web/src/archive-blockers.test.tsx`。它们随现有 pytest / Vitest 入口执行；SQLite 为隔离运行载体，本修复没有 SQL、数据库 schema 或对象存储变更。

## 当前策略修订（2026-10-23）

用户后续明确取消后继写入前兼容证明硬限制，以上“保留显式替代阻断”仅描述历史决定。当前普通归档不要求独立兼容证明或自动规则替代候选，已完成后继仍核验普通验收、唯一身份、连续归档哈希链、增量与最终效果，历史证据不得改写。

隔离数据库中的外部结果 unknown 不应覆盖已知的验收中阶段；reader 保留规范阶段和结果未核验阻断，避免制造状态歧义。产品归档 completed 与成果已核验分别取证，不能把回归测试冒充产品轮次。当前证据见目标 Change 的 evidence/proof-optional/。
