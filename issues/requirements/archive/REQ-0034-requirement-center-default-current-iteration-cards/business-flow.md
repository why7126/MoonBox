---
requirement_id: REQ-0034-requirement-center-default-current-iteration-cards
title: 需求中心默认只显示当前迭代卡片
document_status: pending_review
owner: product
source: requirement.md
created_at: 2026-09-14 14:56:26
updated_at: 2026-09-15 00:10:00
---

# 业务流程

## 默认进入流程

```text
用户进入需求中心
  -> 读取当前空间与项目上下文
  -> 获取需求中心稳定快照
  -> 从 Sprint 生命周期事实源识别当前迭代候选
      -> 0 个当前迭代：默认选中未纳入 Sprint，若仍无卡片则展示空态 + 清空/历史入口
      -> 1 个当前迭代：默认展示该 Sprint 相关卡片 + 未纳入 Sprint 卡片
      -> 多个当前迭代：默认展示全部当前迭代相关卡片 + 未纳入 Sprint 卡片
  -> 渲染 REQ / BUG / 独立 Change 卡片
  -> 保持 Sprint 多选状态显示为当前 Sprint + 未纳入 Sprint 范围
```

## 范围切换流程

```text
用户打开 Sprint 筛选
  -> 选择当前 Sprint / 单个 Sprint / 清空为全部 / 历史 Sprint / 归档 Sprint / 取消或选中未纳入 Sprint
  -> 系统按显式选择刷新卡片集合
  -> 保留搜索、对象类型、负责人、优先级和归档可见性等既有筛选
  -> 用户点击重置或返回默认视图
  -> 恢复当前 Sprint + 未纳入 Sprint 范围
```

## 刷新与上下文切换流程

```text
用户手动刷新
  -> 保留用户当前显式选择的 Sprint 范围
  -> 重新读取稳定快照
  -> 更新当前范围下的卡片集合

用户切换空间或项目
  -> 废弃旧上下文迟到响应
  -> 按新上下文重新识别当前迭代和未纳入 Sprint 候选
  -> 回到新上下文的默认当前 Sprint + 未纳入 Sprint 范围
```

## 异常处理流程

```text
Sprint 事实源缺失或解析失败
  -> 不静默回退全量卡片
  -> 展示轻量错误态或最近一次可用安全结果
  -> 提供重试、清空 Sprint 或选择历史 Sprint 入口
  -> 错误信息脱敏，不暴露内部路径、堆栈、密钥或原始文档全文
```

## 与父需求差异

父需求 REQ-0012 定义了需求中心九阶段看板、卡片、筛选和刷新框架。本需求不改变九阶段生命周期和卡片组件族，只调整默认卡片范围的进入口径：从可能的全量入口改为当前 Sprint + 未纳入 Sprint 优先，并补齐多当前迭代、非当前范围查看、刷新一致性和异常降级规则。

## 数据依赖

- Sprint 生命周期事实源：`iterations/change/` 与 `iterations/archive/` 下可识别的 Sprint 及其状态。
- Issue trace 与 registry：确定 REQ/BUG 的 Sprint 归属、状态和文档入口。
- OpenSpec Change trace 与 Sprint scope：确定独立 Change 与当前 Sprint 的关系。
- 需求中心稳定快照：防止迟到响应覆盖当前项目或范围。
