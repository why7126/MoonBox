---
change_id: establish-root-cause-evidence-governance
status: applied
iteration: sprint-003
created_at: 2026-08-14 17:00:00
updated_at: 2026-08-14 22:33:06
---

# Trace

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-14 17:00:00 | change.created | 创建纯治理 Change，目标为建立证据化根因分析治理。 |
| 2026-08-14 17:00:00 | sprint.include | 纳入 `iterations/change/sprint-003/`。 |
| 2026-08-14 22:33:06 | spec-opt.apply | 新增根因证据规则、人工补证模板、技能门禁、测试/UI/日志规范和校验脚本。 |

## 证据与验证计划

- OpenSpec delta：`openspec/changes/establish-root-cause-evidence-governance/specs/agent-workflow-tooling/spec.md`、`openspec/changes/establish-root-cause-evidence-governance/specs/testing/spec.md`
- 规则事实源：`rules/root-cause-evidence.md`
- 脚本入口：`scripts/validate-root-cause-evidence.py`
- 预期校验：脚本自检、上下文预算、OpenSpec 语言、目录结构、OpenSpec validate、Sprint scope、Workflow Sync。
