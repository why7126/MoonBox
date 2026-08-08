---
purpose: OpenSpec Change Proposal
content: 优化下一步可执行命令的 Issue 身份参数规范
created_at: 2026-08-08 19:34:30
updated_at: 2026-08-08 19:34:30
owner: MoonBox 产品团队
---

# 优化下一步可执行命令的 Issue 身份参数规范

## 背景

当前命令顺序治理已要求 REQ/BUG 链路在 `/opsx-*` 阶段保留来源 ID，但部分 Skill 和校验脚本仍使用 `REQ-xxxx`、`<REQ-id>`、`BUG-xxxx`、`<BUG-id>` 这类宽泛占位，容易让最终回复把 `/opsx-apply` 或 `/opsx-archive` 推荐成裸 Change ID。

用户明确期望：只要来源是 REQ，就从 `/req-*` 到 `/opsx-*` 一直使用完整 `REQ-xxxx-slug`；只要来源是 BUG，就从 `/bug-*` 到 `/opsx-*` 一直使用完整 `BUG-xxxx-slug`；只有非 BUG/REQ 的纯治理 Change 才在 `/opsx-*` 中使用 `<change-id>`。

## 变更内容

- 更新命令顺序文档和规则，明确“原始 Issue ID”必须是完整 `REQ-xxxx-slug` / `BUG-xxxx-slug`。
- 更新 REQ、BUG、opsx 关键 Skill 的输入和下一步模板，避免输出宽泛或回退的参数。
- 更新 `validate-agent-context-budget.py`，将完整 Issue ID 作为可校验的输出契约。
- 记录本次 `/spec-opt` 治理迭代日志。

## 非目标

- 不修改业务 `src/` 代码。
- 不修改 API、数据库、Web、管理端、客户端或 Docker Compose 拓扑。
- 不修改正式 `openspec/specs/`；正式规格由归档命令合并。

## 影响范围

- 影响 `.agents/skills/`、`rules/`、`docs/`、`scripts/` 和本 active Change。
- 业务测试不适用；执行治理校验、OpenSpec 校验和目录校验。
