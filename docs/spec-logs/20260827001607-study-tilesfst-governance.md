---
created_at: 2026-08-27 00:16:07
updated_at: 2026-08-27 00:16:07
---

# TilesFST 治理学习应用报告

## 学习对象与模式

- 学习对象：`ProjectTilesFST（本地只读项目）`
- 学习模式：`auto`
- 执行时间：2026-08-27 00:16:07
- 来源命令：`/spec-study apply TilesFST --items A,B,C,D`
- 承载 Change：`apply-tilesfst-governance-learnings`
- Sprint：`sprint-003`

## 学习到的治理能力

1. 命令最终输出契约需要同时校验“下一步/待用户决策”去重、占位模板残留和规范语气泄漏。
2. Sprint 提议前需要脚本化校验 active Sprint 数量、默认选择和连续编号。
3. 发布治理可增加升级与回滚计划，将首次部署、相邻升级和跨版本复核显式结构化。
4. Sprint AI Usage 矩阵需要区分未观测阶段与真实 `0`，避免复盘误读。

## 已采纳内容

| 内容 | 采纳原因 | 落地方式 |
|---|---|---|
| 输出契约卫生增强 | 降低 Agent 原样输出规则模板、尖括号占位和规范语气的风险 | 更新 `scripts/validate-agent-context-budget.py`、4 个旧模板技能、`rules/agent-context-budget.md` 与 `AGENTS.md` |
| Sprint 选择门禁 | 将 Sprint 默认选择和连续编号从文字规则变成可执行检查 | 新增 `scripts/validate-sprint-selection.py`，同步 `/sprint-propose` 与 Sprint 生命周期规则 |
| 升级/回滚计划治理 | 发布流程已有镜像和部署门禁，但缺少版本升级路径对象 | 新增 `scripts/validate-release-upgrade.py`、`upgrade-plan`、`upgrade-validate`，同步 release/environment/database 规则 |
| AI Usage unknown 语义 | 避免未采集 workflow 阶段在复盘矩阵中被误读成真实 0 | 更新 `scripts/ai_usage.py`、`scripts/generate-sprint-fact-sheet.py` 与 `/sprint-exps` |

## 未采纳内容

| 内容 | 未采纳原因 |
|---|---|
| 小程序命令族 | MoonBox 当前未启用小程序。 |
| 瓷砖媒体、证书、门店业务模板 | 属于学习对象业务上下文，不适合迁移到 MoonBox。 |
| 产品数据采集与端请求封装专项门禁 | MoonBox 当前已有自身 API/日志/Workflow Sync 治理，需另行评估，不在本次 A-D 范围内扩展。 |
| 学习对象长脚本原样复制 | 违反 `/spec-study` 转写原则；本次使用 MoonBox 适配版脚本。 |

## 更新文件清单

| 文件 | 修改原因 |
|---|---|
| `AGENTS.md` | 增加部署升级命令入口、Sprint 选择门禁和输出契约卫生摘要。 |
| `.agents/skills/{upgrade-plan,upgrade-validate}/SKILL.md` | 新增升级计划生成与校验命令入口。 |
| `.agents/skills/{explore,git-check,spec-opt,spec-study}/SKILL.md` | 移除最终输出尖括号模板，补充输出卫生约束。 |
| `.agents/skills/{release-propose,release-prepare,sprint-exps,sprint-propose}/SKILL.md` | 同步 upgrade 链路、AI Usage unknown 语义和 Sprint 选择脚本门禁。 |
| `rules/{agent-context-budget,iterations-lifecycle,release,environment,database}.md` | 同步输出契约、Sprint 选择、升级计划、env 示例和数据库升级证据规则。 |
| `scripts/validate-agent-context-budget.py` | 增加最终输出卫生校验和 upgrade 技能识别。 |
| `scripts/validate-sprint-selection.py` | 新增 Sprint 选择与连续编号校验脚本。 |
| `scripts/validate-release-upgrade.py` | 新增升级计划生成与校验脚本。 |
| `scripts/{ai_usage,generate-sprint-fact-sheet}.py` | 增加矩阵 cell_status，并将 unknown 渲染为 `-`。 |
| `openspec/changes/apply-tilesfst-governance-learnings/` | 承载本次治理学习应用的 proposal、design、tasks、delta spec、trace、acceptance 和 test-plan。 |
| `iterations/change/sprint-003/sprint.yaml` | 将本次纯治理 Change 纳入 Sprint scope。 |
| `docs/spec-logs/CHANGELOG.md` | 登记本次 study。 |

## 影响声明

- API：不影响。
- 数据库：不修改 schema / migration；仅新增发布升级计划中数据库影响证据要求。
- Web：不影响业务运行时代码。
- 客户端 / 管理端：不影响业务运行时代码。
- Orval：不需要。
- Docker Compose：不修改 Compose 文件；升级计划脚本不执行 Docker 或生产升级。
- 测试：新增治理脚本校验与 Python 编译检查；业务测试不适用。

## 校验命令和结果

| 命令 | 结果 |
|---|---|
| `python -m py_compile scripts/validate-sprint-selection.py scripts/validate-release-upgrade.py scripts/validate-agent-context-budget.py scripts/ai_usage.py scripts/generate-sprint-fact-sheet.py` | 通过 |
| `python scripts/validate-sprint-selection.py` | 通过，当前 active Sprint 为 `sprint-003`，下一个编号为 `sprint-004` |
| `python scripts/validate-release-upgrade.py --help` | 通过 |
| `python scripts/validate-release-upgrade.py env-diff` | 通过，仅读取可提交 env 示例文件，识别 82 个变量名 |
| `python scripts/validate-agent-context-budget.py` | 通过 |
| `python scripts/validate-openspec-language.py` | 通过 |
| `python scripts/validate-directory-structure.py` | 通过 |
| `openspec validate apply-tilesfst-governance-learnings` | 通过 |
| `python scripts/validate-sprint-scope.py sprint-003 --item apply-tilesfst-governance-learnings` | 通过 |
| `python scripts/sync-workflow-status.py --event opsx.apply --change apply-tilesfst-governance-learnings --sprint auto` | 通过，Updated 2，Errors 0 |
| `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change apply-tilesfst-governance-learnings --sprint sprint-003 --json` | warning：`usage_mode=unavailable`，未发现可用 token 事件，未阻断主流程 |
| `git diff --name-only -- src` | 通过，输出为空 |

## 学习对象只读保护结果

本次应用仅对 `ProjectTilesFST（本地只读项目）` 执行只读文件清单、片段读取和 Git 状态查看；未在学习对象路径下执行写入、格式化、安装、测试修复、迁移、提交、分支、清理或重置命令。

最终只读复核：学习对象存在自身未提交的 Issue、Sprint 和索引变更，但本次命令只执行 `git status --short` 观察状态，未修改学习对象。

## 后续建议

- 后续可为 `validate-release-upgrade.py` 增加 release tag 历史快照读取能力，但仍必须保持真实 env 和生产操作只读/人工授权边界。
- 后续可将 AI Usage 目录级回溯扫描产品化为正式 dry-run 参数，减少临时回溯脚本需求。
