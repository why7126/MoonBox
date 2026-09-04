---
change_id: apply-deepseek-harness-release-test-governance
type: update
status: proposed
created_at: 2026-08-27 08:06:34
updated_at: 2026-08-27 08:06:34
---

# 应用 deepseek-harness 发布与测试治理学习成果

## 背景

`/spec-study` 已重新学习 deepseek-harness 最新只读快照。相比上一批已采纳的文档层级、事实唯一归属、Issue/Change 文档质量和最小相关验证，本次新增可迁移价值集中在发布产物与构建记录治理、测试分区与慢测试调度。

MoonBox 已有发布对象、镜像构建计划、镜像 manifest、升级计划和测试规则。本变更只将可迁移治理思想转写到现有规则，不照搬 deepseek-harness 的 npm 发布、Cordis 或 TypeScript workspace 细节。

## 目标

- 补强发布产物与构建记录治理，要求发布、镜像或公开站点构建证据记录来源版本、输入摘要、产物 manifest、校验结果和发布写入边界。
- 补强测试分区与慢测试调度规则，允许慢测试按稳定分区运行，并要求串行高风险用例先跑、并行池显式配置、失败时保留可复核摘要。
- 更新治理脚本门禁矩阵，使发布构建记录和慢测试调度有明确验证入口。
- 生成一份本次学习应用报告，并在 spec-logs 索引中登记。

## 非目标

- 不修改业务 `src/` 代码、API、数据库 schema、Web、管理后台或客户端运行时实现。
- 不引入 npm 发布流程、deepseek-harness release workflow 或外部 CI 配置。
- 不新增测试分区脚本；本次只沉淀治理规则和校验入口。
- 不修改 `openspec/specs/` 正式规格。

## 影响范围

```yaml
impact:
  backend: false
  web: false
  miniapp: false
  admin: false
  database: false
  storage: false
  api: false
  governance: true
```
