---
change_id: apply-deepseek-harness-release-test-governance
status: proposed
created_at: 2026-08-27 08:06:34
updated_at: 2026-08-27 08:06:34
---

# 设计说明

## 转写策略

deepseek-harness 的发布与测试治理可迁移部分不是具体 npm workflow，而是三条约束：

- 构建产物需要可复核记录，发布写入必须基于已验证产物，而不是重新解释本地状态。
- 慢测试可以分区和并行，但分区数量、worker、串行前置用例和失败摘要必须显式。
- 发布、测试和文档证据必须区分“验证通过”“不适用”“待人工确认”和“阻塞”。

MoonBox 已有 `release.json`、`image-build-plan.json`、`image-manifest.json`、升级计划和产品手册校验。本变更把上述约束写入 `rules/release.md`、`rules/testing.md` 和 `docs/08-command-execution-order.md`，保持当前事实源不变。

## 风险控制

- 仅修改治理文档、OpenSpec Change、Sprint scope 和 spec-log，避免触碰业务实现。
- 不新增脚本，避免在当前 dirty worktree 中扩大变更面。
- 对测试分区只定义规则，不要求所有现有测试立即迁移。
