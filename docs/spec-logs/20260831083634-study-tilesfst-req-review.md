---
purpose: TilesFST req-review 治理学习应用报告
content: 记录应用 ProjectTilesFST req-review 默认正向评审、同步收尾和 AI Usage Hook 治理学习项
source: /spec-study apply TilesFST --focus req-review --items A,B,C,D
created_at: 2026-08-31 08:36:34
updated_at: 2026-08-31 08:36:34
---

# TilesFST req-review 治理学习应用报告

## 学习对象与模式

- 学习对象：ProjectTilesFST（本地只读项目）
- 学习模式：`apply`
- 聚焦内容：`req-review`
- 执行时间：2026-08-31 08:36:34

## 学习到的治理能力

1. `req-review` 高频正向路径可默认通过，反向结果使用显式 flag 表达，降低重复参数和追问成本。
2. 正向命令提示应统一使用 `/req-review <REQ-full-id>`，`--approve` 仅作为兼容别名，避免下一步输出冗余。
3. `req-review` 完成 Workflow Sync 后应显式运行 AI Usage Post-command Hook，并只输出 compact 摘要字段。
4. approve 后的目录迁移、当前态看板和 Issue 子文档一致性检查应作为同一条收尾链路处理。

## 已采纳内容和采纳原因

| 项 | 采纳内容 | 采纳原因 |
|---|---|---|
| A | `/req-review <REQ-full-id>` 无 flag 默认 approve | 正向评审是高频路径，默认通过能减少重复参数；缺材料或高风险场景仍由评审门禁阻断。 |
| B | 正向提示去掉 `--approve` | 保持下一步命令更短、更一致；`--approve` 继续兼容历史习惯。 |
| C | `req-review` 显式接 AI Usage Hook | 避免只依赖全局规则导致执行遗漏，保持 workflow 成本记录链路一致。 |
| D | 强化目录迁移、当前态看板和子文档同步收尾 | 让 review 结果、物理目录、registry、CHANGELOG 与后续 Sprint 纳入路径一致。 |

## 未采纳内容和未采纳原因

| 内容 | 原因 |
|---|---|
| 移除 MoonBox 引导式反馈契约 | MoonBox 仍要求在用户选择、材料缺失、风险判断或阻塞处理时使用结构化引导；默认 approve 只适用于评审门禁满足的成功路径。 |
| 修改业务实现或 UI 行为 | 本次为纯治理学习应用，不触碰 `src/` 业务运行时代码。 |

## 更新文件清单

| 文件 | 修改原因 |
|---|---|
| `.agents/skills/req-review/SKILL.md` | 将无 flag 默认改为 approve，保留 `--approve` 兼容别名，补齐 AI Usage Hook。 |
| `rules/requirement-management.md` | 同步默认正向评审语义、下一步命令和待评审提示。 |
| `rules/issues-lifecycle.md` | 同步无 flag 默认通过后的目录迁移口径。 |
| `docs/08-command-execution-order.md` | 同步标准链路和 REQ/BUG 到 OpenSpec 的正向命令提示。 |
| `openspec/changes/apply-tilesfst-req-review-governance/` | 承载本次治理学习应用的 OpenSpec Change。 |
| `iterations/change/sprint-003/` | 纳入本次纯治理 Change 并通过 Workflow Sync 刷新派生内容。 |
| `docs/spec-logs/CHANGELOG.md` | 登记本次跨项目学习应用摘要。 |

## API、数据库、Web、客户端、管理端、Orval、Docker Compose、测试影响

| 范围 | 影响 |
|---|---|
| API | 不涉及接口契约或后端路由。 |
| 数据库 | 不涉及 schema、迁移或数据保留策略。 |
| Web | 不涉及前端运行时代码或 UI。 |
| 客户端/管理端 | 不涉及。 |
| Orval | 不涉及 OpenAPI 生成。 |
| Docker Compose | 不涉及部署拓扑或镜像输入。 |
| 测试 | 需要运行治理文档、OpenSpec、目录结构、Sprint scope、Workflow Sync 和 AI Usage Hook 校验。 |

## 校验命令和结果

| 命令 | 结果 |
|---|---|
| `python scripts/add-sprint-scope-item.py --sprint sprint-003 --change apply-tilesfst-req-review-governance ...` | pass，Change 已纳入 `sprint-003`。 |
| `python scripts/sync-workflow-status.py --event opsx.apply --change apply-tilesfst-req-review-governance --sprint auto` | pass，Updated 2，Errors 0。 |
| `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change apply-tilesfst-req-review-governance --sprint sprint-003 --json` | warning，`usage_mode: unavailable`，`command_run_count: 0`，`sprint_snapshot: skipped`，原因是当前 session 未形成可持久化 command run。 |
| `python scripts/validate-agent-context-budget.py` | pass。 |
| `python scripts/validate-openspec-language.py` | pass。 |
| `python scripts/validate-directory-structure.py` | pass。 |
| `python scripts/validate-sprint-scope.py sprint-003 --item apply-tilesfst-req-review-governance` | pass。 |
| `openspec validate apply-tilesfst-req-review-governance` | pass。 |

## 学习对象只读保护结果

已按只读方式读取 ProjectTilesFST 的治理日志、`req-review` 技能、需求规则、Issue 阶段规则、Workflow Sync 技能、命令顺序文档和相关脚本片段。本次不对学习对象执行写入、格式化、安装、生成、测试、提交、分支、清理或重置命令。

复核结果：学习对象存在既有未提交改动；本次只读学习未处理也未引入这些改动。

## 后续建议

- 后续如果 `bug-review` 也要完全对齐默认正向通过语义，可单独执行聚焦学习或治理优化。
- 若实际执行 `/req-review` 时出现误通过风险，应优先补强前置检查和阻断分级，而不是回退整个默认正向路径。
