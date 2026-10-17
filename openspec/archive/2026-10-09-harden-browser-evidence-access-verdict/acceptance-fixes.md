---
title: 浏览器取证门禁技能覆盖返修台账
change_id: harden-browser-evidence-access-verdict
created_at: 2026-10-09 23:06:40
updated_at: 2026-10-09 23:06:40
owner: MoonBox 产品团队
---

# 浏览器取证门禁技能覆盖返修台账

## 验收反馈与偏差

用户指出失败重试门禁不应只进入 `explore` 和 `bug-complete`。期望所有已有浏览器自主取证技能都能在入口直接引用同一门禁。检查发现 47 份技能含自主取证入口，首次交付仅 2 份引用 `rules/root-cause-evidence.md` §5.0；遗漏 45 份。影响所有依赖该入口做运行态取证的治理命令。

## 处置

全部 47 份技能均增加短引用，集中规则仍由 `rules/root-cause-evidence.md` §5.0 维护。`scripts/validate-agent-context-budget.py` 增加逐技能引用检查；单元测试移除一份技能的引用并确认校验失败。

## 验证

47/47 技能引用检查通过；聚焦单元测试 11/11 通过；Agent 上下文预算、当前 Change 中文优先、文档标题、目录结构、OpenSpec strict、Sprint scope 与聚焦 diff whitespace 均通过。Workflow Sync 结果见 `trace.md`。
