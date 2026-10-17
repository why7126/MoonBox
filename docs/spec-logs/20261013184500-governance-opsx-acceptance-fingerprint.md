---
title: 自动验收指纹与归档续接门禁修正
created_at: 2026-10-13 18:45:00
updated_at: 2026-10-13 18:45:00
---

# 自动验收指纹与归档续接门禁修正

## 来源

BUG-0034 的 `/opsx-accept` 产品复验：纯治理 Change 首次归档后，`--finalize` 被活动 trace 缺失门禁阻断；Workflow Sync 刷新 Issue 生成投影后，自动验收清单被误判全部过期。

## 调整

- 归档验收门禁在活动 Change 不存在时，读取唯一 canonical archive 或 CLI 旧目录过渡 trace；歧义身份和未签认 Issue 仍阻断。
- Issue `acceptance.md` 的指纹保留验收条件，忽略 Workflow Sync 派生状态与结果块；验收标准同步说明该边界。
- 聚焦回归覆盖归档续接、安全拒绝和指纹稳定性。

## 验证

隔离产品 `source` 工作区归档与 `--finalize` 轮次均为 `completed`，目标命令退出码 0，Workflow Sync 0 errors；验收与归档相关单测 35 passed。产品原始事件与私有 SQLite 数据未转存本日志。
