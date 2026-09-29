## 背景

OpenSpec 中文优先校验的目标是发现 Change 文档中的英文脚手架标题和英文任务项。现有语言脚本以全部 active Change 为默认范围，适合全局门禁，但不适合单个 Change 的实现验收；`scripts/validate-openspec.sh` 作为 OpenSpec 校验总入口，也需要能透传同一聚焦口径。

并行 Change 中，一个尚未清理的 Change 会阻塞另一个已经完成清理的 Change，用户无法从脚本结果直接判断当前 Change 是否达标。

## 设计决策

### D1. 默认行为保持全量 active 校验

不传参数时继续扫描 `openspec/changes/*/*.md`，保持现有 CI 和全局治理校验语义。

理由：全量 active 校验仍能发现仓库级 OpenSpec 文档语言漂移，不能因为新增聚焦模式而降低全局门禁。

### D2. 使用 `--change` 聚焦单个或多个 Change

新增 `--change <change-id>` 参数，并允许重复传入。脚本只读取指定 Change 目录下的受控 Markdown 文档。

理由：重复参数比逗号字符串更适合命令行组合，也避免 Change ID 中字符解析产生歧义。

### D3. 归档校验与聚焦参数组合

`--include-archive` 与 `--change` 同时出现时，脚本在 `openspec/archive/*-<change-id>/` 中查找目标归档 Change。目标不存在时失败。

理由：归档后仍需要按单 Change 复核语言规则，同时不存在的目标不能静默跳过。

### D4. 残留分离报告不影响当前 Change 结论

`--residual-report` 只能与 `--change` 配合使用。当前 Change 校验通过后，脚本可输出非当前 Change 的中文残留摘要，但残留项不改变当前命令退出码。

理由：用户需要知道全仓仍有残留，但单 Change 验收不应被并行 Change 阻塞。

### D5. OpenSpec 校验总入口透传聚焦参数

`scripts/validate-openspec.sh --change <change-id>` 串行运行当前 Change 中文优先校验与 `openspec validate <change-id>`。`--include-archive` 命中归档 Change 时，语言校验检查归档文档，结构校验改为校验已合并的正式规格。不传 `--change` 时继续执行全局目录结构校验，并运行默认全量中文优先校验。

理由：总入口应覆盖单 Change 常用 OpenSpec 门禁，避免调用方在每个命令中重复拼接语言校验与结构校验。

## 冲突处理

- 若 active 和 archive 中都存在同名 Change，身份唯一性脚本应先阻断；语言校验只按目录事实收集命中文档。
- 若指定 Change 存在但缺少部分文档，语言校验只检查已存在的受控文档；结构完整性由 `openspec validate <change-id>` 负责。
- 若未指定 Change，语言脚本继续按原全量逻辑运行；总入口继续保留目录结构校验，并补充全量中文优先校验，避免破坏既有调用方。
- 若指定 `--residual-report` 但未指定 `--change`，脚本应按参数错误失败，避免全量模式下产生含义重复的残留报告。

## 验证策略

- 运行目标 Change 聚焦语言校验，确认本 Change 文档通过。
- 运行不存在 Change 的聚焦语言校验，确认脚本失败且输出明确原因。
- 运行 `--change` 与 `--residual-report` 组合，确认当前 Change 通过且非当前 Change 残留只作为报告输出。
- 运行 `bash scripts/validate-openspec.sh --change optimize-openspec-language-change-scope --residual-report`，确认总入口可聚焦当前 Change 并执行结构校验。
- 运行 `bash scripts/validate-openspec.sh --change __missing__`，确认总入口透传目标不存在失败。
- 运行默认全量语言校验，确认旧行为仍可用；如被其他并行 Change 阻塞，则记录为既有 active Change 漂移，不影响本 Change 聚焦结论。
- 运行 `openspec validate optimize-openspec-language-change-scope`、目录结构校验、上下文预算校验和 Sprint scope 校验。

## 产品数据采集与链路观测

```yaml
product_data_collection_observability:
  status: not_applicable
  affected_layers: []
  reason: 本次只修改本地治理校验脚本和 OpenSpec 文档，不触达 API、DB、Web 请求封装、行为埋点、请求日志、Task Trace 或对象存储。
  validation: 通过脚本级聚焦校验、OpenSpec 校验和治理门禁验证；无需新增产品数据采集或链路观测验收。
```
