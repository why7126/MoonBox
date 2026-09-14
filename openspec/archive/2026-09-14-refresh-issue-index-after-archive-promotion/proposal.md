---
created_at: 2026-09-14 09:01:23
updated_at: 2026-09-14 09:01:23
---

## 背景与动机

BUG-0014 归档时，`promote-issues-for-archive.py` 已将 Issue 目录迁入 `archive/`，但 `issues/bugs/_registry.yaml` 与 `issues/bugs/CHANGELOG.md` 仍短暂保留 `review/` 路径，需要额外运行一次 Workflow Sync 才恢复一致。

## 变更内容

- 在 Issue archive promote 成功后，自动重新加载已迁移 Issue。
- 复用 Workflow Sync 现有派生与 patch 能力，刷新 registry 与当前态看板行。
- 增加聚焦回归，覆盖迁移后 `archive/` 路径同步。

## 能力范围

### 修改能力

- `agent-workflow-tooling`: Issues 当前态看板索引。

## 影响范围

仅治理脚本、OpenSpec Change、治理日志和脚本级测试。不修改业务 `src/`、API、DB、Web、客户端、管理端、Orval 或部署。
