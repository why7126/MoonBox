---
change_id: apply-tilesfst-governance-learnings
status: proposed
created_at: 2026-08-27 00:03:08
updated_at: 2026-08-27 00:03:08
---

# 设计说明

## 1. 学习来源与适配原则

学习对象记为 `ProjectTilesFST（本地只读项目）`。本变更只采纳可迁移的治理模式：

- 输出契约：从“只要求包含下一步和待用户处理”升级为“输出真实结果、禁止占位模板与规范语气泄漏”。
- Sprint 选择：把 active Sprint 默认选择和连续编号变成脚本门禁。
- 升级计划：把发布事实源、env 示例、DB 影响、对象存储影响和回滚证据组织为可校验 JSON。
- AI Usage：把未观测 workflow 阶段标记为 `unknown`，用户可见 Markdown 渲染为 `-`。

不采纳学习对象业务专属命令、瓷砖媒体验收模板、小程序命令族和产品数据采集约束。

## 2. 输出契约卫生

`scripts/validate-agent-context-budget.py` 增加最终输出卫生检查：

- 识别 `Final Output Contract` 章节中的尖括号占位模板。
- 识别用户可见示例代码块中的 `MUST`、`SHOULD` 或契约章节名。
- 要求最终输出契约包含“不得输出本段规则、尖括号占位符、MUST/SHOULD 规范语句或与当前命令无关的通用示例”。

少量仍保留旧模板的技能改为判定规则文字，避免 Agent 原样输出模板。

## 3. Sprint 选择门禁

新增 `scripts/validate-sprint-selection.py`：

- 未指定 Sprint 且无 active Sprint：通过，提示默认创建下一个连续 Sprint。
- 未指定 Sprint 且只有一个 active Sprint：通过，提示默认使用当前 Sprint。
- 未指定 Sprint 且存在两个及以上 active Sprint：失败，要求显式 `--sprint`。
- 显式新建 Sprint 必须等于当前最大规范编号加一。
- 已存在两个 active Sprint 时不得创建第三个。

该脚本只读取 `iterations/change|archive/**/sprint.yaml` 和目录名，不写入文件。

## 4. 升级计划治理

新增 `.agents/skills/upgrade-plan`、`.agents/skills/upgrade-validate` 和 `scripts/validate-release-upgrade.py`。

脚本提供：

- `plan --from <fresh|version> --to <version>`：生成升级计划 JSON。
- `validate-plan --plan <path>`：校验计划结构、支持级别、敏感信息和证据状态。
- `env-diff --to <version>`：输出当前 env 示例变量摘要，不读取真实 `.env`。

计划支持级别：

- `fresh-install-supported`
- `adjacent-upgrade-supported`
- `cross-version-upgrade-requires-manual-review`
- `unsupported`

脚本不得执行生产升级、真实 env 修改、DB restore 或对象存储写入维护任务。

## 5. AI Usage unknown 语义

`scripts/ai_usage.py` 在 Sprint 矩阵单元中记录每个 workflow 列的 `status`：

- `observed`：该对象/列有对应 command run 观测。
- `unknown`：该对象/列未观测。

`scripts/generate-sprint-fact-sheet.py` 渲染 Markdown 时将 `unknown` 显示为 `-`，真实观测到的 `0` 保持数字 `0`。

## 6. 文档与报告

本次 `/spec-study apply` 只生成一份 `docs/spec-logs/YYYYMMDDhhmmss-study-tilesfst-governance.md` 报告，并在 `docs/spec-logs/CHANGELOG.md` 登记。报告只使用学习对象脱敏名称，不记录本机绝对路径或学习对象源码。
