---
purpose: 全局规则
content: 团队研发规范和AI约束
source: AI自动生成初稿，项目团队确认
update_method: 项目初始化后由人工确认；后续由AI辅助更新并经人工Review
updated_at: 2026-08-27 08:06:34
note: 适用于MoonBox项目模板
---

# 测试规范

后端使用 pytest；前端使用 Vitest/Testing Library；接口变更必须补充集成测试。

## 最小相关验证

每次实现、返修、治理变更或归档前，AI MUST 按影响面选择能证明风险被覆盖的最小相关验证组合，而不是默认全量运行或只报告未验证。选择验证时 SHOULD 先列出变更触达面：API、数据库、Web、管理端、客户端生成、对象存储、Docker/环境、治理规则、Skill、OpenSpec、Sprint、REQ/BUG 文档和脚本。

验证选择规则：

- API 或响应字段变化：运行后端接口测试、OpenAPI/客户端生成相关校验，并同步 `docs/03-api-index.md`。
- 数据库 schema、迁移或持久化语义变化：运行对应数据库/集成测试，并同步 `docs/04-database-design.md`。
- Web 或管理端 UI 变化：运行聚焦前端测试；带 prototype 的 UI Change 还必须提供 1440px 视觉证据和 computed style 或等价证据。
- 治理规则、Skill、OpenSpec、Sprint 或 Workflow Sync 变化：运行上下文预算、OpenSpec 语言、目录结构、目标 Change validate、Sprint scope 和 Workflow Sync；如修改脚本，运行脚本自身或对应单元测试。
- 文档-only 变化：运行文档相关校验；业务测试可标记为不适用，但必须说明不适用原因和残余风险。

不得用“命令输出看起来正常”替代外部验证。若无法自动化验证，MUST 在 trace、验收记录、学习报告或最终回复中说明缺口，并提供可人工复核的日志、截图、Network、computed style、数据库样本或配置差异等证据。

## 测试分区与慢测试调度

慢测试、覆盖率、浏览器验收、Docker smoke 或发布构建验证 MAY 使用分区、worker 池或串并行混合调度降低耗时，但调度方式必须稳定、可复核且可复现。新增或修改这类调度时 MUST 说明：

- 分区数量、worker 数量或来源环境变量。
- 哪些用例必须串行先跑，原因是共享浏览器、端口、数据库、对象存储、全局状态、截图基线或发布产物。
- 并行池覆盖哪些剩余用例，以及失败时是否继续其他分区。
- 输出摘要如何保留失败分区、命令、用例、关键错误和可复跑参数。

高风险互斥用例 SHOULD 在并行池之前串行执行；若串行前置失败，后续并行池 SHOULD 停止，避免产生噪音证据。分区测试不得降低断言、覆盖率阈值、安全扫描或验收门禁；不得通过缩小分区范围隐藏受影响文件。若本地资源不足导致慢测试无法运行，最终回复 MUST 说明未运行的分区、原因、替代证据和建议在 CI 或专用环境补跑的命令。

BUG 修复、验收返修和效果不如预期问题 MUST 遵守 `rules/root-cause-evidence.md`：测试需要回扣复现路径或根因证据。无法自动化复现时，MUST 在验收记录中说明原因，并提供日志、截图、Network、computed style、数据库样本或配置差异等替代证据。

## 产品数据采集与链路观测测试门禁

涉及 API、DB、日志审计、行为埋点、Task Trace、Web/管理端请求封装、对象存储或 Agent Workflow 链路观测的变更，MUST 读取 `docs/standards/product-data-collection-observability.md`，并补充或声明 `product_data_collection_observability`、`affected_layers`、N/A 原因与验证摘要。验证摘要至少覆盖适用层级中的行为事件、请求日志、直接 API、Task Trace、脱敏、保留周期、OpenAPI/Orval、端侧链路 ID 透传或其不适用原因。
