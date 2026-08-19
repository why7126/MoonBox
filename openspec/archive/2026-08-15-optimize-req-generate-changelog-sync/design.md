## 设计

### 派生刷新位置

在 `scripts/workflow_sync/patch.py` 新增 `patch_issue_changelog_index`，由 `scripts/workflow_sync/engine.py` 在聚焦 Issue 事件中调用。

调用范围：

- `req.*` 且目标 Issue 为 `--req`。
- `bug.*` 且目标 Issue 为 `--bug`。
- `opsx.apply`、`opsx.modify`、`opsx.archive` 且 derived Issue 关联当前 Change。

### 行生成策略

REQ 行字段：

```text
REQ | 标题 | 当前状态 | 阶段 | 优先级 | 关联 Sprint | 关联 Change | 最近更新时间 | 下一步 | 事实源
```

`req.generate` 后目标状态通常为 `draft`，下一步为 `/req-complete <REQ-full-id>`。

### 安全边界

- 不复制完整 trace、验收正文、用户原始输入或日志。
- 只写目录级当前态快照。
- 事实源路径使用仓库相对路径。
- 不读取或输出真实 env、密钥、客户数据或本机绝对路径。

## 取舍

- 选择单行替换而非全量重建：降低对历史排序和人工摘要的扰动。
- 同步支持 BUG 与 opsx 聚焦事件：复用同一派生刷新机制，避免重复实现。
- 最近更新时间使用 Workflow Sync 执行时间：表达派生快照刷新时刻，而非替代 trace 生命周期时间。
