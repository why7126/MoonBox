---
purpose: 测试治理体系
content: 测试目标、测试分层、目录职责、测试策略、AI 补测要求、CI 门禁、覆盖率治理、验收与维护规则
update_method: 测试策略、测试框架、目录结构、质量门禁、CI 流程或覆盖率目标变化时同步更新
created_at: 2026-06-27 08:44:18
updated_at: 2026-08-14 17:00:00
owner: MoonBox
note: 适用于 MoonBox 项目；本文档是测试体系总纲，专项规则见 unit/frontend/coverage 标准
---

# 测试治理体系


本文档定义项目测试治理的总原则，覆盖测试目标、测试分层、目录职责、测试类型、AI 补测要求、CI 门禁、覆盖率治理、验收规则和维护边界。

本文档是 `rules/testing.md` 的落地治理文档，应与以下文档保持一致：

- `docs/standards/unit-test-standard.md`
- `docs/standards/frontend-test-standard.md`
- `docs/standards/test-coverage.md`
- `openspec/testing-mapping.md`
- CI 配置与测试脚本


| 参数 | 说明 | 示例 |
|---|---|---|
| `MoonBox` | 产品名称 | 见 docs/pending-decisions.md |
| `MoonBox` | 项目代码 | 见 docs/pending-decisions.md |
| `MoonBox` | 测试/质量负责人 | 见 docs/pending-decisions.md |
| `MoonBox` | 测试总体策略 | 见 docs/pending-decisions.md |
| `Python + FastAPI + Pydantic + uv` | 后端技术栈 | 见 docs/pending-decisions.md |
| `React + TypeScript + TailWind + Shadcn/UI + Axios + Orval + pnpm` | 前端技术栈 | 见 docs/pending-decisions.md |
| `SQLite` | 数据库技术栈 | 见 docs/pending-decisions.md |
| `MinIO 兼容对象存储，面向文档与图片资产` | 对象存储技术栈 | 见 docs/pending-decisions.md |
| `MoonBox` | 测试框架清单 | 见 docs/pending-decisions.md |
| `MoonBox` | 单元测试命令 | 见 docs/pending-decisions.md |
| `MoonBox` | 集成测试命令 | 见 docs/pending-decisions.md |
| `MoonBox` | E2E 测试命令 | 见 docs/pending-decisions.md |
| `MoonBox` | 全量测试命令 | 见 docs/pending-decisions.md |
| `MoonBox` | 覆盖率命令 | 见 docs/pending-decisions.md |
| `MoonBox` | CI 测试门禁 | required / warning / disabled |
| `MoonBox` | 覆盖率门禁 | enforced / warning / disabled |
| `MoonBox` | 测试报告产物路径 | 见 docs/pending-decisions.md |
| `MoonBox` | 测试目录布局 | 见 docs/pending-decisions.md |


测试体系必须验证以下目标：

| 目标 | 说明 |
|---|---|
| 正确性 | 核心业务、接口、数据处理和交互行为符合需求 |
| 稳定性 | 重复运行结果稳定，不依赖隐式顺序、脏数据或外部偶然状态 |
| 兼容性 | 支持矩阵中的浏览器、设备、运行时、数据库、部署方式符合预期 |
| 安全性 | 认证、授权、输入校验、敏感数据和危险操作具备验证 |
| 回归能力 | Bug 修复、OpenSpec Change、需求变更必须留下可重复回归测试 |
| 可维护性 | 测试结构清晰、断言有效、失败信息可定位 |


推荐默认分层：

```text
            E2E / Acceptance
          Integration / Contract
              Unit / Component
```

初始化时应根据 `MoonBox` 生成分层比例和执行频率：

| 层级 | 推荐用途 | 典型比例 | 执行时机 |
|---|---|---:|---|
| Unit / Component | 函数、Service、Repository、组件、工具、错误码、边界条件 | 60%-80% | 本地、PR、CI |
| Integration / Contract | API、数据库、对象存储、消息队列、外部服务契约 | 15%-30% | PR、CI、发布前 |
| E2E / Acceptance | 关键用户路径、跨端流程、发布验收 | 5%-15% | CI、发布前、关键变更 |
| Compatibility | 浏览器、设备、数据库、部署形态、运行时 | 条件启用 | 发布前、兼容性变更 |
| Security / Regression | 安全场景、历史缺陷、关键风险路径 | 条件启用 | PR、发布前 |

规则：

- 不得用大量 E2E 替代必要的单元测试和集成测试。
- 不得用只验证页面可打开的 smoke 测试替代业务断言。
- 高风险模块必须同时具备低层测试和关键路径验收测试。
- 项目未启用的端、服务或能力不得生成强制测试层级。


