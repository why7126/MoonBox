---
purpose: OpenAPI 契约治理
content: OpenAPI 契约来源、路由元数据、Schema、响应、错误码、安全声明、Tags、客户端生成、校验与兼容规则
update_method: API 契约、接口分组、请求响应、错误码、认证、客户端生成或兼容策略变化时同步更新
created_at: 2026-06-27 08:44:18
updated_at: 2026-06-27 08:44:18
owner: MoonBox
note: 适用于 MoonBox 项目；未启用 OpenAPI 时可保留为未来启用规范并标记不适用
---

# OpenAPI 规范


本文档定义项目 OpenAPI 契约治理规则，覆盖契约来源、路由元数据、请求响应 Schema、错误响应、安全声明、Tags、版本兼容、客户端生成、契约校验、测试和 AI 修改边界。

本文档是 `docs/standards/api-governance.md` 的契约落地细则，应与 `rules/api.md`、`docs/03-api-index.md`、`docs/standards/error-codes.md`、`docs/standards/authentication.md`、前端 API Client 和测试保持一致。


| 参数 | 说明 | 示例 |
|---|---|---|
| `MoonBox` | 产品名称 | 见 docs/pending-decisions.md |
| `MoonBox` | 项目代码 | 见 docs/pending-decisions.md |
| `MoonBox` | API 治理负责人 | 见 docs/pending-decisions.md |
| `MoonBox` | 是否启用 OpenAPI | true / false |
| `MoonBox` | OpenAPI 版本 | 3.0.x / 3.1.x |
| `MoonBox` | 契约来源 | 后端运行时 / 静态 YAML / 代码生成 / API 网关 |
| `MoonBox` | 运行时契约地址 | 见 docs/pending-decisions.md |
| `MoonBox` | 契约导出路径 | 见 docs/pending-decisions.md |
| `MoonBox` | API 基础前缀 | `/api/v1` |
| `Python + FastAPI + Pydantic + uv` | 后端技术栈 | 见 docs/pending-decisions.md |
| `React + TypeScript + TailWind + Shadcn/UI + Axios + Orval + pnpm` | 前端技术栈 | 见 docs/pending-decisions.md |
| `MoonBox` | 统一响应结构 | `{ code, message, data }` |
| `MoonBox` | 鉴权策略 | Token / Session / OAuth2 / API Key / none |
| `MoonBox` | 错误码文档路径 | `docs/standards/error-codes.md` |
| `MoonBox` | API Tags 清单 | 见 docs/pending-decisions.md |
| `Orval` | 客户端生成器 | OpenAPI Generator / Kiota / 自定义生成器 / none |
| `MoonBox` | 客户端生成命令 | 见 docs/pending-decisions.md |
| `MoonBox` | 生成客户端目录 | 见 docs/pending-decisions.md |
| `MoonBox` | OpenAPI 校验命令 | 见 docs/pending-decisions.md |


满足以下任一条件时，应完整启用本文档：

- 项目提供 HTTP API，并需要对前端、SDK、第三方或内部服务暴露契约。
- 项目需要生成 API Client、SDK、类型定义、接口文档或契约测试。
- 项目需要通过 OpenAPI 校验请求、响应、错误码、安全声明和兼容性。
- 项目存在多端协作、第三方集成、私有化交付或 API 版本治理。

当 `MoonBox=false` 且项目无 API 契约、客户端生成或接口文档需求时，可保留本文档为未来启用规范，并删除强制导出、生成和校验要求。


| 原则 | 说明 |
|---|---|
| 契约事实源明确 | 必须声明 OpenAPI 从哪里生成或维护 |
| 契约与实现一致 | 后端路由、请求响应、错误码、安全声明必须与契约一致 |
| 契约可生成 | 前端类型、SDK 或接口文档应能从契约稳定生成 |
| 契约可测试 | 契约必须能被校验、集成测试或契约测试验证 |
| 兼容优先 | 破坏性变更必须进入新版本或提供迁移策略 |
| 不泄密 | 契约不得暴露内部路径、密钥、调试字段或不应公开的接口 |


