---
requirement_id: REQ-0027-requirement-center-command-chain-realization
title: 需求中心卡片全命令产品链路真实化业务流程
created_at: 2026-09-30 12:55:45
updated_at: 2026-10-04 10:43:55
---

# 需求中心卡片全命令产品链路真实化业务流程

## 主流程

```text
授权项目 + 完整 REQ ID + 当前版本
  -> 服务端读取对象、权限、阶段和必备文档
  -> 需求分析：只读 Chat -> 返回分析（治理文件不变）
  -> 生成需求：captured/exploring -> draft
  -> 完善需求：draft/enriching -> pending_review
  -> 发起评审：通过 approved / 拒绝 rejected / 延后 deferred
  -> 加入迭代：approved -> in_sprint
  -> 生成 OpenSpec：同 Sprint 关联 Change，展示待开发
  -> 开始开发：真实启动 opsx.start -> 研发中
  -> 开发、验证和文档完成：opsx.apply -> 验收中
  -> 验收通过后完成归档：合并规格、归档 Change、同步、迁移 Issue
  -> 全部关联 Change 归档 -> done
```

每个箭头都是独立动作；成功不自动执行下一命令。评审拒绝/延后在当前结论停止，重新处理遵循既有治理。无父 REQ，不存在父子流程覆盖；与原 Capture 测试记录的差异是本需求定义正式命令闭环，不继承 BUG-0014 的修复与验收结论。

## 写操作执行顺序

1. 从授权项目解析完整对象 ID，读取服务端最新状态、版本和必备文档；区分不存在、空文件与事实漂移。
2. 检查动作白名单、权限、阶段和确认选择；取消即终止，不创建写任务。
3. 建立可查询的操作身份；同对象冲突写串行，重试关联既有操作。此时只报告受理。
4. 受控 controller 执行对应命令，按该命令允许范围落盘、检查标题和产物完整性。
5. 执行对应 Workflow Sync；失败展示“文件已写入，状态同步失败，待恢复”，不标记 application 或 candidate 为完成。
6. 重新读取文件、索引和关联，完成事实一致才展示成功和重算下一动作。
7. 刷新卡片投影和文档入口；工作区、assistant 输出和 candidate 仅保留为候选或执行证据。

本地常驻部署默认以真实治理事实源为工作区：仓库绑定输出 `workspace_mode: source`，执行器直接使用 `source_root` 当前工作树并直接落盘。共享生产仓库、多人同时编辑或强隔离审阅场景才显式使用 `workspace_mode: copy`，并继续依赖副本同步、候选应用和未应用成果保护。

## 异常与恢复

| 情况 | 用户结果 | 恢复约束 |
|---|---|---|
| 对象不存在、权限不足、越级或缺材料 | 安全原因提示，未执行 | 补材料或刷新权限后重新验证 |
| 提交版本过期、外部文件变化 | 冲突，保留已有文件 | 刷新比较，不盲目覆盖 |
| 重复点击、超时、断网 | 查询同一操作 | 结果未知时不换幂等身份重做 |
| 多文件写入中断 | 部分写入、待恢复 | 核实已写步骤与版本，重放未完成步骤 |
| Workflow Sync 失败 | 同步失败、待恢复 | 保留真实文件事实，重放同步并验证索引 |
| candidate 或工作区基于的事实源已变化 | conflict/stale，不更新卡片阶段 | 刷新事实源后重新生成或人工确认恢复路径 |
| 归档部分失败 | 待恢复，REQ 不提前 done | 检查已合并/已迁移步骤后续执行，避免重复合并 |
| 外部修改或权限变化阻碍恢复 | 明确阻塞和操作标识 | 保留证据，不删锁或强改状态冒充恢复 |

## 权限矩阵

| 服务端能力 | 分析/文档读取 | 七类写操作 | 操作结果查询 |
|---|---|---|---|
| 未登录 | 走既有登录流程 | 拒绝 | 拒绝 |
| 无项目访问权限 | 受控拒绝，不泄漏对象存在性细节 | 拒绝 | 拒绝 |
| 项目只读权限 | 对象可读时允许分析 | 拒绝，说明权限不足 | 仅返回既有策略允许的结果 |
| 对应动作写权限 | 允许 | 仍需状态、材料、确认与版本门禁 | 按项目及操作访问策略验证 |
| 运行中权限被撤销 | 后续读取重验 | 后续写入/恢复重验，保留已发生事实 | 重验后拒绝未授权内容 |

角色到能力的真实映射由 Change 盘点现有权限实现后填写，不能采用客户端角色声明。前端禁用与服务端拒绝分别验收。

## 现有复用入口与设计待办

以下为需求完善阶段的历史源码盘点和设计待办，不代表当前实现状态。八动作的现行产品验收结论以 Change `evidence/acceptance/`、REQ `acceptance.md` 和当前文件事实源为准。

| 入口 | 已见事实 | 后续设计任务 |
|---|---|---|
| src/web/src/pages/catalog/RequirementCenterPage.tsx | ActionDialog、confirmActionDialog、runIssueAction 与动作映射 | 逐动作确认真实执行、替换仅演示反馈的分支并保留卡片结构 |
| src/backend/app/governance/api.py | /api/v1/chat/governance-preparations 当前 action 仅 req-generate；候选应用与操作查询接口存在 | 评估扩展白名单、动作参数和完整 ID 校验；不把已有接口宣称支持全部动作 |
| src/backend/app/governance/controller.py | tick 查询 pending/applying/recovering 并调用 writer.process | 核查七动作隔离执行、恢复和结果协议适用性 |
| src/backend/app/api/v1/requirement_center.py | context、文档读取和 Capture 接口 | 复用结果重读与授权上下文，Capture 不重新建设 |
| scripts/workflow_sync/engine.py | req.complete 支持 draft/enriching 到 pending_review | 复用事件映射与索引投影，禁止另造状态机 |

执行结果协议需表达：操作身份、完整对象身份、动作、受理/运行/待补充/失败/完成、已落盘步骤、同步结果、安全错误摘要、允许访问的产物引用、刷新后的版本、可恢复性。字段名、HTTP 状态码、锁实现、持久化表复用与接口版本在 Change 中确定；禁止把上述语义当成现有 API 字段。