测试目录布局：

```text
MoonBox
```

推荐目录职责：

| 目录/模式 | 职责 | 条件 |
|---|---|---|
| `tests/unit/` | 后端/共享库单元测试 | 有后端、脚本、SDK 或共享逻辑时启用 |
| `tests/integration/` | API、数据库、对象存储、队列、外部服务集成测试 | 有服务端集成依赖时启用 |
| `tests/e2e/` | 端到端测试、关键用户路径、发布验收 | 有可交互端或完整业务流程时启用 |
| `tests/compatibility/` | 兼容性矩阵验证 | 有兼容性承诺时启用 |
| `tests/security/` | 权限、安全、输入校验、敏感操作验证 | 有认证授权或安全要求时启用 |
| `tests/fixtures/` | 共享测试数据、构造器、Mock 数据 | 有复用测试数据时启用 |
| `tests/reports/` | 本地临时报告输出 | 不提交 Git，需加入忽略规则 |
| `MoonBox` | 后端就近测试或框架约定测试目录 | 条件启用 |
| `MoonBox` | 前端组件/页面测试文件模式 | 条件启用 |

要求：

- 目录职责必须与实际代码结构、测试框架和 CI 配置一致。
- 未启用的测试目录不得作为强制要求保留。
- 测试报告、覆盖率报告、截图、trace、视频等运行产物不得提交 Git，除非项目明确要求。
- Fixture 和 Mock 必须可读、可复用，不得依赖生产数据或敏感信息。


| 测试类型 | 必须覆盖 | 生成依据 |
|---|---|---|
| 单元测试 | 业务规则、边界条件、错误码、工具函数、权限判断 | `docs/standards/unit-test-standard.md` |
| 组件/页面测试 | 表单、状态、交互、API Mock、错误展示、权限状态 | `docs/standards/frontend-test-standard.md` |
| API 测试 | 请求校验、响应结构、错误码、认证授权、分页过滤 | `docs/03-api-index.md`、`docs/standards/api-governance.md` |
| 集成测试 | 数据库、对象存储、外部服务、事务、异步任务 | 架构和部署文档 |
| E2E 测试 | 核心用户路径、跨模块流程、发布验收路径 | 产品文档和需求验收 |
| 兼容性测试 | 浏览器、设备、运行时、数据库、部署形态 | `docs/05-compatibility-matrix.md` |
| 回归测试 | Bug 复现路径、历史高风险路径 | `issues/bugs/` |
| 安全测试 | 登录、权限、越权、输入校验、敏感数据 | `rules/security.md` |


任何 OpenSpec Change、需求实现、Bug 修复或重构，只要改变行为，就必须评估测试影响。

要求：

- 新增能力必须补充对应单元、集成、前端或 E2E 测试。
- 修改 API 必须补充契约、错误码、权限和兼容性验证。
- 修改数据库、对象存储、异步任务或外部集成必须补充失败路径和回滚/重试验证。
- Bug 修复必须添加可复现的回归测试，除非有明确例外审批。
- Bug 修复、验收返修和效果不如预期问题必须遵守 `rules/root-cause-evidence.md`：测试计划和验收记录必须回扣 root-cause evidence，说明复现路径、失败证据、修复后验证和无法自动化时的替代证据。
- 仅修改文档、样式或无行为配置时，也应说明为什么不需要新增测试。


AI 进行开发、修复或重构时必须遵守：

- 不得只改实现不补测试，除非变更被明确标记为不影响行为。
- 不得删除失败测试来让 CI 通过。
- 不得降低断言质量、跳过关键测试或扩大 skip/xfail 范围。
- 不得引入依赖真实生产服务、生产数据或不可控时间顺序的测试。
- 不得保留来源项目测试目录、命令、技术栈、服务名或业务用例。
- 修改测试命令、目录、覆盖率或 CI 门禁时，必须同步更新本文档和对应专项标准。


单元测试：

```bash
MoonBox
```

集成测试：

```bash
MoonBox
```

E2E 测试：

```bash
MoonBox
```

全量测试：

```bash
MoonBox
```

覆盖率测试：

```bash
MoonBox
```

要求：

- 命令必须来自实际脚本、Makefile、package.json、CI 配置或测试框架配置。
- 命令未知时标记 `见 docs/pending-decisions.md`，不得编造。
- 本地命令和 CI 命令应尽量一致；若不同，必须说明差异。
- 需要外部依赖的集成测试必须提供本地启动、Mock 或跳过条件。


CI 测试门禁：

