---
requirement_id: REQ-0037-current-iteration-archive-entry
title: 当前迭代容量区域新增归档当前迭代入口
created_at: 2026-09-14 23:35:53
updated_at: 2026-09-14 23:35:53
owner: product
source: requirement.md
---

# 业务流程

## 1. 主流程

```text
进入需求中心
  |
  v
加载当前迭代与容量事实源
  |
  +-- 无当前迭代 / 无可见 Sprint ------------+
  |                                        |
  |                                        v
  |                              不展示可执行归档入口
  |
  +-- 当前迭代 used_capacity = 0 ----------+
  |                                        |
  |                                        v
  |                              隐藏或禁用归档入口
  |
  +-- 当前迭代 used_capacity > 0
           |
           v
  显示“归档当前迭代”入口
           |
           v
  用户点击入口
           |
           v
  打开归档确认流程
           |
           v
  执行 Sprint archive 既有门禁检查
           |
           +-- 门禁失败 --------------------+
           |                                |
           |                                v
           |                      展示失败项与修复入口
           |
           +-- 门禁通过
                    |
                    v
             用户二次确认
                    |
                    +-- 取消 -> 关闭确认流程，不改变事实源
                    |
                    v
             执行既有 Sprint archive
                    |
                    v
             Workflow Sync 刷新投影
                    |
                    v
             需求中心刷新当前迭代、容量和卡片状态
```

## 2. 门禁失败流程

```text
门禁检查
  |
  +-- 存在未归档 Change
  |       -> 显示阻塞 Change 清单或安全摘要
  |       -> 提供跳转到 Change / 关联卡片的入口
  |
  +-- 验收报告未 sign-off
  |       -> 显示验收报告待确认状态
  |       -> 提供跳转到 acceptance-report 的入口
  |
  +-- 当前用户无归档权限
  |       -> 显示无权限摘要
  |       -> 不展示执行按钮
  |
  +-- Workflow Sync 校验失败
          -> 显示同步失败摘要
          -> 提供重试或查看事实源入口
```

## 3. 与父 REQ 差异

| 维度 | REQ-0031 当前迭代容量 | REQ-0037 归档入口 |
|---|---|---|
| 目标 | 显示当前迭代已使用容量与总容量 | 在已有容量上下文中提供归档确认入口 |
| 操作属性 | 信息展示为主 | 高风险治理动作入口 |
| 门禁 | 容量事实源与权限展示 | Sprint archive、验收 sign-off、权限、Workflow Sync |
| 失败态 | 容量待核实、接口失败、刷新失败 | 门禁失败、权限拒绝、归档失败、同步失败 |
| 状态变更 | 不改变 Sprint 生命周期 | 通过既有 archive 流程改变 Sprint 生命周期 |

## 4. 数据与权限边界

- 当前迭代、容量和入口展示基于需求中心既有事实源，不用前端临时卡片或文案猜测。
- 归档执行必须以后端或既有治理命令事实源为准，前端不可信任客户端传入的门禁状态。
- 无权限用户不得通过入口、失败摘要或请求响应推断不可见 Sprint、Change 或验收报告详情。
- 归档成功后必须通过 Workflow Sync 刷新 `sprint.yaml`、`sprint.md`、`acceptance-report.md`、`release-note.md`、Issue trace 和当前态看板投影。
