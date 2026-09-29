# 任务

## 1. Change 与 Sprint 纳入

- [x] 1.1 创建纯治理 OpenSpec Change `optimize-opsx-modify-acceptance-fix-ledger`。
- [x] 1.2 将 Change 纳入 `sprint-007` 机器范围并记录 1 人天估算。

## 2. 技能与规则同步

- [x] 2.1 更新 `.agents/skills/opsx-modify/SKILL.md`，将完整返修台账主位置调整为 `acceptance-fixes.md`，并约束 `tasks.md` 与 `trace.md` 的摘要职责。
- [x] 2.2 更新 `.agents/skills/opsx-archive/SKILL.md`，归档复核读取返修台账并验证证据入口。
- [x] 2.3 更新 `rules/document-governance.md`，固化 Change 文档职责分层与返修台账归属。

## 3. 治理日志与验证

- [x] 3.1 写入 `docs/spec-logs/20260915084746-governance-opsx-modify-acceptance-fix-ledger.md` 并更新 `docs/spec-logs/CHANGELOG.md`。
- [x] 3.2 运行上下文预算、OpenSpec 语言、目录结构、OpenSpec validate、Sprint scope 与 Workflow Sync 校验。
- [x] 3.3 运行 AI Usage post-command hook，并在 trace 与最终输出中记录摘要。

## 4. 验收返修

- [x] 4.1 根据用户反馈，将完整台账路径从子目录方案收敛为 Change 根目录 `acceptance-fixes.md`。
  - 台账：`acceptance-fixes.md`
- [x] 4.2 同步当前 Change 文档、技能、规则和治理日志中的路径说明，并重跑聚焦校验。
- [x] 4.3 补齐需求中心可识别的交付验证来源入口：`trace.acceptance_refs` 指向 `acceptance-fixes.md`，并在 `trace.md` 增加非空 `## 验证记录`。
