---
bug_id: BUG-0048-chat-legacy-panel-cleanup-removes-conversation
severity: high
created_at: '2026-10-19 18:48:04'
updated_at: '2026-10-19 18:48:04'
owner: 产品团队
related_requirement: REQ-0046-chat-execution-output-status-feedback
related_bug: BUG-0047-review-recovery-operation-record-missing
title: 旧治理面板清理误删聊天会话区域根因分析
---

# 旧治理面板清理误删聊天会话区域根因分析

## 根因状态

status: confirmed

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | screenshot | logs/review-recovery-deployment/page-verification.jpg | 目标会话加载后仅保留侧栏 | 产品主区域确实缺失 |
| E2 | code_path | src/web/src/runtimeBuild.ts:removeLegacyGovernancePanels | 候选包含全部 aria-label 节点，按递归 textContent 匹配后 remove | 任意祖先可被正文误命中 |
| E3 | reproduction | 实际函数最小 DOM 调用 | 带标签 chat-main 中含确认应用文字，removed=2，chatMainRetained=false | 无网络和模型依赖仍确定复现 |

## 已排除假设

API 返回 200 且执行服务 ready；最小 DOM 可独立复现，因此主区缺失不是该轮执行器预检失败。

## 修复方向

只清理具有明确旧面板标识的元素，正常消息、会话外壳和无关对话框不参与文本识别。

## 验证闭环

先增加失败回归，再修复并验证页面、轨迹和输入区域；重新执行评审并回读应用记录。

## 真实验收发现的关联阻断

新轮次 99093906-8e69-4248-b5d7-d67377d433fd 执行 completed，但候选 rejected/review_state，未生成应用。目标 trace 为 req_id、主文档为 requirement_id；review.py 状态门禁对二者均固定读取 requirement_id。新增三种结果兼容与两种冲突字段测试在旧代码下五项失败，确认校验字段契约不一致。拒绝后正式目录安全恢复为 plan/pending_review。

## 最终闭环

真实返修继续确认原生同步末尾换行被误判为验收内容越界，以及 source-mode 从仅有文档的治理投影 root 查找脚本导致 generic 拒绝。已兼容仅末尾换行并从可信 source_root 执行同步，前后校验两处事实一致。96项后端/40项Web回归通过；最终真实轮次 cff097ea-eadc-40c6-b8d9-671206988d51 completed，唯一应用 a4150523-b06b-4c4e-bc70-23a5a37a4748 applied/verified，恢复操作completed。五项AC通过、归档预演通过，ready；历史拒绝保持原样。
