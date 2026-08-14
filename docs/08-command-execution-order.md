---
purpose: 命令执行顺序速查
content: MoonBox REQ/BUG、Sprint、OpenSpec、发布、镜像与产品手册命令的推荐顺序和串行门禁
created_at: 2026-08-07 23:20:00
updated_at: 2026-08-13 08:58:35
owner: MoonBox 产品团队
---

# 命令执行顺序速查

本文用于约束 AI 在 MoonBox 中推荐和执行工作流命令的顺序。原则是先评审、再纳入 Sprint、再创建 Change、再实现、再归档，发布链路位于交付闭环之后。

## 标准链路

```text
/req-capture 或 /bug-capture
→ /req-generate 或 /bug-generate
→ /req-complete 或 /bug-complete
→ /req-review --approve 或 /bug-review --approve
→ /sprint-propose
→ /req-opsx 或 /bug-opsx
→ /opsx-apply
→ /opsx-modify（可选）
→ /opsx-archive
→ /sprint-archive
→ /sprint-exps
→ /release-propose
→ /release-prepare
→ /usage-docs-generate 或 /usage-docs-update 或 /usage-docs-validate
→ /image-prepare
→ /image-build
→ /release-publish
```

## REQ / BUG 到 OpenSpec

- 未评审的 REQ/BUG 不得进入 Sprint、不得转 OpenSpec、不得执行开发。
- 已评审 REQ/BUG MUST 先通过 `/sprint-propose` 纳入 Sprint 正式范围，并由 Workflow Sync 同步为 `in_sprint`，再通过 `/req-opsx` 或 `/bug-opsx` 创建 Change。
- `/req-review --approve` 的下一步 MUST 是 `/sprint-propose --req <REQ-full-id>`；`/bug-review --approve` 的下一步 MUST 是 `/sprint-propose --bug <BUG-full-id>`。
- `/req-opsx` 和 `/bug-opsx` 遇到 `status: approved` 但尚未 `in_sprint` 时 MUST 停止，并提示先运行对应 `/sprint-propose`。
- `/req-opsx` / `/bug-opsx` 完成后 MUST 运行 Workflow Sync，把新 Change 回填到同一个 Sprint 的 `changes[]` 与 `scope_estimates[].change`。
- 如果 REQ/BUG 已经纳入 Sprint，但 `/opsx-apply --dry-run` 仍解析不到 Sprint，优先修复 `sprint.yaml` 机器事实源，不要求用户重复口头确认。

## Apply / Modify / Archive

- `/opsx-apply` 前 MUST 通过 `python scripts/sync-workflow-status.py --event opsx.apply --change <change-id> --sprint auto --dry-run` 确认目标 Change 位于 Sprint scope。
- `/opsx-modify` 只用于 `/opsx-apply` 之后、`/opsx-archive` 之前的验收返修；超出原 Change 范围时应创建新 REQ/BUG 或新 Change。
- `/opsx-archive` 只能归档已完成 tasks 且 artifact 完整的 Change。
- 归档步骤必须严格串行：归档脚本或 OpenSpec archive → 目录校验 → env ignore 校验 → archive evidence → Workflow Sync → Issue promote → AI Usage。

## Sprint

- `sprint.yaml` 是 Sprint scope 的机器事实源；不得只手工编辑 `sprint.md` 或 Workflow Sync marker 块。
- 已存在 Sprint 追加范围时，先运行 `scripts/add-sprint-scope-item.py` 更新 `sprint.yaml`，再运行 Workflow Sync 和 `validate-sprint-scope.py`。
- 多个范围项写入同一个 Sprint 时必须串行运行，不得并行写同一个 `sprint.yaml`。
- `/sprint-archive` 前必须确认 Sprint 中全部 Change 已归档，并通过 readiness、归档路径残留和 stale scan 门禁。

## 发布、镜像和产品手册

- `/release-propose` 可在 Sprint 接近完成时创建计划，但 `/release-prepare` 和 `/release-publish` 不得伪造未完成门禁为通过。
- `usage-docs-*` 属于公开产品手册链路，必须遵守公开安全和截图/manifest 门禁。
- `/image-prepare` 和 `/image-build` 基于 release 对象和镜像计划执行；不得读取或输出真实 `.env`、密钥、连接串或私有地址。
- `/release-publish` 位于发布公告、产品手册、镜像、部署验证完成之后。

## 下一步参数规则

- “原始 Issue ID”指完整目录 ID，包含编号和 slug，例如 `REQ-0100-mintlify-docs-site-ia-content-experience`、`BUG-0125-miniapp-sku-detail-media-original-load`。
- REQ 来源链路的所有 `/req-*` 和后续 `/opsx-*` 下一步命令 MUST 使用同一个完整 `REQ-xxxx-slug`，不得在 `/opsx-apply`、`/opsx-modify` 或 `/opsx-archive` 中改用 `<change-id>`。
- BUG 来源链路的所有 `/bug-*` 和后续 `/opsx-*` 下一步命令 MUST 使用同一个完整 `BUG-xxxx-slug`，不得在 `/opsx-apply`、`/opsx-modify` 或 `/opsx-archive` 中改用 `<change-id>`。
- 无 REQ/BUG 来源的纯治理 Change 才使用 `<change-id>` 作为 `/opsx-*` 参数。
- `/explore` 与 `/opsx-explore` 输出下一步 `/opsx-*` 命令时同样适用上述规则；若用户只提供 `<change-id>`，必须先从 Change 文档和 Sprint `scope_estimates` 识别是否存在 `requirement` 或 `bug` 来源。
- 「下一步」只放可直接执行的命令；「待用户决策/处理」只放缺失输入、范围选择、证据补充、验收或发布确认、阻塞项。

### 示例

```text
正确：下一步：/opsx-apply REQ-0012-frontend-requirement-center
错误：下一步：/opsx-apply add-frontend-requirement-center
```

```text
正确：下一步：/opsx-modify BUG-0009-frontend-admin-sidebar-version-mismatch
错误：下一步：/opsx-modify fix-frontend-admin-sidebar-version-mismatch
```

```text
正确：下一步：/opsx-apply optimize-explore-chain-identity
前提：该 Change 为无 REQ/BUG 来源的纯治理 Change，且已纳入 Sprint。
```

## 串行写入边界

以下步骤写入同一事实源，MUST 严格串行执行：

- 多次运行 `scripts/add-sprint-scope-item.py` 写同一个 `sprint.yaml`。
- Workflow Sync 写 Sprint 派生表、Issue trace、registry 或验收回填。
- `promote-issues-for-archive.py` 迁移 Issue 阶段。
- AI Usage hook 刷新同一 Sprint 或 release snapshot。

不得用并行工具同时运行上述写入步骤；每一步必须基于前一步写入后的最新文件状态继续。
