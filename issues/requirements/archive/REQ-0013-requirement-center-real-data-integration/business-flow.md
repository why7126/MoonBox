---
requirement_id: REQ-0013-requirement-center-real-data-integration
title: 需求中心真实数据接入
owner: product
source: requirement.md
priority: P1
created_at: 2026-08-10 21:53:16
updated_at: 2026-08-10 21:53:16
---

# 业务流程

## 1. 首屏数据加载流程

```text
用户进入 /requirements
  -> 前端读取本地最近 workspaceId
  -> 请求需求中心 BFF 上下文接口
  -> 后端解析当前用户与可访问空间
  -> 后端读取治理事实源
  -> 后端映射 9 阶段与权限态
  -> 前端渲染统计、筛选、空间和看板
```

关键约束：
- 请求未完成前展示加载态，不展示旧 Mock 数据。
- 本地 workspaceId 无效时，由服务端或前端回退到默认可访问空间。
- 响应字段必须可直接驱动 REQ-0012 页面骨架。

## 2. BFF 聚合流程

```text
GET /api/v1/requirement-center/context
  -> 读取 current_user
  -> 读取 workspaces 与 permissions
  -> 读取 issues/requirements/_registry.yaml
  -> 读取 issues/bugs/_registry.yaml
  -> 按需读取 trace.md / Sprint / OpenSpec Change
  -> 字段白名单映射
  -> 返回 context payload
```

事实源优先级：

```text
Issue trace.md
  > Issue _registry.yaml
  > Sprint 四件套
  > OpenSpec Change 元信息
  > 可推导默认值
```

当事实源冲突时，接口返回对象级 `blocked` 或 `drift` 提示，前端在卡片阻塞区域展示。

## 3. 状态映射流程

```text
Issue status / docs / Sprint / Change
  -> capture
  -> planning
  -> review-ready
  -> approved
  -> sprint-planning
  -> ready-dev
  -> development
  -> acceptance
  -> done
```

映射原则：
- captured / exploring → 采集池或规划中，取决于是否已有 `requirement.md` / `bug.md`。
- draft / enriching / pending_review → 规划中或待评审，取决于文档包是否齐全。
- approved → 已通过。
- 已归档前的 Sprint 纳入阶段且未创建 Change → 迭代规划。
- 已创建 OpenSpec Change 且未 apply → 待开发。
- apply 进行中或任务未完成 → 研发中。
- apply 完成且验收待回填 → 验收中。
- done / archived → 已完成。

## 4. 筛选搜索流程

```text
用户调整类型 / 负责人 / 优先级 / Sprint / 搜索词
  -> 前端基于当前 context 过滤 issues
  -> 重算统计
  -> 9 阶段列保留
  -> 无结果阶段展示 00
```

首版允许前端本地过滤；后续数据量增长后可演进为服务端分页和筛选。

## 5. 空间与权限流程

```text
用户 Hover 切换空间
  -> 展示接口返回的可访问空间
  -> 用户选择空间
  -> 写入本地最近选择
  -> 重新请求 context
  -> 看板和权限入口刷新
```

权限影响：
- `can_access_admin` 控制“进入后台”入口。
- `can_manage_workspace` 控制“设置空间”入口。
- `can_create_workspace` 或等价权限控制“创建或加入空间”入口。
- 只读用户仍可浏览有权限空间下的对象，但高风险动作必须隐藏或禁用并说明原因。

## 6. 异常状态流程

```text
请求中 -> loading
请求失败 -> error + 重试
无空间权限 -> forbidden + 返回默认入口
当前空间无对象 -> empty workspace
筛选无结果 -> empty filtered
事实源解析冲突 -> drift warning
```

错误和漂移状态必须使用安全文案，不展示本地路径、堆栈或原始文件内容。

## 7. 与父需求差异

REQ-0012 负责前台需求中心页面骨架、交互、视觉和 Mock 数据下的 9 阶段看板体验。REQ-0013 不重做页面骨架，而是在父需求基础上补齐真实数据接入、BFF 聚合、权限态、加载态、错误态和安全脱敏边界。
