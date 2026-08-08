---
purpose: ProjectTilesFST spec-opt/spec-study 学习报告
content: 记录从 ProjectTilesFST 学习并应用到 MoonBox 的治理能力
created_at: 2026-08-07 00:00:00
updated_at: 2026-08-07 11:55:25
owner: MoonBox 产品团队
---

# ProjectTilesFST Spec Study

## 学习对象

- 对象：`ProjectTilesFST（本地只读项目）`
- 模式：本地只读学习 + 用户确认后应用
- 重点：`.agents/skills/spec-opt`、`.agents/skills/spec-study`、`.agents/skills/sprint-propose`、`openspec/specs/` delta、上下文预算校验、文档目录边界

## 报告状态

本文件是 2026-08-07 初次 ProjectTilesFST spec-study 学习应用的历史报告，已按当前规范重命名为 `YYYYMMDDhhmmss-study-xxx.md`。

当前 `docs/spec-logs/` 已升级为规范工程日志目录，新报告 MUST 使用时间戳级命名：

```text
YYYYMMDDhhmmss-study-xxx.md
YYYYMMDDhhmmss-governance-xxx.md
```

后续 A-E 治理学习应用已经记录在：

- `docs/spec-logs/20260807110558-study-projecttilesfst-governance.md`

## 学习到的治理能力

- `/spec-opt` 增加纯治理 Change 自动创建 Sprint 时的编号约束：必须扫描 `iterations/archive/` 与 `iterations/change/` 中最大的 `sprint-[0-9]{3}` 编号并加一。
- `/spec-study` 采用两阶段跨项目学习流程：先学习并输出候选内容，等待用户确认后才应用到本项目。
- `/sprint-propose` 将 Sprint ID 约束写入命令入口：只能使用 `sprint-xxx` 三位数字递增格式，且不得默认创建并行 Sprint。
- `openspec/specs/agent-workflow-tooling/spec.md` 与 `openspec/specs/sprint-planning-governance/spec.md` 对 spec-study 和 Sprint 自动编号形成可归档的能力约束。
- 学习对象必须全程只读，不得运行写入、格式化、安装、迁移、测试修复、提交、清理或重置命令。
- 学习报告统一写入 `docs/spec-logs/`，新报告使用 `YYYYMMDDhhmmss-study-xxx.md`，不混入 active Change、知识库或迭代文档。
- `spec-study` 作为裸命令需要纳入 `scripts/validate-agent-context-budget.py` 的命令技能强校验。
- 已读规则和 Skill 在同一会话内可以用结构化摘要复用，但遇到高风险阶段、版本变化或校验失败必须补读原文片段。
- `docs/spec-logs/` 后续可同时承载 `/spec-study` 学习报告和 `/spec-opt` 治理迭代日志，并通过 `study` / `governance` 文件名区分。
- Mintlify 产品手册站点应作为公开投影目录，不替代 `docs/`、`releases/`、`deploy/` 或 OpenSpec 事实源。
- usage-docs 与 Mintlify 校验需要覆盖 site manifest、共享截图资产、旧版本人工修正授权和公开安全。
- deploy 脚本允许在本地演示或配置校验时回退 `.env.example`，但不得输出密钥值、数据库连接串或真实 env 原文。

## 已采纳内容

- 新增 `.agents/skills/spec-study/SKILL.md`，并将业务端表述项目化为 MoonBox 当前的 Web、客户端、管理端边界。
- 更新 `.agents/skills/spec-opt/SKILL.md`，补充治理 Sprint 自动编号规则。
- 更新 `.agents/skills/sprint-propose/SKILL.md`，补充 Sprint ID 自动编号、复用进行中 Sprint、禁止日期或主题混合命名等规则。
- 更新 `AGENTS.md`、`README.md`、`docs/README.md`、`rules/agent-context-budget.md`、`rules/directory-structure.md`、`rules/iterations-lifecycle.md`，补齐 `/spec-study` 入口、学习报告目录、只读保护红线、已读摘要复用和 Sprint 自动编号规范。
- 更新 `scripts/validate-agent-context-budget.py`，将 `spec-study` 纳入命令技能校验。
- 更新 `scripts/validate-directory-structure.py`，登记 `docs/spec-logs/README.md` 与 `docs/spec-logs/`。
- 新增 `docs/spec-logs/README.md`，说明学习报告命名和归属边界。
- 新增 OpenSpec Change `apply-projecttilesfst-spec-study`，用 delta specs 承接 `agent-workflow-tooling` 与 `sprint-planning-governance` 的待归档能力变更。
- 将 `apply-projecttilesfst-spec-study` 纳入 `iterations/change/sprint-001/` 范围，作为治理学习应用项跟踪。

## 后续已采纳内容

