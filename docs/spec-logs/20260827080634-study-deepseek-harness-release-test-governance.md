---
purpose: deepseek-harness 发布与测试治理学习应用报告
content: 记录发布产物与构建记录治理、测试分区与慢测试调度治理的学习与采纳结果
created_at: 2026-08-27 08:06:34
updated_at: 2026-08-27 08:24:53
owner: MoonBox 产品团队
---

# deepseek-harness 发布与测试治理学习应用报告

## 学习对象与模式

- 学习对象：deepseek-harness（GitHub 只读快照）
- 学习模式：auto
- 快照标识：`b150a55`
- 执行时间：2026-08-27 08:06:34

## 学习到的治理能力

- 发布构建过程拆分为准备、构建、发布写入阶段，并用产物记录承载版本、输入、校验和发布依据。
- 构建记录保存公开环境、commit 或外部证据标识、产物摘要和校验结果，避免发布时重新解释未记录的本地状态。
- 慢测试通过分区、worker 池和串行前置用例降低耗时，同时保留失败分区、命令和可复跑参数。
- 发布、测试和文档证据区分通过、不适用、warning、blocker 与人工确认。

## 已采纳内容

- 发布产物与构建记录治理：采纳到 `rules/release.md`，要求 release、image、产品手册投影或公开站点构建记录可复核，并声明输入漂移后的失效规则。
- 测试分区与慢测试调度：采纳到 `rules/testing.md`，要求分区数量、worker 来源、串行前置用例、失败停止策略和失败摘要可复核。
- 治理脚本门禁矩阵：采纳到 `docs/08-command-execution-order.md`，补充发布构建记录和慢测试调度的验证入口。

## 未采纳内容

- 未采纳 npm 发布 workflow、registry 写入步骤或 deepseek-harness 包族发布细节；MoonBox 发布对象不同。
- 未采纳 Cordis、TypeScript workspace、client package verifier 等技术栈专用规则。
- 未新增测试分区脚本；本次只建立治理规则，后续如需自动化再通过独立 Change 落地。
- 未修改外部 CI 配置；MoonBox 当前发布和测试校验仍以本项目脚本与命令族为准。

## 更新文件清单

| 文件 | 修改原因 |
|---|---|
| `openspec/archive/2026-08-27-apply-deepseek-harness-release-test-governance/` | 创建并归档独立治理 Change，承载本次学习应用和归档证据。 |
| `openspec/specs/harness-runtime/spec.md` | 归档时合并本次学习应用新增的 harness-runtime 治理规格。 |
| `iterations/change/sprint-003/sprint.yaml` | 将纯治理 Change 纳入 sprint-003 scope。 |
| `rules/release.md` | 补充发布产物、构建记录、manifest、输入漂移和发布写入边界。 |
| `rules/testing.md` | 补充测试分区与慢测试调度规则。 |
| `docs/08-command-execution-order.md` | 在治理脚本门禁矩阵中补充发布构建记录和慢测试调度验证入口。 |
| `docs/spec-logs/CHANGELOG.md` | 登记本次 study 索引。 |
| `docs/spec-logs/20260827080634-study-deepseek-harness-release-test-governance.md` | 记录学习、采纳、未采纳、影响、验证和只读保护结果。 |

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
- 通过：`openspec validate apply-deepseek-harness-release-test-governance`
- 通过：`python scripts/validate-sprint-scope.py sprint-003`
- 通过：`python scripts/sync-workflow-status.py --event opsx.apply --change apply-deepseek-harness-release-test-governance --sprint auto`，`Updated: 0`、`Skipped (no delta): 17`、`Errors: 0`。
- 通过：`python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change apply-deepseek-harness-release-test-governance --sprint sprint-003 --json`，`usage_mode: actual`，`warning_count: 0`。
- 通过：`scripts/archive-change.sh apply-deepseek-harness-release-test-governance`，正式规格合并 `+ 3 added`，归档到 `openspec/archive/2026-08-27-apply-deepseek-harness-release-test-governance/`。
- 通过：`python scripts/validate-env-ignore-policy.py`
- 通过：`python scripts/validate-archive-evidence.py --change apply-deepseek-harness-release-test-governance --archive-path openspec/archive/2026-08-27-apply-deepseek-harness-release-test-governance`，归档证据 `PASS`。
- 通过：`python scripts/sync-workflow-status.py --event opsx.archive --change apply-deepseek-harness-release-test-governance --sprint auto`，`Updated: 2`、`Skipped: 15`、`Errors: 0`。
- 通过：`python scripts/promote-issues-for-archive.py --change apply-deepseek-harness-release-test-governance --reason "/opsx-archive apply-deepseek-harness-release-test-governance"`，无符合归档迁移条件的 Issue。
- 通过：`python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.archive --change apply-deepseek-harness-release-test-governance --sprint sprint-003 --json`，`usage_mode: actual`，`warning_count: 0`。

聚焦 diff 复核：本次变更文件限定在 OpenSpec Change、Sprint scope、发布规则、测试规则、命令顺序文档、spec-logs 和 AI Usage 派生记录；当前工作区存在 `src/web/openapi.json` generated diff（5299 行删除），该文件不属于本次学习应用编辑范围，未在本命令中处理。

## 学习对象只读保护结果

学习对象使用 GitHub 临时只读快照读取；未对学习对象执行写入、安装、格式化、迁移、测试修复、提交、push、reset 或 clean 操作。最终 `git status --short` 无输出。

## 后续建议

- 可在后续 `/spec-opt` 中评估是否为慢测试分区和发布产物 manifest 增加自动校验脚本。
