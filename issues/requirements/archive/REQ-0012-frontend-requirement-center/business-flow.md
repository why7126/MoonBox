---
requirement_id: REQ-0012-frontend-requirement-center
title: MoonBox 前台需求中心
owner: product
source: requirement.md
priority: P1
created_at: 2026-08-10 12:57:18
updated_at: 2026-08-10 12:57:18
---

# 业务流程

## 1. 生命周期总览流程

```text
Capture Pool
  -> Planning
  -> Review Ready
  -> Approved
  -> Sprint Planning
  -> Ready for Dev
  -> In Development
  -> Acceptance
  -> Done
```

每个对象在阶段内 MUST 保留文档产物和 trace 证据。Requirement 与 Bug 共享阶段框架，但阶段主动作根据对象类型映射到不同 Skill。

## 2. 看板浏览与筛选流程

```text
进入需求中心
  -> 读取当前空间上下文
  -> 展示统计区、筛选工具栏和 9 阶段看板
  -> 用户搜索或筛选对象类型/负责人/优先级/Sprint
  -> 看板卡片按筛选条件刷新
  -> 用户查看卡片文档产物、阻塞状态、进度与下一步主动作
```

关键约束：

- 列头吸顶时 MUST 保持与横向滚动列对齐，不创建克隆表头。
- 卡片“更新于”文本保持弱层级，不得挤压标题、标签和阶段动作。
- Sprint 标签只在迭代规划及后续阶段展示，且每张卡片最多一个。

## 3. 阶段动作流程

```text
用户点击卡片主动作
  -> 前端识别对象类型 Requirement/Bug
  -> 前端识别当前阶段
  -> 系统检查阶段必需文档是否存在
  -> 系统检查权限、前置条件、幂等约束和审计要求
  -> 通过后触发对应 req-* / bug-* / sprint-* / opsx-* 动作入口
  -> 动作结果回写对象状态、文档产物、trace 和看板卡片
```

阶段动作映射：

| 阶段 | Requirement 主动作 | Bug 主动作 |
|---|---|---|
| 采集池 | `req-generate` | `bug-generate` |
| 规划中 | `req-complete` | `bug-complete` |
| 待评审 | `req-review` | `bug-review` |
| 已通过 | `sprint-propose --req` | `sprint-propose --bug` |
| 迭代规划 | `req-opsx` | `bug-opsx` |
| 待开发 | `opsx-apply` / `sprint-apply` | `opsx-apply` / `sprint-apply` |
| 研发中 | 查看任务进度 | 查看任务进度 |
| 验收中 | 继续验收 / 完成归档 | 继续验收 / 完成归档 |
| 已完成 | 查看归档 | 查看归档 |

## 4. 组织与空间切换流程

```text
用户打开用户菜单
  -> Hover“切换空间”
  -> 右侧展示空间列表浮层
  -> 用户搜索或按组织浏览空间
  -> 用户单选目标空间
  -> 系统更新当前空间、用户区摘要和本地最近选择
  -> 看板按新空间上下文刷新
```

交互边界：

- Hover 进入空间列表前，一级用户菜单不得关闭。
- 空间列表关闭应具备短延时防误关闭。
- 任一时刻最多一个空间处于选中状态。
- 创建/加入空间入口不得破坏当前已选空间状态。

## 5. 空间设置流程

```text
用户打开用户菜单
  -> 点击“空间设置”
  -> 居中分栏弹窗打开
  -> 用户切换左侧设置分组
  -> 用户编辑常规配置
  -> 点击保存
  -> 系统校验权限、字段和幂等提交
  -> 保存成功后关闭弹窗并展示 fixed toast
```

设置分组：

- 常规：空间名称、标识、描述、默认时区。
- 成员与权限：成员角色与访问范围。
- Agent：默认 Agent 与执行策略。
- Skill：空间可用 Skill 与默认组合。
- 集成：代码仓库、通知渠道和外部服务连接。
- 高级设置：空间归档、转移和高风险操作。

## 6. 与父需求差异

当前 REQ 没有父需求。它是 MoonBox 前台需求中心的独立首版能力，承接已有治理命令、Issue 文档包、Sprint 和 OpenSpec 流程，但不直接修改既有管理后台用户管理、后台认证或对象存储能力。
