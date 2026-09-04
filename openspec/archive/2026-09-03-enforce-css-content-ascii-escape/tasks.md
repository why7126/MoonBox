---
purpose: OpenSpec Change 任务清单
content: CSS content 非 ASCII escape 写法治理落地任务
created_at: 2026-09-03 09:34:14
updated_at: 2026-09-03 09:34:14
owner: MoonBox 产品团队
---

# 任务清单

- [x] 创建 OpenSpec Change，明确 CSS `content` 非 ASCII 符号 escape 规则和影响范围。
- [x] 更新 `rules/ui-design.md`，将该规则纳入 UI 组件规则。
- [x] 扩展 `scripts/validate-design-system.py`，自动阻断 CSS `content` 字符串中的原始非 ASCII 符号。
- [x] 增加脚本级单元测试，覆盖失败与通过样例。
- [x] 将纯治理 Change 纳入 `sprint-004` 并运行 Workflow Sync。
- [x] 写入治理迭代日志并更新 `docs/spec-logs/CHANGELOG.md`。
- [x] 运行上下文预算、OpenSpec 语言、目录结构、目标 Change、Sprint scope 和相关验证。
