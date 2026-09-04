---
created_at: 2026-08-27 01:02:45
updated_at: 2026-08-27 01:12:30
---

# TilesFST sprint.md 治理学习应用报告

## 学习对象与模式

- 学习对象：`ProjectTilesFST（本地只读项目）`
- 学习模式：`auto`
- 学习焦点：`sprint.md`
- 执行时间：2026-08-27 01:02:45
- 来源命令：`/spec-study apply TilesFST --focus sprint.md --items A,B,C,D,E`
- 承载 Change：`apply-tilesfst-sprint-md-governance`
- Sprint：`sprint-003`

## 学习到的治理能力

1. `sprint.md` 可以从单一 Scope 面板升级为产品化规划面板，显式展示目标编号列表和每个范围项要点。
2. Sprint 范围一致性不应只校验 `sprint.yaml` 和 Scope 表，还应校验 `## 1. Sprint 目标` 的目标编号列表与要点段落。
3. 已有 Sprint 追加范围时，应先更新 `sprint.yaml` 机器事实源，再由 Workflow Sync 刷新 `sprint.md`、`release-note.md` 和 `acceptance-report.md`。
4. `/sprint-exps` 和 `/sprint-archive` 应优先读取 Sprint Fact Sheet，再按 blocker、warning 或 evidence hint 定向读取原始文档。

## 已采纳内容

| 内容 | 采纳原因 | 落地方式 |
|---|---|---|
| Sprint 目标编号列表 | 让 Sprint 目标区覆盖正式范围，避免只有 Scope 表可见 | 更新 `scripts/workflow_sync/patch.py` |
| 每项要点段落 | 让 REQ/BUG/Change 的状态、估算和下一步在目标区可快速扫描 | 更新 `scripts/workflow_sync/patch.py` |
| Scope 校验增强 | 防止 `sprint.yaml`、目标区、Scope 主表和派生表漂移 | 更新 `scripts/validate-sprint-scope.py` |
| Sprint 技能与规则同步 | 让后续 `/sprint-propose`、`/sprint-apply`、`/sprint-exps`、`/sprint-archive` 承接新结构 | 更新 Sprint 技能和 `rules/iterations-lifecycle.md` |
| Fact Sheet 读优先 | 降低复盘/归档时全量展开四件套、trace 和 tasks 的上下文成本 | 更新 `/sprint-exps` 与 `/sprint-archive` |

## 未采纳内容

| 内容 | 未采纳原因 |
|---|---|
| ProjectTilesFST 小程序、瓷砖、证书、SKU、媒体转码等业务内容 | 属于学习对象业务上下文，不适合迁移到 MoonBox。 |
| 直接复制 sprint-026 的风险、横切 AC 或验收门禁 | MoonBox 应按自身 Sprint scope、知识库和 Change 派生摘要生成。 |
| 将 `sprint.md` 升级为机器事实源 | MoonBox 仍以 `sprint.yaml` 为正式范围机器事实源，`sprint.md` 是产品化规划面板。 |
| 改造全部历史归档 Sprint | 本次只增强 active Sprint 流程；历史归档批量变更风险高，需独立治理。 |

## 更新文件清单

| 文件 | 修改原因 |
|---|---|
| `scripts/workflow_sync/patch.py` | 新增 Sprint 目标编号列表和要点段落渲染。 |
| `scripts/validate-sprint-scope.py` | 校验目标编号列表、要点段落、Scope 主表和派生表一致。 |
| `.agents/skills/{sprint-propose,sprint-apply,sprint-exps,sprint-archive}/SKILL.md` | 同步产品化规划面板、追加范围顺序和 Fact Sheet 读优先规则。 |
| `rules/iterations-lifecycle.md` | 固化 `sprint.md` 目标区与 Scope 一致性门禁。 |
| `openspec/changes/apply-tilesfst-sprint-md-governance/` | 承载本次治理学习应用的 proposal、design、tasks、delta spec、trace、acceptance 和 test-plan。 |
| `iterations/change/sprint-003/sprint.yaml` | 将本次纯治理 Change 纳入 Sprint scope。 |
| `iterations/change/sprint-003/sprint.md` | Workflow Sync 派生刷新目标编号列表、要点段落和 Scope。 |
| `iterations/change/sprint-003/acceptance-report.md` | Workflow Sync 派生刷新 Sprint 状态摘要。 |
| `docs/spec-logs/CHANGELOG.md` | 登记本次 study。 |

## 影响声明

- API：不影响。
- 数据库：不修改 schema / migration。
- Web：不修改业务运行时代码。
- 客户端 / 管理端：不影响业务运行时代码。
- Orval：不需要。
- Docker Compose：不修改。
- 测试：新增/增强治理脚本校验；业务测试不适用。
- Sprint：`sprint-003` 容量从 30/30 增至 31/30，处于 100%~120% 软通过区间，需记录容量风险。

## 校验命令和结果

| 命令 | 结果 |
|---|---|
| `python -m py_compile scripts/workflow_sync/patch.py scripts/validate-sprint-scope.py scripts/generate-sprint-fact-sheet.py scripts/validate-agent-context-budget.py` | 通过 |
| `python scripts/validate-sprint-scope.py sprint-003 --item apply-tilesfst-sprint-md-governance` | 通过 |
| `python scripts/validate-sprint-scope.py sprint-003` | 通过 |
| `python scripts/generate-sprint-fact-sheet.py --sprint sprint-003 --summary` | 通过；Fact Sheet 可生成，并提示当前 Sprint 较大、需按 warning 定向展开 |
| `python scripts/validate-agent-context-budget.py` | 通过 |
| `python scripts/validate-openspec-language.py` | 通过 |
| `python scripts/validate-directory-structure.py` | 通过 |
| `openspec validate apply-tilesfst-sprint-md-governance` | 通过 |
| `python scripts/sync-workflow-status.py --event opsx.apply --change apply-tilesfst-sprint-md-governance --sprint auto` | 通过；最终同步后本 Change 在 Sprint 中为 `applied 12/12` |
| `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change apply-tilesfst-sprint-md-governance --sprint sprint-003 --json` | warning；本地会话无 command-run token 事件，usage mode 为 `unavailable`，不阻塞治理应用 |
| `git diff --name-only -- src` | 通过；输出为空 |

## 学习对象只读保护结果

本次应用仅对 `ProjectTilesFST（本地只读项目）` 执行只读文件清单、片段读取和 Git 状态查看；未在学习对象路径下执行写入、格式化、安装、测试修复、迁移、提交、分支、清理或重置命令。

最终只读复核：学习对象存在既有工作区改动，但本次仅执行 `git status --short` 只读检查，未产生写入。

## 后续建议

- 后续可继续评估由 Workflow Sync 派生 `工作量与容量`、`里程碑`、`风险`、`知识库承接` 和 `横切预防清单` 的结构化段落，但应避免把每个 Sprint 的业务风险硬编码到脚本。
- 若要改造历史归档 Sprint，应另开治理 Change，先 dry-run 生成差异清单。
