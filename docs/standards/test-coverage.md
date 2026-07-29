---
purpose: 测试覆盖率治理
content: 覆盖率目标、分层门槛、统计范围、排除规则、测量命令、CI 门禁、例外审批与维护规则
update_method: 测试策略、覆盖率阈值、统计工具、CI 门禁、目录结构或排除规则变化时同步更新
created_at: 2026-06-27 08:44:18
updated_at: 2026-06-27 08:44:18
owner: MoonBox
note: 适用于 MoonBox 项目；覆盖率是质量信号，不得替代有意义的断言和验收测试
---

# 测试覆盖率标准


本文档定义项目测试覆盖率治理规则，覆盖覆盖率目标、分层门槛、统计范围、排除规则、测量命令、报告格式、CI 门禁、例外审批、趋势治理和 AI 修改边界。

本文档是 `rules/testing.md` 覆盖率章节的落地细则，应与 `docs/standards/testing-governance.md`、`docs/standards/unit-test-standard.md`、`docs/standards/frontend-test-standard.md` 和 CI 配置保持一致。


| 参数 | 说明 | 示例 |
|---|---|---|
| `MoonBox` | 产品名称 | 见 docs/pending-decisions.md |
| `MoonBox` | 项目代码 | 见 docs/pending-decisions.md |
| `MoonBox` | 测试/质量负责人 | 见 docs/pending-decisions.md |
| `MoonBox` | 是否启用覆盖率统计 | true / false |
| `MoonBox` | 全局覆盖率目标 | 见 docs/pending-decisions.md |
| `MoonBox` | 分层覆盖率目标 | 见 docs/pending-decisions.md |
| `MoonBox` | 后端覆盖率目标 | 见 docs/pending-decisions.md |
| `MoonBox` | 前端覆盖率目标 | 见 docs/pending-decisions.md |
| `MoonBox` | 核心模块覆盖率目标 | 见 docs/pending-decisions.md |
| `MoonBox` | 覆盖率工具 | pytest-cov / coverage.py / vitest coverage / nyc / jacoco / none |
| `MoonBox` | 覆盖率配置路径 | 见 docs/pending-decisions.md |
| `MoonBox` | 覆盖率命令 | 见 docs/pending-decisions.md |
| `MoonBox` | 报告格式 | terminal / html / xml / lcov / json |
| `MoonBox` | 覆盖率排除规则 | 见 docs/pending-decisions.md |
| `MoonBox` | CI 覆盖率门禁 | enforced / warning / disabled |
| `MoonBox` | 覆盖率产物路径 | 见 docs/pending-decisions.md |


满足以下任一条件时，应完整启用本文档：

- 项目包含后端、前端、SDK、算法、脚本、移动端、微信小程序或共享库代码。
- 项目需要在 PR、Sprint、发布或 OpenSpec Change 中评估测试充分性。
- 项目需要覆盖率报告、覆盖率趋势、CI 门禁或质量度量。
- 项目存在核心业务、权限、安全、数据、上传、支付、计费、导入导出等高风险模块。

当 `MoonBox=false` 时，可保留本文档为未来启用规范，并明确当前仅执行测试通过率、手工验收或其他质量门禁。


| 原则 | 说明 |
|---|---|
| 覆盖行为 | 覆盖率必须服务于行为验证，不追求无意义行覆盖 |
| 核心优先 | 业务核心、权限、安全、数据变更和错误处理优先高覆盖 |
| 分层治理 | 后端、前端、集成、E2E、脚本和 SDK 可有不同门槛 |
| 趋势稳定 | 覆盖率下降必须有说明、补测或审批 |
| 排除透明 | 排除规则必须显式登记，不得随意扩大 |
| 命令真实 | 覆盖率命令必须来自实际脚本、配置或 CI |
| 不以数代质 | 高覆盖率不能替代有效断言、边界测试和验收测试 |


全局覆盖率目标：

```text
MoonBox
```

分层覆盖率目标：

```text
MoonBox
```

推荐目标矩阵：

