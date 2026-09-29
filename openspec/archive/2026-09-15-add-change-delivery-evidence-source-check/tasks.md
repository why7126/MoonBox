# 任务

## 1. Change 与 Sprint 纳入

- [x] 1.1 创建纯治理 OpenSpec Change `add-change-delivery-evidence-source-check`。
- [x] 1.2 将 Change 纳入 `sprint-007` 机器范围并记录 1 人天估算。

## 2. 脚本实现

- [x] 2.1 新增 `scripts/validate-change-delivery-evidence.py`。
- [x] 2.2 复用需求中心 `ChangeIndex.acceptance_source_reason()`，默认扫描 active applied Change。
- [x] 2.3 支持 `--change` 聚焦校验和 `--json` 输出。

## 3. 规则与技能同步

- [x] 3.1 更新 `.agents/skills/opsx-archive/SKILL.md`，归档前可运行脚本校验目标 Change。
- [x] 3.2 更新 `rules/document-governance.md`，说明 applied Change 交付验证来源可用脚本扫描。
- [x] 3.3 写入 delta spec，固化交付验证来源脚本门禁。

## 4. 治理日志与验证

- [x] 4.1 写入 `docs/spec-logs/20260915093843-governance-change-delivery-evidence-check.md` 并更新 `docs/spec-logs/CHANGELOG.md`。
- [x] 4.2 运行脚本自身、上下文预算、OpenSpec 语言、目录结构、OpenSpec validate、Sprint scope 与 Workflow Sync 校验。
- [x] 4.3 运行 AI Usage post-command hook，并在 trace 与最终输出中记录摘要。
