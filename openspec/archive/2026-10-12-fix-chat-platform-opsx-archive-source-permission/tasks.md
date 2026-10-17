---
title: Chat 平台 source 工作区归档权限与状态诊断修复
created_at: '2026-10-04 11:17:53'
updated_at: 2026-10-10 07:21:24
---

# Chat 平台 source 工作区归档权限与状态诊断修复

## 实施

- [x] 为 Chat 写策略新增 `archive_write`，仅 `/opsx-archive <完整 REQ 或 BUG ID>` 且目标对象可写时启用。
- [x] 为执行容器新增 `moonbox-archive` permission profile，并保持 `moonbox-governance` 不含生效规格与归档目录写权限。
- [x] 调整本地 Chat 平台 worker 的 source root 挂载，让受信任 source 模式可写真实仓库，backend 保持只读。
- [x] 将未创建 executor turn 的 setup/workspace/sandbox 失败记录为 `failed`，保留安全错误码并释放会话占用；已创建 executor turn 后不可确认仍保留 `unknown`。
- [x] 更新 Change 身份校验，忽略 active/archive 根下隐藏系统目录。

## 验证

- [x] 后端测试覆盖 archive 写策略、权限 profile、source 挂载配置和 setup 失败终态。
- [x] 脚本测试覆盖隐藏系统目录不再阻断 Change 身份校验。
- [x] 运行相关 pytest、OpenSpec 中文校验、Workflow Sync，并记录结果。
- [x] 补充本地 source/copy 与 archive 权限边界说明；真实 Docker archive 链路留给重建 worker 后复验。

## 文档与同步

- [x] 同步 BUG-0026 trace、acceptance 和 Sprint/Change 状态。
- [x] 如部署文档涉及 source/copy 工作区差异，补充本地部署默认 source 的写入边界说明。
- [x] 完成后通过 Workflow Sync 维护 BUG、Sprint 与 Change 状态。

## 验收返修

- [x] AF-001：移除 `run_claim` 的旧目录名前置校验，让 source 模式统一由 `_workspace_identity` 判定；补充 source 模式 `run_claim` 回归测试。完整台账见 `acceptance-fixes.md`。
- [x] AF-002：允许已验证 source root 的旧 copy 会话从 `workspace_id == conversation_id` 迁移到 `workspace_id: source`，并同步既有 baseline；补充旧 copy 到 source 的 `run_claim` 回归测试。完整台账见 `acceptance-fixes.md`。
- [x] AF-003：source 模式 workspace 快照改为尊重 Git exclude 规则，排除 `.gitignore` 已忽略的运行态数据，避免 `data/runtime/**` 进入 baseline 并触发容量边界；补充 ignored runtime 回归测试。完整台账见 `acceptance-fixes.md`。
- [x] AF-004：Chat Platform 私有执行数据目录禁止位于 source root 内，启动脚本自动将旧仓库内配置迁移到源仓库同级私有目录，避免 `/work` 与 `/runtime` 容器挂载重叠；补充平台预检回归测试。完整台账见 `acceptance-fixes.md`。
- [x] AF-005：归档权限策略兼容旧版 `source_bug` / `source_requirement` trace 字段，并同步 `archive_write` API schema 与前端标签；补充旧 `source_bug` BUG 归档权限回归测试。完整台账见 `acceptance-fixes.md`。
- [x] AF-006：纠正产品归档入口语义，需求中心归档按钮继续跳转对象 Chat 并填入 `/opsx-archive` prompt；保留 setup `cause_type` 诊断回归。完整台账见 `acceptance-fixes.md`。
- [x] AF-007：source 模式 baseline 存储键改为按会话独立，避免多个对象会话共享 `workspace_id=source` 触发唯一约束；补充多 source 会话 `run_claim` 回归测试。完整台账见 `acceptance-fixes.md`。
- [x] AF-008：归档移动后继续校验唯一 archive 的原对象关联；产品 prompt 驱动标准脚本，跨挂载安全迁移、半归档恢复与验证/sync/promote 串行闭环；补充延迟命令完成及可信用量收据恢复回归。完整台账见 `acceptance-fixes.md`。
- [x] AF-008 产品补证：修复 Issue promote 迁移间隙、执行容器无 HOME 的日志发现和流式通知队列溢出；88 passed、1 skipped；真实产品恢复轮次 completed、结果可见、脚本成功、最终用量已结算。
- [x] AF-009：精确识别 Chat 沙箱内空工具目录挂载点，真实违规目录仍阻断；归档移动前预校验，既有半归档保留续跑。聚焦回归与证据见 `acceptance-fixes.md`。

- [x] AF-010：修正 Chat 命令环境识别，安全清理宿主空工具目录；复验 60 passed、1 skipped。完整证据见 `acceptance-fixes.md`。

- [x] AF-011：全仓自有目录工具残留安全清理与校验；单元、后端及同款执行器镜像离线探针通过，真实产品新轮次待复验。完整台账见 `acceptance-fixes.md`。
- [x] AF-012：将 BUG-0026 Issue 验收范围整理为可计数 AC 复选框，补齐待复验的全仓目录与真实归档条目；保留表格证据和 pending 结论，验证卡片投影。完整台账见 `acceptance-fixes.md`。
- [x] AF-013：修复冷启动工具链预检误判、部署健康探针超时和 OpenSpec CLI 旧归档目录迁移间隙的归档权限撤销；聚焦回归通过，产品新轮次待复验。完整台账见 `acceptance-fixes.md`。
- [x] AF-014：补齐跨挂载复制时旧源与未完成标准目标并存的归档权限窗口，保持同一命令与唯一身份门禁；聚焦回归通过，产品首次归档仍待新样本复验。完整台账见 `acceptance-fixes.md`。
- [x] AF-015：历史引用再授权复用精确归档过渡门禁，保留未知轮次原始原因码；隔离回归及全新产品样本首次归档同轮闭环通过。完整台账见 `acceptance-fixes.md`。