| 范围 | 最低覆盖率 | 说明 | 是否强制 |
|---|---:|---|---|
| 后端整体 | `MoonBox` | Service、Repository、API、工具函数 | 见 docs/pending-decisions.md |
| 前端整体 | `MoonBox` | 组件、页面、状态、API Client | 见 docs/pending-decisions.md |
| 核心模块 | `MoonBox` | 权限、安全、计费、核心业务、数据变更 | 见 docs/pending-decisions.md |
| 共享库/SDK | `MoonBox` | 类型转换、序列化、兼容逻辑 | 条件启用 |
| 脚本/工具 | `MoonBox` | 参数校验、失败路径、幂等性 | 条件启用 |
| 算法/模型服务 | `MoonBox` | 预处理、后处理、推理接口、边界输入 | 条件启用 |

规则：

- 初始化时必须根据项目技术栈和风险等级生成真实门槛。
- 未启用的端或模块不得生成强制覆盖率门槛。
- 新项目可先使用 warning 门禁，但必须说明何时升级为 enforced。
- 关键模块覆盖率目标应高于普通胶水代码。


以下代码即使整体覆盖率达标，也必须重点补测：

- 认证、授权、角色、租户、数据范围和资源归属。
- 金额、计费、订单、审批、删除、导入导出和批量操作。
- 数据迁移、数据修复、Repository/DAO 查询条件和事务。
- API 请求校验、响应结构、错误码和兼容行为。
- 文件上传、对象存储、媒体处理、下载权限和生命周期。
- 前端表单、权限状态、错误展示、登录态、上传、关键业务流程。
- 外部服务失败、超时、重试、熔断和回退逻辑。
- Bug 修复对应的复现路径和回归断言。


覆盖率工具：

```text
MoonBox
```

覆盖率配置：

```text
MoonBox
```

统计范围必须明确：

| 范围 | 是否统计 | 说明 |
|---|---|---|
| 后端业务代码 | 见 docs/pending-decisions.md | Service、Repository、API、Schema、工具 |
| 前端业务代码 | 见 docs/pending-decisions.md | components、features、pages、services、stores |
| 共享代码/SDK | 见 docs/pending-decisions.md | shared、sdk、types、client |
| 脚本工具 | 见 docs/pending-decisions.md | scripts、cli、migration helper |
| 测试代码 | 否 | 默认排除 |
| 生成代码 | 条件排除 | OpenAPI 生成、ORM 生成、SDK 生成 |
| 迁移文件 | 条件排除 | 迁移本身可测试，但通常不计行覆盖率 |
| 类型声明 | 条件排除 | 纯类型、接口、常量可合理排除 |


覆盖率排除规则：

```text
MoonBox
```

允许排除：

- 测试目录、Fixture、Mock 数据和测试工具代码。
- 生成代码，例如 OpenAPI Client、ORM 生成模型、GraphQL 生成类型。
- 纯类型定义、接口声明、常量映射、框架入口胶水代码。
- 第三方适配器的薄包装层，但核心错误处理仍应测试。
- 平台启动文件、开发工具配置和不可稳定自动化的环境分支。

禁止排除：

- 为了提高覆盖率而排除未测试业务逻辑。
- 排除认证、权限、安全、计费、删除、导入导出等高风险模块。
- 排除近期 Bug 修复代码。
- 排除异常分支、错误码映射、外部依赖失败处理。

任何新增排除规则必须在本文档、覆盖率配置和 PR 说明中同步说明。


覆盖率命令：

```bash
MoonBox
```

报告格式：

```text
MoonBox
```

报告产物：

```text
MoonBox
```

要求：

- 覆盖率命令必须来自实际脚本、Makefile、package.json、CI 配置或测试框架配置。
- 命令未知时标记 `见 docs/pending-decisions.md`，不得编造。
- 本地命令和 CI 命令应尽量一致；若不同，必须说明差异。
- HTML、XML、LCOV、JSON 等报告产物不得提交 Git，除非项目明确要求。
- 报告路径应加入 `.gitignore` 或项目等价忽略配置。


CI 覆盖率门禁：

```text
MoonBox
```

门禁模式：

