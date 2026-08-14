# 空间管理原型上下文工程

## 1. 设计基线

- 画布：桌面端 1440×900，内容区域随侧边栏伸缩。
- 延续 MoonBox 平台运营后台：深色侧边栏、浅色内容区、蓝色主操作、8px 间距基准、6/8/12px 圆角。
- 字体：Inter / PingFang SC / Microsoft YaHei；正文 14px，辅助 12px，页标题 24px。
- 语义色：主色 `#4f6ef7`，成功 `#16a66a`，警告 `#d88916`，危险 `#dc4c64`，正文 `#202637`，弱文字 `#6f7787`，边框 `#e4e8f0`。
- 签名元素：空间状态与用量进度条共同表达“生命周期 + 资源健康度”。

## 2. 页面与 DOM

| 页面 | DOM 标识 | 核心组件 |
|---|---|---|
| 空间列表 | `#page-spaces` | `stats-grid`、全宽 `filterbar`、`data-table`、状态化查看/编辑操作 |
| 申请审批 | `#page-approvals` | 页签角标、申请表格、审批弹窗 |
| 回收站 | `#page-recycle` | 剩余天数、恢复/永久删除操作 |
| 空间详情 | `#page-detail` | 含负责人的详情头、分区页签、信息卡、配额进度、审计时间线 |

## 3. 弹窗

| 弹窗 | `data-modal` | 触发点 |
|---|---|---|
| 创建空间 | `create` | 页面主按钮 |
| 编辑空间 | `edit` | 正常空间列表行“编辑” |
| 审批申请 | `approve` | 申请行“审批” |
| 冻结空间 | `freeze` | 正常空间主操作 |
| 恢复空间 | `restore` | 冻结空间或回收站 |
| 配额调整 | `quota` | 详情页配额卡“调整” |
| 续期 | `renew` | 详情页更多操作 |
| 移交负责人 | `transfer` | 详情页顶部负责人信息“变更” |
| 删除空间 | `delete` | 详情页/列表更多操作 |
| 永久删除 | `purge` | 回收站超级管理员操作 |

## 4. 数据模型

### Space

`id, name, code, description, ownerId, status, source, memberCount, memberQuota, storageUsedGb, storageQuotaGb, aiUsedTokens, aiQuotaTokens, productId, expiresAt, createdAt, updatedAt, protected`

状态枚举：`ACTIVE | FROZEN | RECYCLE`。冻结原因另存 `freezeReason`；回收态包含 `deletedAt, deletedBy, deleteReason, purgeAt`。

### ProductBinding

`productId, spaceId, productName, immutableBinding=true`。产品名称由空间名称变更事件同步更新。

### SpaceApplication

`id, applicantId, name, purpose, proposedOwnerId, expectedMembers, requestedStorageGb, requestedAiTokens, status, submittedAt, decisionBy, decisionAt, decisionReason`

### AuditLog

`id, spaceId, action, operatorId, source, before, after, reason, result, createdAt, immutableRiskLog`

## 5. 接口预期

| 方法 | 路径 | 用途 |
|---|---|---|
| GET | `/admin/spaces` | 搜索、筛选、分页查询空间 |
| POST | `/admin/spaces` | 原子创建空间与同名产品 |
| GET | `/admin/spaces/{id}` | 获取详情与权限动作集 |
| PATCH | `/admin/spaces/{id}` | 修改基础信息并同步产品名 |
| POST | `/admin/spaces/{id}/freeze` | 冻结空间 |
| POST | `/admin/spaces/{id}/restore` | 恢复冻结或回收空间 |
| POST | `/admin/spaces/{id}/renew` | 续期 |
| POST | `/admin/spaces/{id}/transfer-owner` | 移交负责人 |
| PATCH | `/admin/spaces/{id}/quota` | 调整三类配额 |
| DELETE | `/admin/spaces/{id}` | 进入 30 天回收期 |
| DELETE | `/admin/spaces/{id}/purge` | 超级管理员永久删除 |
| GET/POST | `/admin/space-applications` | 查询/创建申请 |
| POST | `/admin/space-applications/{id}/approve` | 核定并通过 |
| POST | `/admin/space-applications/{id}/reject` | 拒绝并记录原因 |
| GET | `/admin/spaces/{id}/audit-logs` | 查询不可变操作记录 |

所有高风险接口要求后端二次鉴权、幂等键和审计写入；状态约束以后端返回的 `allowedActions` 为准。

## 6. 原型交互映射

- `.nav-item[data-page]` 和 `.tab[data-page]` 切换模块页面。
- `.detail-link` 打开详情；`.detail-tab` 切换详情分区。
- `[data-open]` 打开指定弹窗；`[data-close]` 关闭。
- `.filters .input` 使用 `flex: 1` 填满筛选栏剩余空间，筛选下拉框不改变宽度。
- 表单提交在原型中用 Toast 模拟成功，并同步可见状态；生产实现需调用接口后再更新。
- `#userMenuTrigger` 展开侧边栏用户菜单；菜单内 `#theme` 切换 `body.light`，并通过 `#themeValue` 显示当前主题。
# v1.0.1 上下文增量

## Design System

- Reference: `MoonBox-Platform-Operations-v1.0.5`
- Default theme: dark; primary `#CBA35C`; background `#0A0C1B`; panel `#12142B`; sidebar `#0E1023`.
- Component radius: 2px; sidebar width: 224px; right content area has no top navigation container.
- Light theme follows the same reference variables and is switched by the theme control.

# v1.0.4 上下文增量