当前 OpenAPI 契约来源：

```text
MoonBox
```

运行时契约地址：

```text
MoonBox
```

契约导出路径：

```text
MoonBox
```

生成规则：

- 后端运行时生成时，必须说明运行时地址、导出命令、环境要求和权限边界。
- 静态 YAML/JSON 维护时，必须说明文件路径、评审流程、与代码同步方式。
- API 网关或聚合契约生成时，必须说明聚合来源、过滤规则和公开范围。
- 契约输出不得包含内部调试接口、未授权管理接口、真实密钥、真实服务地址或测试数据。


每个对外 API 必须具备以下元数据或等价信息：

| 元数据 | 要求 |
|---|---|
| operationId | 稳定、唯一、可用于客户端生成 |
| summary | 简短描述接口目的 |
| description | 说明业务语义、边界、限制和副作用 |
| tags | 必须来自 `MoonBox` 或 API 分组 |
| parameters | 路径、查询、Header、Cookie 参数必须完整声明 |
| requestBody | 请求体 Schema、必填字段、枚举和示例必须完整声明 |
| responses | 成功、错误、认证、权限、参数错误响应必须声明 |
| security | 鉴权要求必须与 `docs/standards/authentication.md` 一致 |

示例模板：

```yaml
paths:
  "MoonBox/{resource}":
    get:
      operationId: list{Resource}
      summary: 查询{Resource}列表
      description: 按项目真实业务语义生成，不保留来源项目资源。
      tags:
        - "MoonBox"
      parameters: []
      responses:
        "200":
          description: 成功
```

初始化时必须用项目真实资源替换 `{resource}`、`{Resource}` 和 `MoonBox`。


API Tags 清单：

```text
MoonBox
```

要求：

- Tags 必须与 `docs/03-api-index.md` 的 API 分组一致。
- 禁止未登记 tags 的接口混入默认分组。
- Tags 应按业务能力、端能力或集成边界划分，不按文件名或临时实现命名。
- 管理端、内部接口、开放接口、Webhook、SDK 能力应能从 tags 或路径中清晰识别。
- 废弃接口必须在 description 或扩展字段中声明状态、替代接口和删除计划。


统一响应结构：

```text
MoonBox
```

Schema 要求：

- 请求、响应、分页、错误、认证、上传、异步任务必须有明确 Schema。
- 字段类型、是否必填、默认值、枚举、格式、长度、范围必须尽量声明。
- 时间、金额、ID、文件大小、URL、对象 Key 等字段必须明确格式和单位。
- 响应 envelope 中的 `data` 类型必须明确，不得长期使用空对象或任意对象。
- 字段命名必须与 `rules/language.md` 保持一致。
- 已废弃字段必须标记 deprecated，并说明替代字段。


错误码事实源：

```text
MoonBox
```

要求：

- 每个接口必须声明主要成功响应。
- 需要认证的接口必须声明 401 或项目等价错误响应。
- 有权限边界的接口必须声明 403 或项目等价错误响应。
- 参数错误、资源不存在、业务冲突、限流、外部依赖失败必须按接口场景声明。
- OpenAPI 中的错误码、HTTP 状态、响应 envelope 必须与 `docs/standards/error-codes.md` 一致。
- 错误示例不得包含真实 Token、用户隐私、对象 Key、SQL、堆栈或内部路径。


当前认证策略：

```text
MoonBox
```

当 `MoonBox` 不为 `none` 时启用。

要求：

- securitySchemes 必须声明认证方式、Header/Cookie/API Key/OAuth/OIDC 信息。
- 每个接口必须标明是否需要认证。
- 公开端点必须与 `docs/standards/authentication.md` 的公开端点清单一致。
- OAuth/OIDC/SSO 必须声明 scope、flow、回调或授权边界。
- API Key、Webhook 签名、服务间认证必须有独立安全声明或说明。


