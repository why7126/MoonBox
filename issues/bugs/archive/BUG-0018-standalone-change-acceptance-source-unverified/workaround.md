---
bug_id: BUG-0018-standalone-change-acceptance-source-unverified
title: 独立 Change 卡片误报验收来源待核实
created_at: 2026-09-14 10:23:16
updated_at: 2026-09-14 15:40:08
owner: 产品团队
---

# 临时规避方案

## 当前可用规避

在修复验收来源识别逻辑前，人工判断独立 Change 是否存在交付验证记录时，不以卡片“未找到交付验证记录”提示作为唯一依据。

可人工核对以下证据入口：

1. 目标 Change 的 `trace.md` 是否存在非空 `## 验证摘要`、`## Validation Log`、`## 验证记录`、`## 验收记录`、`## 验证结果` 或 `## 验收结果`。
2. 目标 Change 目录是否存在非空 `acceptance.md` 或 `verification.md`。
3. 目标 Change 是否声明 `acceptance_refs`，且引用为 Change 目录内相对 Markdown 文件，文件存在且非空。

## 不建议的规避

- 不建议为了让卡片提示消失而随意补建空的 `acceptance.md` 或 `verification.md`。
- 不建议把 tasks 全勾或状态为已完成 当作验收来源。
- 不建议跨 Change 复制验收记录或通过绝对路径引用外部证据。

## 风险

该规避依赖人工核对，仍可能造成看板提示与真实交付证据不一致；正式修复应落在验收来源识别逻辑和回归测试上。