```text
MoonBox
```

覆盖率门禁：

```text
MoonBox
```

推荐门禁：

| 场景 | 必须运行 | 是否阻断 |
|---|---|---|
| PR | Lint、类型检查、单元测试、必要集成测试 | 是 |
| OpenSpec Apply | 受影响测试、契约测试、回归测试 | 是 |
| Bug 修复 | 复现测试、回归测试、相关单元/集成测试 | 是 |
| 验收返修 / 效果不符 | 与偏差证据对应的回归测试、截图、Network、日志或 computed style 检查 | 是 |
| 发布前 | 全量测试、E2E、兼容性、安全抽查 | 是 |
| 文档变更 | 文档校验、链接或结构检查 | 条件启用 |

测试报告产物：

```text
MoonBox
```


覆盖率目标、统计范围、排除规则和 CI 门禁由 `docs/standards/test-coverage.md` 定义。

本文档只规定治理关系：

- 覆盖率是质量信号，不是测试质量本身。
- 覆盖率下降必须说明原因、补测计划或例外审批。
- 核心模块、权限、安全、数据变更、上传、支付、导入导出等高风险路径应设置更高目标。
- 不得通过删除代码、扩大排除范围或无意义断言制造虚假覆盖率。


测试数据必须满足：

- 可重复创建和清理。
- 不依赖生产数据或真实用户信息。
- 不包含密钥、Token、手机号、邮箱、身份证、地址等敏感信息。
- 集成测试应具备隔离数据库、事务回滚、临时桶/容器或 Mock 服务。
- E2E 测试应明确账号、权限、初始状态和清理策略。

环境要求：

- 本地、CI、预发和生产验证的测试边界必须清晰。
- 破坏性测试不得指向生产环境。
- 外部服务调用应优先使用 Mock、沙箱或专用测试账号。
- 测试依赖的端口、环境变量和服务启动方式应与 `rules/environment.md`、`docs/02-deployment.md` 一致。


允许暂不补测的情况：

- 纯文档、注释、格式化或无行为配置变更。
- 原型探索，且不进入生产或主干。
- 第三方平台、硬件能力、浏览器能力或外部服务难以稳定自动化。
- 遗留代码补测成本过高，且已登记补测计划。

例外必须记录：

| 项 | 说明 |
|---|---|
| 范围 | 哪个需求、Bug、模块或文件 |
| 原因 | 为什么无法或暂不补测 |
| 风险 | 可能漏测的行为 |
| 替代验证 | 人工验收、灰度、监控、集成测试或 E2E |
| 截止时间 | 何时补齐或重新评估 |
| 负责人 | 谁跟进 |


- `rules/testing.md`：项目级测试规则。
- `docs/standards/unit-test-standard.md`：单元测试标准。
- `docs/standards/frontend-test-standard.md`：前端测试标准。
- `docs/standards/test-coverage.md`：覆盖率标准。
- `docs/05-compatibility-matrix.md`：兼容性测试依据。
- `docs/03-api-index.md`：API 测试与契约依据。
- `openspec/testing-mapping.md`：需求、变更与测试映射。


初始化生成本文档时应执行：

1. 根据用户输入替换 `MoonBox`、`MoonBox`、`MoonBox`、`MoonBox`、`MoonBox`、`MoonBox`、`MoonBox`、`MoonBox`。
2. 根据 BACKEND_STACK、FRONTEND_STACK、DATABASE_STACK、OBJECT_STORAGE_STACK、PRODUCT_FORMS 生成真实测试类型和目录职责。
3. 根据实际脚本、测试框架和 CI 配置生成 `MoonBox`、`MoonBox`、`MoonBox`、`MoonBox`、`MoonBox`。
6. 未确认的信息标记为 `见 docs/pending-decisions.md`，不得编造测试框架、命令、目录、报告路径或 CI 门禁。
7. 不得保留来源项目测试命令、目录、服务名、技术栈或业务场景。
8. 保持本文档与 `rules/testing.md`、`docs/standards/unit-test-standard.md`、`docs/standards/frontend-test-standard.md`、`docs/standards/test-coverage.md` 一致。


以下变化必须更新本文档：

- 测试框架、测试命令、测试目录或 CI 流程变化。
- 新增或删除后端、前端、移动端、微信小程序、SDK、算法、对象存储、外部集成等项目能力。
- 覆盖率目标、测试门禁、发布准入或兼容性矩阵变化。
- 新增高风险模块、认证授权、数据迁移、上传下载、支付计费、导入导出或安全要求。
- OpenSpec、需求、Bug、Sprint 或发布流程中的测试责任变化。
