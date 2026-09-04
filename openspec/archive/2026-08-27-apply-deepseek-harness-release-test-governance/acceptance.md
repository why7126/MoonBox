---
change_id: apply-deepseek-harness-release-test-governance
status: pending
created_at: 2026-08-27 08:06:34
updated_at: 2026-08-27 08:06:34
---

# 验收

## 验收标准

- 发布规则包含构建记录、产物 manifest、输入漂移和发布写入边界。
- 测试规则包含测试分区、慢测试调度、串行前置用例、并行池配置和失败摘要要求。
- 命令执行顺序文档的治理脚本门禁矩阵覆盖发布构建记录和慢测试调度。
- spec-logs 中存在一份本次学习报告，并在 CHANGELOG 中登记。
- 聚焦 diff 未触碰业务 `src/`。
- 必需治理校验和 Workflow Sync 已执行或记录阻塞原因。
