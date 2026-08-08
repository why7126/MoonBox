---
purpose: OpenSpec Change Design
content: 下一步可执行命令 Issue 身份参数优化设计
created_at: 2026-08-08 19:34:30
updated_at: 2026-08-08 19:34:30
owner: MoonBox 产品团队
---

# 下一步可执行命令 Issue 身份参数优化设计

## 设计决策

### D1：完整 Issue ID 优先

REQ/BUG 链路的用户可执行命令使用完整 Issue 目录 ID，而不是只使用编号，也不是 Change ID。

```text
REQ: REQ-0100-mintlify-docs-site-ia-content-experience
BUG: BUG-0125-miniapp-sku-detail-media-original-load
```

原因：

- 完整 ID 与目录、trace、registry 和 Sprint scope 更一致。
- 编号加 slug 更适合用户复制执行，避免多个历史别名或同编号引用歧义。
- `/opsx-*` 内部仍可以解析 Change ID，但对用户暴露的下一步应保持链路身份。

### D2：纯治理 Change 才使用 Change ID

非 REQ/BUG 来源的治理 Change 没有 Issue 身份，因此 `/opsx-apply <change-id>`、`/opsx-modify <change-id>`、`/opsx-archive <change-id>` 仍是正确形式。

### D3：校验脚本覆盖常见回退

`validate-agent-context-budget.py` 增加对关键 Skill 的完整 ID 文本约束，并将 `/opsx-apply <REQ-id>`、`/opsx-archive <REQ-id>` 等不完整模板作为风险项。

## 文档同步

- `docs/08-command-execution-order.md` 是长期规则入口。
- `rules/requirement-management.md` 和 `rules/bug-management.md` 分别约束 REQ/BUG 命令族。
- `rules/agent-context-budget.md` 约束所有 Skill 的输出契约。
- `AGENTS.md` 记录项目级红线。

## 验证策略

- 运行上下文预算校验，确认 Skill 输出契约可被脚本识别。
- 运行 OpenSpec 中文优先校验和目录结构校验。
- 运行 `openspec validate optimize-next-step-issue-identity`。
- 运行 Workflow Sync 和 AI Usage hook。