在本报告之后，用户继续确认应用 ProjectTilesFST A-E 治理候选，已通过 `apply-projecttilesfst-governance-refinements` 落地：

- A：`docs/spec-logs/` 升级为 `study` / `governance` 双用途规范工程日志目录。
- B：`/spec-opt` 完成规范、技能、脚本、目录边界或校验规则迭代后，必须写入治理迭代日志。
- C：Mintlify 站点投影补充 `site-manifest.json`、`latest`、共享截图资产、manual overrides 和公开安全校验。
- D：usage-docs 生成、更新、校验补充截图资产、旧版本修正授权和站点投影门禁。
- E：deploy 文档固化 env 回退、服务自愈、docs-site 预览和安全输出边界。
- F：后续补充 ProjectTilesFST 的 spec-study 单报告去重规则：同一次 `/spec-study` 学习应用流程只维护一份正式 `study` 报告，不再额外生成内容重复的 `governance` 日志。

对应记录：

- OpenSpec Change：`openspec/changes/apply-projecttilesfst-governance-refinements/`
- 学习报告：`docs/spec-logs/20260807110558-study-projecttilesfst-governance.md`
- 去重修正规则：`openspec/changes/avoid-duplicate-spec-study-reports/`

## 本次应用候选

| 候选 | 处理结果 | MoonBox 落点 |
|---|---|---|
| A | 已应用 | `.agents/skills/sprint-propose/SKILL.md`、`rules/iterations-lifecycle.md`、`AGENTS.md` |
| B | 已应用 | `openspec/changes/apply-projecttilesfst-spec-study/specs/agent-workflow-tooling/spec.md`、`openspec/changes/apply-projecttilesfst-spec-study/specs/sprint-planning-governance/spec.md` |
| C | 已应用 | `rules/agent-context-budget.md` 的 `## 2.1 已读摘要复用` |
| D | 已应用 | `docs/spec-logs/README.md` 的边界说明 |

说明：上表中的 A-D 是初次学习阶段的候选；后续 A-E 指 `spec-logs`、`spec-opt`、Mintlify、usage-docs、deploy 五项治理细化，已在后续报告中独立记录。

## 未采纳内容

- 未采纳 ProjectTilesFST 的瓷砖业务脚本、TileSpec 视觉采集、miniapp 相关发布流程；这些属于 TilesFST 业务域或当前 MoonBox 未启用端。
- 未直接恢复 `.cursor/`、`.codex/`、`.kiro/`、`.opencode/`、`.claude/` 等多 Agent 目录；MoonBox 仍以 `.agents/skills/` 为唯一入口。

## 影响范围

- API：无影响。
- 数据库：无影响。
- Web：无业务实现影响。
- 客户端：无生成物影响。
- 管理端：无业务实现影响。
- Orval：无影响。
- Docker Compose：无配置影响。
- 测试：仅治理校验脚本范围。

## 校验结果

- `openspec validate apply-projecttilesfst-spec-study`：通过。
- `bash scripts/validate-openspec.sh`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change apply-projecttilesfst-spec-study --sprint auto`：通过，更新 2 处，错误 0。
- `python scripts/sync-workflow-status.py --check`：通过，更新 0 处，错误 0。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change apply-projecttilesfst-spec-study --sprint sprint-001`：通过，`data/ai-usage/sprints/sprint-001.json` 已刷新，warning 0。
- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-sprint-scope.py sprint-001 --item apply-projecttilesfst-spec-study`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-generated-docs.py --strict`：通过，仍保留 1 个既有未决占位提示。
- `python scripts/validate-env-ignore-policy.py`：通过。
- `python scripts/validate-mintlify-docs.py`：通过。

后续 `apply-projecttilesfst-governance-refinements` 的校验结果见 `docs/spec-logs/20260807110558-study-projecttilesfst-governance.md`。

## 只读保护结果

学习过程中仅对 ProjectTilesFST 执行 `sed`、`find`、`rg`、`git status`、`git diff` 等只读命令。未在 ProjectTilesFST 路径下执行写入、复制目标写入、格式化、安装、迁移、清理、提交或重置命令。

ProjectTilesFST 在学习前后均存在其自身未提交的治理相关改动；本次任务未修改这些源项目文件。

## 后续建议

- 后续再学习其他项目治理能力时，优先使用 `/spec-study <path> --focus <主题>` 输出候选清单。
- 用户确认应用后，再使用 `/spec-study apply <候选项>` 落地到 MoonBox 治理资产，并继续写入 `docs/spec-logs/YYYYMMDDhhmmss-study-xxx.md`。
- 本文件已按时间戳级 `study` 命名保留；新学习报告不再使用 `YYYYMMDD-xxx.md` 命名。
