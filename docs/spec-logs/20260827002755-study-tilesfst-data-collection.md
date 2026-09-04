---
created_at: 2026-08-27 00:27:55
updated_at: 2026-08-27 00:27:55
---

# TilesFST 数据采集治理学习应用报告

## 学习对象与模式

- 学习对象：`ProjectTilesFST（本地只读项目）`
- 学习模式：`auto`
- 学习焦点：数据采集
- 执行时间：2026-08-27 00:27:55
- 来源命令：`/spec-study apply TilesFST --focus 数据采集 --items A,B,C,D`
- 承载 Change：`apply-tilesfst-data-collection-governance`
- Sprint：`sprint-003`

## 学习到的治理能力

1. 产品数据采集应有统一事实源，覆盖行为事件、请求日志、Task Trace、流程节点、保留周期和脱敏边界。
2. 数据采集门禁应前移到 REQ、Change、Sprint 和归档验收，而不是等实现后补文档。
3. Task Trace 适合按长耗时、多步骤、批量/异步、外部依赖、高风险写操作和失败定位价值分级覆盖。
4. 门禁脚本应检查标准文档、入口规则、技能入口和目标 Change/Sprint 声明，避免只靠人读规范。

## 已采纳内容

| 内容 | 采纳原因 | 落地方式 |
|---|---|---|
| 产品数据采集与链路观测标准 | MoonBox 缺少专项事实源，后续 API/DB/日志/Agent Workflow 变更需要统一口径 | 新增 `docs/standards/product-data-collection-observability.md` |
| Task Trace 覆盖清单 | 需要把“哪些场景应接入流程节点”从经验判断变成可审查清单 | 新增 `docs/standards/task-trace-coverage.md` |
| 门禁脚本 | 让标准、规则和技能接入可执行校验，减少遗漏 | 新增 `scripts/validate-product-data-observability.py` |
| 工作流接入 | REQ、OpenSpec、Sprint 和归档命令需要在不同阶段检查同一声明 | 更新 `AGENTS.md`、`rules/` 和 `.agents/skills/` |

## 未采纳内容

| 内容 | 未采纳原因 |
|---|---|
| 小程序/App 请求封装规则 | MoonBox 当前未启用小程序、移动端或桌面端。 |
| TilesFST 店主端、瓷砖 SKU、媒体转码和门店业务字段 | 属于学习对象业务上下文，不适合迁移到 MoonBox。 |
| 真实数据表、迁移、API 或前端请求封装实现 | 属于业务实现范围，必须另走 REQ/OpenSpec；本次只落地治理标准和门禁。 |
| 学习对象长脚本/长规范原样复制 | 违反 `/spec-study` 转写原则；本次使用 MoonBox 适配版文档和脚本。 |

## 更新文件清单

| 文件 | 修改原因 |
|---|---|
| `docs/standards/product-data-collection-observability.md` | 新增 MoonBox 数据采集与链路观测事实源。 |
| `docs/standards/task-trace-coverage.md` | 新增 MoonBox Task Trace 候选场景和分级策略。 |
| `scripts/validate-product-data-observability.py` | 新增标准文档、入口规则、技能和目标声明校验。 |
| `AGENTS.md` | 增加数据采集读取路由和流程红线。 |
| `rules/{api,database,testing,requirement-management,iterations-lifecycle}.md` | 接入数据采集与链路观测门禁摘要。 |
| `.agents/skills/{req-complete,req-review,req-opsx,opsx-propose,opsx-apply,opsx-archive,sprint-propose,sprint-apply,sprint-archive}/SKILL.md` | 在生成、评审、转 Change、执行、归档和 Sprint 编排阶段接入固定声明检查。 |
| `docs/README.md` | 增加新 standards 索引。 |
| `openspec/changes/apply-tilesfst-data-collection-governance/` | 承载本次治理学习应用的 proposal、design、tasks、delta spec、trace、acceptance 和 test-plan。 |
| `iterations/change/sprint-003/sprint.yaml` | 将本次纯治理 Change 纳入 Sprint scope。 |
| `docs/spec-logs/CHANGELOG.md` | 登记本次 study。 |

## 影响声明

- API：不修改 API；新增 API 变更触发数据采集声明的治理门禁。
- 数据库：不修改 schema / migration；新增数据库变更触发 `usage_events`、`request_logs`、`task_traces`、`task_trace_spans` 和保留周期声明的治理门禁。
- Web：不修改 Web 运行时代码；新增 Web/管理端请求封装和行为事件相关变更门禁。
- 客户端 / 管理端：不修改运行时代码。
- Orval：不需要生成；后续涉及请求头或响应字段时必须声明影响。
- Docker Compose：不修改。
- 测试：新增治理脚本校验；业务测试不适用。

## 校验命令和结果

| 命令 | 结果 |
|---|---|
| `python -m py_compile scripts/validate-product-data-observability.py scripts/validate-agent-context-budget.py scripts/ai_usage.py scripts/generate-sprint-fact-sheet.py` | 通过 |
| `python scripts/validate-product-data-observability.py` | 通过 |
| `python scripts/validate-product-data-observability.py --change apply-tilesfst-data-collection-governance` | 通过 |
| `python scripts/validate-product-data-observability.py --sprint sprint-003` | 通过 |
| `python scripts/validate-agent-context-budget.py` | 通过 |
| `python scripts/validate-openspec-language.py` | 通过 |
| `python scripts/validate-directory-structure.py` | 通过 |
| `openspec validate apply-tilesfst-data-collection-governance` | 通过 |
| `python scripts/validate-sprint-scope.py sprint-003 --item apply-tilesfst-data-collection-governance` | 通过 |
| `python scripts/sync-workflow-status.py --event opsx.apply --change apply-tilesfst-data-collection-governance --sprint auto` | 通过，Updated 2，Errors 0 |
| `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change apply-tilesfst-data-collection-governance --sprint sprint-003 --json` | warning：`usage_mode=unavailable`，未发现可用 token 事件，未阻断主流程 |
| `git diff --name-only -- src` | 通过，输出为空 |

## 学习对象只读保护结果

本次应用仅对 `ProjectTilesFST（本地只读项目）` 执行只读文件清单、片段读取和 Git 状态查看；未在学习对象路径下执行写入、格式化、安装、测试修复、迁移、提交、分支、清理或重置命令。

最终只读复核：学习对象存在自身未提交变更，包含 Issue/Sprint 索引、Workflow Sync、Miniapp、Web 审计页和测试等文件；本次命令只执行 `git status --short` 观察状态，未修改学习对象。

## 后续建议

- 后续若要真实落地 `usage_events`、`request_logs`、`task_traces` 或 `task_trace_spans`，应创建独立 REQ/OpenSpec，覆盖 API、DB、Web/管理端请求封装、OpenAPI/Orval、测试和保留周期。
- 可在后续治理优化中把 `validate-product-data-observability.py --diff` 接入发布或归档前集中校验。