| 模式 | 说明 | 适用阶段 |
|---|---|---|
| disabled | 不校验覆盖率，只运行测试 | 原型或尚未配置覆盖率 |
| warning | 覆盖率下降只警告 | 早期建设或历史包袱整理期 |
| enforced | 覆盖率不达标阻断合并 | 稳定工程或核心模块 |

要求：

- PR 至少应展示测试结果；启用覆盖率后应展示覆盖率摘要。
- 覆盖率下降必须说明原因、补测计划或例外审批。
- 核心模块建议使用更严格门槛。
- 生成代码、大规模迁移、重构和删除代码导致的覆盖率波动必须单独说明。


允许短期例外的情况：

- 遗留代码补测计划已登记。
- 第三方 SDK、平台 API、硬件能力、浏览器能力难以稳定自动化。
- 大规模迁移期间需要分阶段恢复覆盖率。
- 自动化成本明显高于风险，且已有人工验收或其他门禁。

例外必须记录：

| 项 | 说明 |
|---|---|
| 范围 | 哪些目录、模块、文件或能力例外 |
| 原因 | 为什么暂不满足覆盖率门槛 |
| 风险 | 可能漏测的行为 |
| 替代验证 | 人工验收、集成测试、E2E、监控或灰度 |
| 截止时间 | 何时补齐或重新评估 |
| 负责人 | 谁跟进 |


- 覆盖率应关注趋势，不只关注单次数字。
- 新增功能覆盖率低于项目目标时，应在 PR 中说明补测计划。
- Bug 修复应增加复现测试，避免覆盖率不变但回归风险未降低。
- 覆盖率提高不应通过无意义断言、纯 smoke 或测试私有实现达成。
- 覆盖率统计口径变化时，必须在本文档和 CI 说明中记录。


覆盖率只回答“哪些代码被执行过”，不能回答“行为是否被正确验证”。

必须同时遵守：

- `docs/standards/testing-governance.md`：测试分层和质量门禁。
- `docs/standards/unit-test-standard.md`：单元测试质量要求。
- `docs/standards/frontend-test-standard.md`：前端测试质量要求。
- `rules/testing.md`：项目级测试治理。
- `openspec/testing-mapping.md`：需求、变更与测试映射。


AI 修改测试、覆盖率配置、CI 或质量门禁时必须同步检查：

```text
rules/testing.md
docs/standards/testing-governance.md
docs/standards/unit-test-standard.md
docs/standards/frontend-test-standard.md
docs/standards/test-coverage.md
CI 配置
测试框架配置
```

要求：

- 不得为了通过 CI 降低覆盖率阈值。
- 不得扩大排除范围来掩盖未测试代码。
- 不得删除失败测试、跳过断言或保留无意义 smoke 测试。
- 不得保留来源项目目录、命令、覆盖率配置或技术栈假设。
- 新增业务代码、Bug 修复、安全变更、API 变更必须评估覆盖率影响。


初始化生成本文档时应执行：

1. 根据用户输入替换 `MoonBox`、`MoonBox`、`MoonBox`、`MoonBox`、`MoonBox`、`MoonBox`、`MoonBox`、`MoonBox`。
4. 根据实际测试框架、配置文件、脚本和 CI 生成测量命令与报告路径；未知信息标记为 `见 docs/pending-decisions.md`。
5. 不得编造覆盖率工具、覆盖率命令、配置路径、CI 门禁或覆盖率目标。
6. 保持本文档与 `rules/testing.md`、`docs/standards/testing-governance.md`、`docs/standards/unit-test-standard.md`、`docs/standards/frontend-test-standard.md` 一致。


以下变化必须更新本文档：

- 覆盖率目标、统计工具、配置路径或报告格式变化。
- 测试目录、源码目录、前端/后端/移动端/SDK/算法技术栈变化。
- CI 门禁、发布准入、PR 模板或覆盖率趋势规则变化。
- 新增高风险模块、核心业务、权限、安全、上传、外部服务或数据迁移。
- 新增或调整覆盖率排除规则、例外审批或质量门禁。