- `.main` 内直接挂载 `.content`，不再渲染空的 `.top` 节点。
- `.content` 的既有 padding 保持不变，作为右侧内容区顶部留白的唯一来源。

## Expiry model

```ts
type ExpiryType = 'fixed_date' | 'long_term'
interface WorkspaceExpiry {
  type: ExpiryType
  endDate: string | null // fixed_date 必填；long_term 必须为 null
}
```

`create`、`approve`、`renew` 三个弹窗复用 `.date-type` 组件。选择 `long_term` 后隐藏日期输入并取消 required；列表使用 `.expiry-long` 显示“长期有效”。

# v1.0.2 上下文增量

- `edit` 弹窗复用 `.date-type` 有效期组件；允许编辑 `name / description / expiry`，禁止编辑 `code / ownerId / quota`。
- 列表行操作根据 `allowedActions` 渲染：正常空间包含 `VIEW / EDIT / FREEZE`，冻结空间包含 `VIEW / RESTORE`，回收中空间不包含 `EDIT`。
- 详情顶部使用 `.detail-owner` 承载负责人摘要和移交入口，原独立负责人卡片已移除。
- 详情概览 `.detail-grid` 内包含三个同级独立卡片：基础信息、最近操作、配额与用量；在双列自动布局中，基础信息位于左上，配额与用量位于左下。

# v1.0.5 上下文增量

- 修正“最近操作”卡片的 DOM 闭合边界，确保“配额与用量”不再嵌套其中。
- 基础信息与配额用量均保持独立 `.card` 节点、`.card-title` 标题及各自操作入口。

## req-complete 原型拆解

### 页面清单

| 页面 | 入口 | 验收重点 |
|---|---|---|
| 空间列表 | `#page-spaces` | 统计卡、筛选栏、数据表格、分页、状态化行内操作 |
| 申请审批 | `#page-approvals` | 待办角标、申请列表、审批弹窗、通过/拒绝分支 |
| 回收站 | `#page-recycle` | 删除信息、剩余天数、恢复、永久删除 |
| 空间详情 | `#detail-page` / 详情链接 | 详情头、负责人摘要、详情 Tab、基础信息、最近操作、配额与用量、审计时间线 |

### 关键区域

- 左侧侧边栏：`OPERATIONS / 空间管理` active，底部用户菜单承载主题切换。
- 右侧内容区：不设置顶部导航栏，页面内容从 `.content` 顶部开始。
- 筛选栏：搜索框弹性占满剩余宽度，筛选控件保持稳定宽度。
- 详情概览：基础信息位于左上，配额与用量位于左下，最近操作位于右侧。
- 弹窗层：创建、编辑、审批、冻结、恢复、配额调整、续期、负责人移交、删除、永久删除均使用设计系统弹窗。

### 组件层级

```text
.app
  .sidebar
    .nav.active
    .user-wrap
      .user-menu
  .main
    .content
      #list-shell
        .head
        .tabs
        #page-spaces / #page-approvals / #page-recycle
      #detail-page
        .detail-head
        .detail-tabs
        .detail-grid
  .modal-mask[data-modal]
  .toast
```

### 状态矩阵

| 对象 | 状态 | UI 表现 | 可用操作 |
|---|---|---|---|
| Space | ACTIVE | 正常状态标签 | 查看、编辑、冻结、更多 |
| Space | FROZEN | 蓝灰冻结标签、只读说明 | 查看、恢复、更多，必要配置由平台管理员处理 |
| Space | RECYCLE | 回收中状态与剩余天数 | 查看、恢复；永久删除仅超级管理员 |
| Quota | normal | 常规进度条 | 正常使用 |
| Quota | warning | 黄色预警 | 通知负责人，可调整配额 |
| Quota | exceeded | 红色超限 | 禁止新增或继续消耗对应资源 |
| Expiry | fixed_date | 展示结束日期 | 到期提醒、到期自动冻结 |
| Expiry | long_term | 展示“长期有效” | 不触发到期提醒或到期自动冻结 |

### 交互触发

- `.tab[data-page]` 切换空间列表、申请审批、回收站。
- `.detail-link` 从列表或审批结果进入空间详情。
- `.detail-tab` 切换概览、成员、产品、配额与用量、操作记录。
- `[data-open]` 打开指定弹窗；`[data-close]` 关闭弹窗。
- `#userMenuTrigger` 展开用户菜单；`#theme` 在深浅主题间切换。

### 数据依赖

- `GET /admin/spaces` 驱动列表、搜索、筛选、分页和状态化操作。
- `POST /admin/spaces` 原子创建空间与同名产品。
- `GET /admin/spaces/{id}` 驱动详情、权限动作集、状态提示和产品绑定信息。
- `PATCH /admin/spaces/{id}` 更新名称、简介和有效期并同步产品名。
- 高风险动作接口驱动冻结、恢复、续期、负责人移交、配额调整、删除和永久删除。
- `GET /admin/spaces/{id}/audit-logs` 驱动操作记录。

### 响应式断点

- 1440px 桌面视口为主验收视口，必须完整展示侧边栏、筛选栏、表格和详情双列布局。
- 1280px 及以上不得破版；表格列较多时操作列必须保持易访问。
- 低视口高度下弹窗 body 必须滚动，底部操作按钮始终可访问。

### 1440px 验收焦点

- 右侧内容区顶部无空白导航容器。
- 筛选栏占满整行，搜索框弹性宽度正确。
- 空间详情概览中基础信息、配额与用量、最近操作互不嵌套且阅读顺序稳定。
- 用户菜单中的主题切换入口可用，顶部不出现独立主题按钮。
- fixed toast 不挤压页面布局。
