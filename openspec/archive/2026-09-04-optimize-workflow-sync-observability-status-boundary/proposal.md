## 背景与动机

Workflow Sync 需要从 Issue、Change 和 Sprint 文档中读取主状态，并同步派生文档。产品数据采集治理引入 `product_data_collection_observability.status` 后，轻量 Frontmatter 解析若不区分缩进层级，可能把嵌套声明状态误读为顶层 `status`，导致 Issue 或 Change 主状态被错误推导。

## 变更内容

- 收紧 Workflow Sync 轻量 Frontmatter 解析边界，只把顶层键作为主状态、标题、优先级等事实源。
- 增加单元测试，覆盖嵌套 `product_data_collection_observability.status` 不覆盖顶层 `status` 的场景。
- 补充 OpenSpec、Sprint scope 和治理日志，记录本次纯治理脚本优化。

## 影响范围

- Workflow Sync：`scripts/workflow_sync/collect.py`。
- 测试：`tests/unit/test_workflow_sync_engine.py`。
- OpenSpec：`harness-runtime` delta spec。
- Sprint：`sprint-004` 追加纯治理 Change。
- 产品数据采集与链路观测：N/A，本次只修复治理脚本对既有声明字段的解析边界，不新增 API、DB、请求日志、行为事件、Task Trace、对象存储或请求封装。

