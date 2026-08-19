---
purpose: deepseek-harness 治理学习应用报告
content: 记录文档层级、事实唯一归属、治理脚本门禁、Issue/Change 文档质量和最小相关验证策略的学习与采纳结果
created_at: 2026-08-19 12:10:48
updated_at: 2026-08-19 12:10:48
owner: MoonBox 产品团队
---

# deepseek-harness 治理学习应用报告

## 学习对象与模式

- 学习对象：deepseek-harness（GitHub 只读快照）
- 学习模式：auto
- 执行时间：2026-08-19 12:10:48

## 学习到的治理能力

- 根入口保留短执行约束，细节由文档、脚本和专门技能承载。
- 长期文档强调事实唯一归属，减少同一规则在多个位置完整复制。
- 文档质量、Issue/PR 约束和状态流转通过脚本门禁降低漂移。
- 验证策略按影响面选择最小相关证据，不默认全量运行，也不接受自述替代外部验证。

## 已采纳内容

- 文档层级与事实唯一归属：采纳到 `rules/document-governance.md`，用于约束 `docs/`、`issues/`、`iterations/`、`openspec/` 和 Skill 之间的事实归属。
- 治理脚本门禁目录化：采纳到 `docs/08-command-execution-order.md`，形成治理脚本门禁矩阵。
- Issue/Change 文档质量校验：采纳到 `rules/requirement-management.md` 与 `rules/bug-management.md`，强调 trace、registry、CHANGELOG、Sprint 和 Change 的互相追溯。
- 最小相关验证策略：采纳到 `rules/testing.md`，要求按触达面选择验证并说明不适用项。

## 未采纳内容

- 未采纳外部 `.claude/`、`.codex/`、`.cursor/` 等入口目录；MoonBox 当前唯一入口是 `.agents/skills/`。
- 未采纳双语文档三件套机制；MoonBox 当前治理规则为中文优先。
- 未采纳 GitHub Project 自动化状态机；MoonBox 已有 REQ/BUG/Sprint/OpenSpec 与 Workflow Sync 事实源。
- 未采纳 TypeScript/Cordis 专项校验；该能力与 MoonBox 当前技术栈和治理目标不匹配。

## 更新文件清单

| 文件 | 修改原因 |
|---|---|
| `openspec/changes/apply-deepseek-harness-governance-learnings/` | 创建独立治理 Change，承载本次学习应用。 |
| `iterations/change/sprint-003/sprint.yaml` | 将纯治理 Change 纳入 sprint-003 scope。 |
| `rules/document-governance.md` | 补充事实唯一归属和 `/spec-study apply` study 报告例外规则。 |
| `rules/testing.md` | 补充最小相关验证策略。 |
| `rules/requirement-management.md` | 补充 REQ 文档质量与追溯一致性门禁。 |
| `rules/bug-management.md` | 补充 BUG 文档质量、根因证据和追溯一致性门禁。 |
| `docs/08-command-execution-order.md` | 增加治理脚本门禁矩阵。 |
| `docs/spec-logs/CHANGELOG.md` | 登记本次 study 索引。 |
| `docs/spec-logs/20260819121048-study-deepseek-harness-governance.md` | 记录学习、采纳、未采纳、影响、验证和只读保护结果。 |

## 影响评估

- API：不适用，未修改接口契约。
- 数据库：不适用，未修改 schema、迁移或持久化语义。
- Web：不适用，未修改前台页面。
- 客户端生成：不适用，未修改 OpenAPI 或 Orval 生成物。
- 管理端：不适用，未修改管理后台。
- Docker Compose：不适用，未修改部署拓扑或环境变量。
- 测试：仅治理校验适用；业务测试不适用。

## 校验命令和结果

- 通过：`python scripts/validate-agent-context-budget.py`
- 通过：`python scripts/validate-openspec-language.py`
- 通过：`python scripts/validate-directory-structure.py`
- 通过：`openspec validate apply-deepseek-harness-governance-learnings`
- 首次参数错误：`python scripts/validate-sprint-scope.py --sprint sprint-003`，脚本实际接收位置参数。
- 通过：`python scripts/sync-workflow-status.py --event opsx.apply --change apply-deepseek-harness-governance-learnings --sprint auto`
- 通过：`python scripts/validate-sprint-scope.py sprint-003`
- 通过：`python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change apply-deepseek-harness-governance-learnings --sprint sprint-003 --json`，`usage_mode: actual`，`warning_count: 0`。

聚焦 diff 复核：本次变更文件限定在 OpenSpec Change、Sprint scope、规则、命令顺序文档、spec-logs 和 AI Usage 派生记录；工作区已有 `src/` 改动，但不是本次学习应用新增编辑范围。

## 学习对象只读保护结果

学习对象使用 GitHub 临时只读快照读取；未对学习对象执行写入、安装、格式化、迁移、测试修复、提交、push、reset 或 clean 操作。最终 `git status --short` 无输出。

## 后续建议

- 可在后续 `/spec-opt` 中评估是否把治理脚本门禁矩阵接入自动校验脚本，减少人工遗漏。
