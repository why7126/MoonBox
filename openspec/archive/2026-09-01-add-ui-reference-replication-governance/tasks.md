# 任务

- [x] 创建 OpenSpec Change，并明确纯治理范围。
- [x] 将 Change 纳入 Sprint scope。
- [x] 更新 UI 设计规则与原型验收标准，新增 UI 参考稿复刻契约。
- [x] 更新 explore/req/opsx 相关技能，贯通参考稿反向工程、selector 映射、computed style 采样和分批验收。
- [x] 更新 AGENTS 与上下文预算规则，补充入口和读取边界。
- [x] 写入治理迭代日志和目录级变更历史。
- [x] 补充 OpenSpec delta spec。
- [x] 运行治理校验、OpenSpec 校验、Workflow Sync 和 AI Usage Hook。

## 验证记录

- 通过：`python scripts/validate-agent-context-budget.py`
- 通过：`python scripts/validate-openspec-language.py`
- 未通过：`python scripts/validate-directory-structure.py`，原因是根目录存在既有未登记目录 `.vite`，非本次变更新增。
- 通过：`openspec validate add-ui-reference-replication-governance`
- 通过：`python scripts/validate-sprint-scope.py sprint-004`
- 通过：`python scripts/sync-workflow-status.py --event opsx.apply --change add-ui-reference-replication-governance --sprint auto`
- 完成：`python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change add-ui-reference-replication-governance --sprint sprint-004 --json`，返回 `warning/unavailable`，原因是当前会话无可持久化 command-run token 事件。
