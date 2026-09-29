## 设计目标

把 OpenSpec CLI template 的英文标题从“生成后靠人工发现再修”前移为“REQ/BUG 转 Change 时必须中文化”的命令契约，并用现有中文优先校验与上下文预算校验形成双层防回退。

## 中文标题映射

`/req-opsx` 和 `/bug-opsx` 在读取 `openspec instructions <artifact-id> --change <change-id> --json` 后，只复用 schema 顺序、artifact 依赖和结构意图。写入项目文档前，将标题替换为中文：

| 英文脚手架标题 | 中文标题 |
|---|---|
| `Why` | `背景` |
| `What Changes` | `变更内容` |
| `Capabilities` | `能力影响` |
| `New Capabilities` | `新增能力` |
| `Modified Capabilities` | `修改能力` |
| `Impact` | `影响范围` |
| `Context` | `背景与现状` |
| `Goals` | `目标` |
| `Non-Goals` | `非目标` |
| `Proposed Design` | `设计方案` |
| `Root Cause` | `根因` |
| `Proposed Fix` | `修复方案` |
| `Data and API` | `数据与 API` |
| `Risks` | `风险` |
| `Rollback Plan` | `回滚方案` |
| `Implementation` | `实施任务` |
| `Testing` / `Test Strategy` | `验证任务` / `测试策略` |
| `Documentation` | `文档同步` |

OpenSpec 关键字、命令、路径、API 字段、代码标识和已有 spec capability ID 可保留英文。`Requirement:` 后的标题仍以正式规格或 delta spec 目标能力为准，不做机械翻译。

## 校验策略

`scripts/validate-openspec-language.py` 已能识别 `Why`、`What Changes`、`Context`、`Impact`、`Implementation`、`Testing`、`Documentation` 等英文脚手架标题。两个 opsx 技能生成 Change 后继续运行当前 Change 聚焦中文校验，作为文档落盘后的门禁。

`scripts/validate-agent-context-budget.py` 增加对 `/req-opsx` 与 `/bug-opsx` 技能的 required 片段检查，要求保留“OpenSpec CLI 模板标题中文化”“CLI 模板标题”“项目标题”“背景”“变更内容”“能力影响”等契约词，避免后续技能改动删掉前置规则。

## product_data_collection_observability

```yaml
status: not_applicable
affected_layers: []
reason: 仅修改治理 Skill、规则、校验脚本和 OpenSpec 文档，不触达 API、DB、请求日志、行为事件、Task Trace、Web/管理端请求封装或对象存储。
validation: 通过上下文预算校验、OpenSpec 中文校验、目录结构校验、目标 Change 校验、Sprint scope 校验和 Workflow Sync 校验确认。
```
