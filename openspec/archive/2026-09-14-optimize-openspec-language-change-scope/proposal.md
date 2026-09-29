## 背景与动机

当前 `scripts/validate-openspec-language.py` 默认扫描全部 active OpenSpec Change。多个 Change 并行推进时，任意一个未完成或仍含英文脚手架标题的 Change 都会让另一个 Change 的语言校验失败，导致校验结论无法准确归因。

本次治理优化为语言校验脚本和 OpenSpec 校验总入口增加 Change 范围参数，使 `/spec-opt`、`/opsx-apply` 和单 Change 验收可以只校验当前 Change，同时保留默认全量 active 校验与归档校验能力。

## 变更内容

- 为 `scripts/validate-openspec-language.py` 增加 `--change <change-id>` 参数，支持重复传入多个 Change。
- 为 `scripts/validate-openspec.sh` 增加 `--change <change-id>` 参数，聚焦运行当前 Change 中文优先校验与 `openspec validate <change-id>`。
- 未传 `--change` 时保持既有全量 active Change 校验行为。
- 传入 `--change` 时只校验目标 Change 的 `proposal.md`、`design.md`、`tasks.md`、`trace.md`、`acceptance.md` 和 `test-plan.md`。
- 传入 `--residual-report` 时输出非当前 Change 的中文残留摘要，但不影响当前 Change 退出码。
- 配合 `--include-archive` 时允许校验目标归档 Change。
- 目标 Change 不存在时输出明确失败信息，避免静默通过。

## 能力影响

### 新增能力

无。

### 修改能力

- `agent-workflow-tooling`：OpenSpec 中文优先语言校验与校验总入口支持按 Change 聚焦，减少并行 Change 之间的校验干扰。

## 影响范围

- 治理脚本：`scripts/validate-openspec-language.py`、`scripts/validate-openspec.sh`。
- OpenSpec：新增纯治理 Change 和 delta spec。
- Sprint：纳入 `sprint-006` 作为纯治理范围项。
- 文档：新增治理迭代日志并更新 `docs/spec-logs/CHANGELOG.md`。
- API、数据库、Web、管理端、客户端生成、Docker Compose、安全：不适用，本次不触达业务运行时、接口契约、数据结构、部署拓扑或权限边界。
