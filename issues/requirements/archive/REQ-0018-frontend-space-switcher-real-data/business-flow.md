---
requirement_id: REQ-0018-frontend-space-switcher-real-data
title: 前台空间切换列表真实数据接入
owner: product
source: requirement.md
created_at: 2026-08-15 10:45:44
updated_at: 2026-08-15 10:45:44
---

# 业务流程

## 1. 总体链路

```text
用户登录前台
  |
  v
读取前台会话 token
  |
  v
请求需求中心上下文 / 前台空间上下文接口
  |
  v
后端按当前用户解析后台空间成员关系
  |
  +-- 已加入 ACTIVE/FROZEN 空间 -> 映射为前台 Workspace
  |
  +-- RECYCLE / 未加入 / 无权限空间 -> 不返回
  |
  v
前端校验 localStorage 最近选择
  |
  +-- 有效 -> 使用最近选择
  |
  +-- 无效 -> 回退默认可访问空间
  |
  v
用户菜单和空间切换浮层展示真实空间
```

## 2. 空间切换流程

```text
用户打开用户菜单中的“切换空间”
  |
  v
打开右侧轻量二级浮层
  |
  v
展示已加入空间列表
  |
  +-- ACTIVE: 正常展示，可切换
  |
  +-- FROZEN: 展示只读标记，可切换查看
  |
  +-- 无空间: 展示空态和“创建或加入空间”入口
  |
  v
用户点击空间项
  |
  v
更新当前空间 state + 最近选择
  |
  v
关闭浮层并提示切换成功
  |
  v
刷新或重算当前空间范围内的统计、筛选和看板数据
```

## 3. 最近选择失效回退

```text
读取 localStorage.moonbox.workspace
  |
  v
与接口返回 workspaces[] 对比
  |
  +-- 命中且可访问 -> 作为当前空间
  |
  +-- 未命中 / RECYCLE / 被移出 / 权限不足
       |
       v
     清理或覆盖本地缓存
       |
       +-- 有默认空间 -> 切到默认空间
       |
       +-- 无默认空间 -> 展示无已加入空间空态
```

## 4. 与关联需求差异

| 关联需求 | 职责 | 与本需求边界 |
|---|---|---|
| REQ-0012-frontend-requirement-center | 前台需求中心、用户菜单、空间切换 UI 骨架 | 本需求复用 UI 骨架，不重做 9 阶段看板 |
| REQ-0013-requirement-center-real-data-integration | 需求中心治理对象真实数据聚合 | 本需求补齐 `workspaces` 的真实后台空间事实源 |
| REQ-0017-admin-space-management | 后台空间生命周期、成员、产品和状态治理 | 本需求只读复用后台空间数据，不新增后台管理操作 |
| REQ-0019-space-creation-join-application-flow | 前台创建或加入空间申请流程 | 本需求保留入口但不实现流程 |

## 5. 数据与权限边界

- 前台空间上下文的数据源是后台空间、成员和产品绑定事实源。
- 普通前台用户只能看到自己已加入空间的切换字段。
- 后台配额、审计、删除原因、负责人内部 ID 和高风险 allowed actions 不进入前台切换响应。
- 冻结空间的只读限制必须由服务端能力校验兜底。
