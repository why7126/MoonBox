---
purpose: spec-study 本机路径隐私边界治理日志
content: 记录学习报告本机绝对路径脱敏、规则补充和校验脚本兜底
created_at: 2026-08-07 11:55:25
updated_at: 2026-08-07 11:55:25
owner: MoonBox 产品团队
---

# spec-study 本机路径隐私边界治理日志

## 迭代目标

修正 ProjectTilesFST study 报告和相关 active Change trace 中的本机绝对路径持久化问题，并把“本机绝对路径、系统用户名、用户主目录不得落盘”写成可执行规范和校验门禁。

## 根因

既有规范只要求不得记录用户隐私数据、真实客户数据、密钥和可识别个人主体信息，但没有显性列出本机绝对路径、系统用户名和用户主目录。`/spec-study` 在记录本地学习对象时因此保留了完整本地路径。

## 变更摘要

- 将 ProjectTilesFST 学习对象统一改为 `ProjectTilesFST（本地只读项目）`。
- 更新 `/spec-study`，要求本地路径只用于会话内定位，持久化文档必须使用项目名或脱敏占位符。
- 更新 `docs/spec-logs/README.md` 与 `rules/agent-context-budget.md`，补充本机绝对路径、系统用户名和用户主目录禁写规则。
- 扩展 `scripts/validate-agent-context-budget.py`，扫描 `docs/spec-logs/` 与 active Change 文档中的未脱敏本机路径。

## 更新文件

- `.agents/skills/spec-study/SKILL.md`：补充本地学习对象脱敏规则。
- `AGENTS.md`：补充跨项目学习与治理日志的本机路径禁写红线。
- `rules/document-governance.md`：补充 `docs/spec-logs/` 本机路径禁写规则。
- `rules/directory-structure.md`：补充规范工程日志目录的本机路径隐私边界。
- `docs/spec-logs/README.md`：补充 spec logs 本机路径隐私边界。
- `rules/agent-context-budget.md`：补充 `/spec-study` 学习报告本机路径禁写要求。
- `scripts/validate-agent-context-budget.py`：新增治理隐私扫描。
- `docs/spec-logs/20260807000000-study-projecttilesfst-spec-study.md`：脱敏学习对象。
- `docs/spec-logs/20260807110558-study-projecttilesfst-governance.md`：脱敏学习对象。
- `openspec/changes/apply-projecttilesfst-spec-study/trace.md`：脱敏学习对象。
- `openspec/changes/apply-projecttilesfst-governance-refinements/trace.md`：脱敏学习对象。
- `openspec/changes/avoid-duplicate-spec-study-reports/trace.md`：脱敏学习对象。
- `openspec/changes/redact-spec-study-local-paths/`：新增本次治理 Change。
- `iterations/change/sprint-001/sprint.yaml`：纳入本次纯治理 Change。

## 影响范围

- API：无影响。
- 数据库：无影响。
- Web：无业务实现影响。
- 客户端：无影响。
- 管理端：无业务实现影响。
- Orval：不需要。
- Docker Compose：无影响。
- 测试：仅治理校验和 OpenSpec 校验。

## 验证结果

- `rg` 初查发现两份 study 报告和三个 active Change trace 包含完整本机路径。
- `python scripts/validate-agent-context-budget.py` 扩展后可阻断未脱敏本机路径；占位符示例不再误报。

## 后续建议

- 后续 `/spec-study` 对本地路径学习对象统一在报告中写项目名和只读属性。
- 如未来需要扫描更多目录，可在确认归档历史处理策略后扩大治理隐私扫描范围。
