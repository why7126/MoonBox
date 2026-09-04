---
created_at: 2026-09-04 16:05:54
updated_at: 2026-09-04 16:05:54
---

# TilesFST 本地 session JSONL 治理学习应用报告

## 学习对象与模式

- 学习对象：`ProjectTilesFST（本地只读项目）`
- 学习模式：`auto`
- 学习焦点：本地 session JSONL
- 执行时间：2026-09-04 16:05:54
- 来源命令：`/spec-study apply TilesFST --focus 本地session JSONL --items A,B,C,D,E`
- 承载 Change：`apply-tilesfst-local-session-jsonl-governance`
- Sprint：`sprint-004`

## 学习到的治理能力

1. 普通 workflow AI Usage hook 应先自动发现本地 session JSONL，再降级为 unavailable。
2. 历史回填和审计要使用显式 session 与必要的 manual map，不能依赖最近会话自动命中。
3. `data/ai-usage` 只能保存脱敏派生事实，不能保存 raw session、prompt、系统指令、工具输出或本机路径。
4. Sprint 复盘和归档 gate 需要把 missing、stale、failed、缺 token 与覆盖不足明确降级为 `estimated_fallback`。
5. 自动发现、fallback 和安全跳过必须有脚本级测试兜底。

## 已采纳内容

| 内容 | 采纳原因 | 落地方式 |
|---|---|---|
| 本地 session 自动发现口径 | 避免命令已有上下文但因未手动传 session 过早判定成本不可用 | 更新 `workflow-sync`、`sprint-archive`、`sprint-exps`、命令顺序和上下文预算说明 |
| AI Usage fallback 推荐动作 | 让缺 session、路径不存在和缺 token 场景给出可执行修复路径 | 更新 `scripts/ai_usage.py` |
| `data/ai-usage` 目录说明 | 明确 raw session 与脱敏派生事实边界，降低隐私和路径泄漏风险 | 新增 `data/ai-usage/README.md` 并加入 docs 导航 |
| AI Usage 单元测试 | 防止自动发现、fallback 和 unsafe record 语义漂移 | 新增 `tests/unit/test_ai_usage.py` |
| OpenSpec 与学习报告 | 保持治理变更可追溯，避免只改规则不留事实源 | 新建 active Change、delta spec、学习报告和 CHANGELOG 索引 |

## 未采纳内容

| 内容 | 未采纳原因 |
|---|---|
| 学习对象 raw session、历史快照或业务数据 | 属于本地隐私或业务上下文，不应迁移。 |
| 自动发现用于历史回填 | 历史审计需要精确输入和归因，自动发现只适合普通当前命令。 |
| 将 session 环境变量写入 `.env.example` | 这些变量只用于本地治理脚本定位，不属于应用运行时配置。 |
| 学习对象长脚本原样复制 | MoonBox 已有适配脚本，本次只做差异补齐和测试保护。 |

## 更新文件清单

| 文件 | 修改原因 |
|---|---|
| `.agents/skills/workflow-sync/SKILL.md` | 补齐本地 session 自动发现顺序和历史回填边界。 |
| `.agents/skills/sprint-archive/SKILL.md` | 归档前 AI Usage gate 先尝试自动发现，再降级。 |
| `.agents/skills/sprint-exps/SKILL.md` | Sprint 复盘遇到缺失快照时先尝试刷新，再使用估算模式。 |
| `rules/agent-context-budget.md` | 增加 AI Usage JSONL 持久化安全和自动发现边界。 |
| `docs/08-command-execution-order.md` | 在命令顺序文档补充 AI Usage hook 输入发现口径。 |
| `docs/README.md` | 增加 `data/ai-usage/README.md` 导航。 |
| `data/ai-usage/README.md` | 新增目录级事实源、隐私边界和历史回填说明。 |
| `scripts/ai_usage.py` | 更新 fallback 推荐动作。 |
| `tests/unit/test_ai_usage.py` | 新增脚本级回归测试。 |
| `openspec/archive/2026-09-04-apply-tilesfst-local-session-jsonl-governance/` | 承载并归档本次治理学习应用。 |
| `iterations/change/sprint-004/sprint.yaml` | 将本次纯治理 Change 纳入 Sprint scope。 |
| `docs/spec-logs/CHANGELOG.md` | 登记本次 study。 |

## 影响声明

- API：不影响。
- 数据库：不修改 schema、migration 或运行时数据。
- Web：不影响业务运行时代码。
- 客户端 / 管理端：不影响业务运行时代码。
- Orval：不需要。
- Docker Compose：不修改。
- 测试：新增治理脚本单元测试；业务测试不适用。

## 校验命令和结果

| 命令 | 结果 |
|---|---|
| `python -m pytest tests/unit/test_ai_usage.py` | 通过，4 passed |
| `python -m py_compile scripts/ai_usage.py tests/unit/test_ai_usage.py` | 通过 |
| `python scripts/validate-agent-context-budget.py` | 通过 |
| `python scripts/validate-openspec-language.py` | 通过 |
| `python scripts/validate-directory-structure.py` | 通过 |
| `openspec validate apply-tilesfst-local-session-jsonl-governance` | 通过 |
| `python scripts/validate-sprint-scope.py sprint-004 --item apply-tilesfst-local-session-jsonl-governance` | 首次失败，因 `sprint.md` 派生表尚未刷新；Workflow Sync 后复验通过 |
| `python scripts/sync-workflow-status.py --event opsx.apply --change apply-tilesfst-local-session-jsonl-governance --sprint auto` | 通过，Updated 2，Errors 0 |
| `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change apply-tilesfst-local-session-jsonl-governance --sprint sprint-004 --json` | warning：`usage_mode=unavailable`，当前会话无可归因 command-run token 事件，未阻断主流程 |
| `scripts/archive-change.sh apply-tilesfst-local-session-jsonl-governance` | 通过，归档到 `openspec/archive/2026-09-04-apply-tilesfst-local-session-jsonl-governance/` 并同步正式规格 |
| `python scripts/validate-archive-evidence.py --change apply-tilesfst-local-session-jsonl-governance --archive-path openspec/archive/2026-09-04-apply-tilesfst-local-session-jsonl-governance` | 通过 |
| `python scripts/sync-workflow-status.py --event opsx.archive --change apply-tilesfst-local-session-jsonl-governance --sprint auto` | 通过，Updated 2，Errors 0 |
| `python scripts/promote-issues-for-archive.py --change apply-tilesfst-local-session-jsonl-governance --reason "/opsx-archive apply-tilesfst-local-session-jsonl-governance"` | 通过，无可 promote Issue |
| `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.archive --change apply-tilesfst-local-session-jsonl-governance --sprint sprint-004 --json` | warning：`usage_mode=unavailable`，当前会话无可归因 command-run token 事件，未阻断归档 |
| `openspec validate --all` | 通过，21 passed，0 failed |
| `git diff --name-only -- src` | warning：输出为既有业务改动清单；本次 `/spec-study apply` 未编辑 `src/` |

## 学习对象只读保护结果

本次应用仅对 `ProjectTilesFST（本地只读项目）` 执行只读文件清单、片段读取和 Git 状态观察；未在学习对象路径下执行写入、格式化、安装、测试修复、迁移、提交、分支、清理或重置命令。最终只读复核显示学习对象存在自身未提交变更，但本次命令只观察状态，未修改学习对象。

## 后续建议

- 后续可评估为 AI Usage 历史回填增加独立 dry-run candidate report，但仍应保持显式 session 输入。
- 后续可将 `data/ai-usage/README.md` 的安全边界接入更细粒度的持久化字段校验。
