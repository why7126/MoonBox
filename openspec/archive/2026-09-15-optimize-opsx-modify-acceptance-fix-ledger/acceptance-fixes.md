---
created_at: 2026-09-15 09:01:13
updated_at: 2026-09-15 09:33:51
---

# 验收返修台账

## 返修批次

| 时间 | 反馈来源 | 范围判断 | 处理状态 |
|---|---|---|---|
| 2026-09-15 09:33:51 | `/opsx-modify`：需求中心卡片仍提示“验收来源待核实：未找到交付验证记录” | 范围内；属于纯治理 Change 交付验证来源入口补齐，不涉及业务 `src/`、API、DB、Web、客户端、部署或权限边界 | 已处理 |
| 2026-09-15 09:01:13 | 用户反馈：`acceptance-fixes.md` 是否可直接与 `tasks.md` 同级 | 范围内；属于刚创建的治理 Change 文档结构语义返修，不涉及业务 `src/`、API、DB、Web、客户端、部署或权限边界 | 已处理 |

## 偏差证据

| 项 | 记录 |
|---|---|
| 期望 | 完整验收返修台账作为 Change 根目录一等文档，与 `tasks.md` 同级，减少 `implementation/` 子目录带来的语义成本。 |
| 实际 | 首版规则将完整台账放在 `implementation/acceptance-fixes.md`，需要额外解释 `implementation/` 是执行过程材料目录。 |
| 偏差 | 路径层级和目录名增加理解成本；台账本质是验收返修事实源，不是实现细节。 |
| 证据状态 | confirmed；依据用户连续探索反馈、需求中心 Change 索引阻断原因与已落地规则文本。 |

## 调整内容

- 将 `.agents/skills/opsx-modify/SKILL.md` 中完整返修台账路径调整为 `acceptance-fixes.md`。
- 将 `.agents/skills/opsx-archive/SKILL.md` 中归档复核路径调整为 `acceptance-fixes.md`。
- 将 `rules/document-governance.md` 的 Change 推荐结构补充 `acceptance-fixes.md`，并保留 `implementation/` 作为其他实施材料目录。
- 同步当前 Change 的 `proposal.md`、`design.md`、`tasks.md`、`trace.md`、delta spec 与治理日志。
- 在 `trace.md` Frontmatter 增加 `acceptance_refs: [acceptance-fixes.md]`，并补充非空 `## 验证记录` 作为需求中心识别入口。

## 文档未更新项与原因

- 未修改 `src/`：本次只调整治理文档结构。
- 未修改 API、DB、OpenAPI、Orval、Docker Compose：不涉及接口、数据结构、客户端生成或部署行为。
- 未新增脚本校验：当前先以规则和技能契约固化；后续如出现回退再评估脚本化检查。

## 验证证据

- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py --change optimize-opsx-modify-acceptance-fix-ledger --residual-report`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate optimize-opsx-modify-acceptance-fix-ledger`：通过。
- `python scripts/validate-sprint-scope.py sprint-007 --item optimize-opsx-modify-acceptance-fix-ledger`：通过。
- `git diff --check -- <本次治理文件>`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change optimize-opsx-modify-acceptance-fix-ledger --sprint auto`：通过，无新派生差异。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change optimize-opsx-modify-acceptance-fix-ledger --sprint sprint-007 --json`：warning，`usage_mode: unavailable`，不阻断父命令。
- 需求中心 Change 索引复核：本 Change 的归档动作阻断原因为 `None`。

## 子文档一致性扫尾

- Change `proposal.md`、`design.md`、`tasks.md`、`trace.md` 与 delta spec 已同步为根目录 `acceptance-fixes.md`。
- `docs/spec-logs/20260915084746-governance-opsx-modify-acceptance-fix-ledger.md` 和 `docs/spec-logs/CHANGELOG.md` 已同步为根目录台账口径。
