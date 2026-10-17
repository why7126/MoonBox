---
title: 评审迁移后注册表恢复验证
created_at: 2026-10-07 15:00:31
updated_at: 2026-10-07 15:00:31
---

# 评审迁移后注册表恢复验证

## 真实偏差与恢复

BUG-0033 七份文件存在于 review 目录，bug/review/trace 为 approved；注册表旧路径为 plan、状态 pending_review。Firefox 的 localhost:18102/requirements 实际显示待评审、六份文档缺失且动作禁用。

2026-10-07 对完整 BUG-0033 ID 执行 promote-issue-stage.py --to review：已迁移目录保持原位，定向 Workflow Sync 返回 0，更新注册表和索引，acceptance 来源事件同步。三个子文档语义 warning 为 review approved、root-cause confirmed、workaround draft，不将这些状态强改为 Issue 生命周期。BUG-0033 未纳入 Sprint。

Firefox 刷新后：当前阻塞 1 → 0，待评审 1 → 0，已评审 0 → 1；BUG-0033 展示 bug/trace/review/acceptance/root-cause/workaround，加入迭代按钮可用。点击 review.md，抽屉加载实际评审结论通过；未发送 Agent 命令或编辑文档。

## 回归边界

聚焦 pytest 共 57 passed；唯一 warning 为现有 Starlette/httpx 弃用提示。命令选择 tests/unit/test_review_promotion_sync.py、test_workflow_sync_patch.py、test_workflow_sync_engine.py、test_promote_issues_for_archive.py，以及 src/backend/tests/test_governance_review.py。新增六项为真实 CLI 临时仓库回归，不是 mock 同步成功。

真实脚本在临时仓库运行，覆盖首次迁移、同步失败保留目录、重试恢复、重复执行、无关注册表行保留、dry-run/check 无写入、退出零但未同步仍失败、目标目录冲突。另运行工作流 patch/engine、归档兼容与后端评审门禁套件。

当前事实源已修复，不等同于 BUG-0033 的独立源码权限问题已修复。未重建服务镜像，未宣称新的模型驱动端到端评审已执行。当前 source 工作区读取的仓库脚本已更新；copy 模式需按现有控制文件同步入口取得更新。
