---
title: Agent 浏览器自主取证验收返修台账
created_at: 2026-10-05 23:29:47
updated_at: 2026-10-06 01:02:52
owner: MoonBox 产品团队
---

# Agent 浏览器自主取证验收返修台账

## 反馈与偏差

| 项 | 记录 |
|---|---|
| 反馈 | `.agents/skills/` 下所有技能都应遵守浏览器自主取证、通常优先 Firefox、无需人工二次确认的规则。 |
| 期望 | 任一技能需要产品运行态证据时先在已有权限内自行取证；确实无法取证或仍缺关键证据时才请用户补证。 |
| 实际 | 首轮仅 `bug-explore`、`opsx-modify` 两份技能显式接入；`explore`、`bug-complete`、`opsx-apply` 等仍保留先请用户补证的旧指引。 |
| 证据 | 首轮技能 diff 与本轮 46 份技能清单、聚焦 `rg` 冲突扫描。 |
| 范围 | 原治理 Change 内的技能入口覆盖与一致性返修，不涉及产品运行时代码。 |

## 调整

- 为全部 46 份 `SKILL.md` 加入同一自主取证入口，引用 `rules/root-cause-evidence.md` 第 5 节。
- 修正 `explore`、`bug-complete`、`opsx-apply`、`opsx-modify` 的人工补证顺序。
- 扩展 `scripts/validate-agent-context-budget.py`，对当前及未来技能检查该入口，并加入缺失入口的回归测试。
- 同步 Change 提案、设计、规格增量、治理日志、Sprint 验收摘要和本台账。

## 验证证据

| 验证 | 结果 |
|---|---|
| 46 份技能覆盖扫描 | 46/46 均包含统一自主取证入口。 |
| 旧冲突指引复核 | `explore`、`bug-complete`、`opsx-apply`、`opsx-modify` 已调整为先自主取证。 |
| `python -m unittest tests.unit.test_validate_agent_context_budget` | 8 项通过，含缺失入口反例。 |
| `python scripts/validate-agent-context-budget.py` | 通过，46 份技能覆盖门禁通过。 |
| 当前 Change 中文校验、文档标题与 `openspec validate --strict` | 通过。 |
| 目录结构与 Sprint scope | 通过；既有 legacy 数据目录有非阻断警告。 |
| 聚焦 `git diff --check` | 通过。 |
| Workflow Sync `opsx.modify` | 通过，解析到 `sprint-008`，无错误。 |
| AI Usage Post-command Hook | 非阻断 warning：无可归属 token_count，会话用量不可用，未生成 Sprint snapshot。 |

纯治理文档返修无需实际打开产品；本次验证对象是技能文本与校验门禁。

## 文档一致性

本 Change 无关联 REQ/BUG 子文档；无需更新 API、数据库、UI、部署、安全或客户端生成文档。`rules/root-cause-evidence.md` 第 5 节继续作为完整规则事实源。

## 第二轮反馈：BUG 根因连续补证

| 项 | 记录 |
|---|---|
| 反馈 | `bug-explore`、`bug-generate`、`bug-complete` 生成文档或结论后，如根因尚未 `confirmed`，应尽可能自动补证。 |
| 期望 | 在当前命令内继续聚焦失败测试、脱敏日志、代码与配置、产品浏览器复现等最小关键证据，回填判断，尽早以真实证据确认根因。 |
| 实际 | 原规则只要求根因证据门禁和浏览器优先，`bug-generate` 缺少生成后继续补证流程，`bug-explore` 与 `bug-complete` 也没有统一的连续收敛门禁。 |
| 处置 | 新增 `rules/root-cause-evidence.md` §2.1，分别同步三个技能和 `rules/bug-management.md`；校验脚本与单元测试防止回退。 |
| 边界 | `bug-explore` 默认只读，`bug-generate` 仍只生成 `bug.md`，`bug-complete` 才写 `root-cause.md`；证据不足不得伪造 `confirmed` 或推进评审。 |

| 第二轮验证 | 结果 |
|---|---|
| `python -m unittest tests.unit.test_validate_agent_context_budget` | 9 项通过，新增三个 BUG 技能连续补证防回退测试。 |
| `python scripts/validate-agent-context-budget.py` | 通过，三技能连续补证与 46 份技能自主浏览器取证入口均符合门禁。 |
| 当前 Change 中文校验、OpenSpec strict、中文标题 | 通过。 |
| 目录结构、sprint-008 scope、聚焦 diff whitespace | 通过；既有 legacy 数据目录警告不阻断。 |
| Workflow Sync `opsx.modify` | 通过，解析到 `sprint-008`，无错误。 |
| AI Usage Post-command Hook | 非阻断 warning：无可归属 token_count，`usage_mode: unavailable`。 |

本 Change 仍无关联 REQ/BUG 子文档，产品 API、DB、UI、部署、安全和客户端生成均不受影响。

## 第三轮反馈：探索阶段主动取证

| 项 | 记录 |
|---|---|
| 反馈 | `/explore` 与 `/req-explore` 在需要时也允许并应主动取证。 |
| 期望 | 现状判断依赖产品真实表现且材料不足时，当前探索中直接浏览产品并给出脱敏证据，无需人工二次确认。 |
| 实际 | 既有通用入口只明确测试、验收、BUG 和问题排查；需求探索未列产品浏览为必要动作。 |
| 处置 | 扩展 `rules/root-cause-evidence.md` 第 5 节，并同步两份探索技能、需求管理入口及静态校验。 |
| 边界 | 默认只读，不写仓库或持久业务数据；无法取得证据时明确已尝试路径和不确定性。 |

| 第三轮验证 | 结果 |
|---|---|
| `python -m unittest tests.unit.test_validate_agent_context_budget` | 10 项通过，含两个探索技能主动取证防回退测试。 |
| `python scripts/validate-agent-context-budget.py` | 通过，探索入口与 46 份技能通用取证入口均符合门禁。 |
| 当前 Change 中文校验、OpenSpec strict、中文标题 | 通过。 |
| 目录结构、sprint-008 scope、聚焦 diff whitespace | 通过；既有 legacy 数据目录警告不阻断。 |

无需更新 REQ 子文档、产品 API、DB、UI、部署、安全或客户端生成文档。

第三轮 Workflow Sync `opsx.modify` 解析到 `sprint-008` 且无错误；AI Usage 因缺少可归属 token_count 返回 `usage_mode: unavailable`，属于非阻断 warning。