客户端生成器：

```text
Orval
```

生成命令：

```bash
MoonBox
```

生成目录：

```text
MoonBox
```

要求：

- 启用客户端生成时，前端或 SDK 不得手写与 OpenAPI 重复的接口类型。
- 生成目录必须标注为生成产物，避免人工直接修改。
- 生成命令必须来自实际脚本或包管理器配置；未知时标记为 `见 docs/pending-decisions.md`。
- 契约变化后必须重新生成客户端或明确说明无需生成。
- 生成器、输出目录和请求适配层必须与 `React + TypeScript + TailWind + Shadcn/UI + Axios + Orval + pnpm` 或 SDK 技术栈一致。


OpenAPI 校验命令：

```bash
MoonBox
```

校验要求：

- OpenAPI JSON/YAML 必须语法有效。
- operationId 必须唯一。
- tags 必须在分组清单内。
- 对外接口必须声明 summary、description、request、response、错误响应和 security。
- 契约不得包含来源项目资源、内部调试接口、真实服务地址或密钥。
- 客户端生成命令必须能基于导出的契约稳定执行。


非破坏性变更：

- 新增可选字段。
- 新增接口。
- 新增错误码但不改变既有错误语义。
- 新增枚举值但客户端已有兼容策略。

破坏性变更：

- 删除或重命名字段、接口、枚举值。
- 改变字段类型、必填性、默认值或单位。
- 改变错误码含义、HTTP 状态或权限边界。
- 改变分页、排序、过滤或认证方式。

破坏性变更必须同步 API 版本策略、`docs/03-api-index.md`、客户端生成、兼容性矩阵、测试和发布说明。


测试要求：

- API 集成测试必须覆盖契约中的主要成功和失败响应。
- 契约测试应验证 OpenAPI 输出与实际接口响应一致。
- 客户端生成后必须至少有编译、类型检查或 smoke 测试。
- 认证、权限、错误码、分页、上传、异步任务等接口必须有对应契约断言。
- OpenAPI 变更必须能追踪到需求、Bug、OpenSpec Change 或接口设计记录。


AI 修改 API、OpenAPI、客户端生成或接口文档时必须同步检查：

```text
rules/api.md
rules/security.md
rules/language.md
docs/03-api-index.md
docs/standards/api-governance.md
docs/standards/openapi-rules.md
docs/standards/error-codes.md
docs/standards/authentication.md
frontend API client / SDK
tests/
```

要求：

- 不得新增没有 OpenAPI 元数据的对外接口。
- 不得只改后端接口而不同步契约、客户端生成和测试。
- 不得手写与契约重复且可能漂移的客户端类型。
- 不得新增未登记 tags、未登记错误码或未声明安全要求的接口。
- 不得保留来源项目路径、资源名、后端框架注解、生成器、输出目录或命令。


初始化生成本文档时应执行：

1. 根据用户输入替换 `MoonBox`、`MoonBox`、`MoonBox`、`MoonBox`、`MoonBox`、`MoonBox`、`Orval`、`MoonBox`、`MoonBox`。
4. 用真实技术栈生成契约来源、导出路径、校验命令和客户端生成方式；未知信息标记为 `见 docs/pending-decisions.md`。
5. 不得编造后端框架、运行时 OpenAPI 地址、生成器、生成命令或输出目录。
6. 保持本文档与 `rules/api.md`、`docs/03-api-index.md`、`docs/standards/api-governance.md`、`docs/standards/error-codes.md`、`docs/standards/authentication.md` 一致。


以下变化必须更新本文档：

- API 路径、请求、响应、错误码、认证、权限或分页策略变化。
- OpenAPI 来源、导出路径、生成命令、客户端生成器或输出目录变化。
- API Tags、分组、版本、兼容性策略变化。
- 新增 Webhook、SDK、开放 API、上传、异步任务或外部集成。
- 契约校验、CI 门禁、测试命令或发布准入变化。
