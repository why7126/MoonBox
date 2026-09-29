---
requirement_id: REQ-0032-requirement-center-sprint-dropdown-status
title: 需求中心 Sprint 下拉列表新增状态展示
owner: product
source: requirement.md
created_at: 2026-09-14 14:50:40
updated_at: 2026-09-14 14:50:40
---

# 业务流程

## 1. 主流程

```text
用户进入需求中心
  -> 选择授权项目
  -> 加载稳定快照与卡片数据
  -> 构建 Sprint 筛选选项
  -> 读取每个 Sprint 的状态事实
  -> 显示 Sprint ID / 名称 + 状态
  -> 用户选择 Sprint
  -> 按选中 Sprint 刷新卡片、统计和文档入口
```

## 2. 状态解析流程

```text
Sprint 候选项
  -> 是否为“全部 Sprint”
      -> 是：展示聚合筛选项，不绑定单个状态
      -> 否：读取 Sprint 状态事实源
          -> planning      -> 规划中
          -> in_progress   -> 进行中
          -> completed     -> 已完成
          -> archive 目录事实 -> 已归档
          -> 缺失/非法/冲突 -> 状态待核实
```

状态事实源优先级：

1. 当前项目稳定快照中的结构化 Sprint 状态字段。
2. `iterations/change|archive/<sprint-id>/sprint.yaml` 的状态与目录阶段。
3. Workflow Sync 派生出的可追溯状态摘要。
4. 无法唯一确认时降级为“状态待核实”。

## 3. 异常与权限流程

```text
加载 Sprint 选项失败
  -> 判断是否为项目/权限/快照错误
  -> 沿用需求中心现有错误反馈
  -> 不暴露内部路径或原始日志

单个 Sprint 状态异常
  -> 保留该 Sprint 可选项
  -> 标记“状态待核实”
  -> 其他 Sprint 正常展示

用户无项目读取权限
  -> 不展示受限 Sprint
  -> 不通过数量差异泄漏受限对象
```

## 4. 与父需求差异

父需求 REQ-0012 建立需求中心页面与基本需求查看能力。本需求不扩展需求中心的生命周期规则、卡片动作或 Sprint 管理能力，只增强筛选控件中的 Sprint 状态可见性。

与 REQ-0026 的差异：REQ-0026 关注卡片与 Change 追溯，本需求关注工具栏 Sprint 筛选下拉选项。实现时可以复用其“事实源优先、异常不伪造正常状态”的经验，但不新增 Change 卡片能力。

与加入迭代弹窗的差异：现有加入迭代弹窗已有现有迭代选项和状态/容量模型，本需求重点补齐需求中心工具栏 Sprint 筛选下拉；后续实现需确保两个入口的状态口径一致。

## 5. 非目标流程

- 不提供 Sprint 新建、编辑、完成或归档。
- 不自动修复状态漂移。
- 不把“全部 Sprint”伪装为单个 Sprint 状态。
- 不引入跨项目 Sprint 汇总。
