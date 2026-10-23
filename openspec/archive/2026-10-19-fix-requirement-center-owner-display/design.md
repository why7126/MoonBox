---
title: 需求中心负责人可读名称修复设计
created_at: 2026-10-19 10:28:00
updated_at: 2026-10-19 10:28:00
---

# 需求中心负责人可读名称修复设计

## 背景与现状

Capture 将 actor 稳定键写入 owner；`src/backend/app/services/requirement_center.py` 的 `_owner_name` 只映射固定别名，其余原样返回。Web 卡片、详情及筛选使用 owner。扩大标签宽度不能解决名称缺失。既有评审允许在 Change 中定稿名称字段与回退文案。

## 修复方案

1. 治理 owner 保持原值。context 中保留兼容展示字段 `owner`，新增可选 `owner_key`（稳定筛选键）和 `owner_display_name`（展示名），新客户端优先用显式字段。现有 owner 本来已有团队别名映射，不把它重新定义为认证身份。
2. 空白 owner、null/None 既有空值映射为“未分配”；product 映射“产品团队”，user 保留“用户反馈”。已识别内部身份按可访问用户目录解析：非空昵称 → 非空用户名 → “未知用户”。无法解析、已删除或不在授权范围的身份同样显示“未知用户”。用户名若本身等于内部身份键也视为不可读。既有中文团队和历史可读文本保留。
3. 在已有空间、项目权限校验后收集当前可见条目身份键，通过现有用户目录批量解析；不因全局用户存在就公开其名称。缓存如有使用必须按授权空间/项目隔离，不跨租户复用。禁止逐卡请求造成 N+1 查询。
4. 卡片文本、title、详情和筛选标签共用展示值；筛选 value 使用 owner_key，同名标签使用当前列表内非敏感序号区分，不暴露内部 ID，也不按名称合并。搜索支持可读名称。无新字段的旧服务响应由客户端安全归一化内部标识，不能回显原始键。
5. 新旧响应兼容与所有 owner 消费点在实现时列清单；Mock 仅用于自动化，产品验收以真实 context 响应和浏览器为准。

## 局部界面契约

本次是既有负责人区域局部一致性修复，不增加按钮或弹窗，动作矩阵不适用。参考为当前实现与父 REQ 原型约束；不重做页面骨架。

| 组件 | selector 或定位锚点 | 状态与验收 |
|---|---|---|
| 卡片负责人 | `.rc-owner-tag` | 昵称、回退、长名称；文本和 title 均为可读名称 |
| 详情负责人 | 详情标题中的负责人文本，实施前固化稳定 selector | 与同条卡片一致 |
| 负责人筛选 | owner 筛选控件，实施前固化稳定 selector | 同名、选中、清空、刷新和项目切换 |

实施前采样现有 DOM、字体、颜色、width、max-width、overflow、text-overflow、white-space 与 flex-shrink，建立局部 UI Contract 和基线；沿用已确认骨架，若需结构变更先完成 Skeleton 确认。1440px 和 390px 检查长名称、深浅主题、REQ/BUG 卡片与详情/筛选交互；原反馈视口未知，390px 是补充视口，不能冒称原反馈复验。实施中补齐可获得的原反馈视口，无法取得时明确验收缺口。证据放在当前 Change evidence/acceptance/。

## 测试策略

AC-001/002：昵称优先、仅用户名；AC-003：空白名称、未知/删除/无权身份及空 owner；AC-004：团队与历史文本；AC-005：REQ/BUG 首次 Capture 与刷新；AC-006：同名不同键、详情和筛选一致、搜索组合；AC-007：双视口截图和 computed style；AC-008：不同角色、跨项目不可见用户、未授权直接 API。接口测试同时断言旧字段兼容、授权失败不泄漏名称与批量查询次数，前端测试断言隐藏内部标识且筛选不串人。真实产品观察与合成回归分开记录。

## 数据采集与链路观测

product_data_collection_observability: applicable

affected_layers: [api, web, database_read, openapi_client]

reason: context 响应增加身份展示字段并读取已有用户目录；不新增持久化字段、日志事件、Task Trace、请求封装或链路 ID 规则。

validation: 实施时验证直接 API 授权、OpenAPI/客户端同步、现有 request_id 透传不回退，日志与证据不保存真实姓名、身份键或完整响应。usage_events、Task Trace、对象存储、保留周期 N/A：没有新增行为采集、后台任务、存储或保留策略。修复后直接 API、139 项组件回归及隔离产品观察已通过，详见 verification.md。

## 风险与回滚方案

重点风险是名称查询越权、同名筛选合并、旧响应回退泄露及批量解析性能；按上述授权批量读取和兼容测试阻断。发布按前后端配套交付，失败可回退代码；不改持久化 owner，不需要 DB restore。不得将名称用于认证授权。



## 实施补充与局部参考契约

保真模式为负责人区域局部一致；优先级为已批准名称契约、当前页面结构、父需求原型。组件边界仅卡片负责人、详情副标题与筛选选项，不调整布局、动作或弹窗；现有按钮/modal 不变，动作矩阵 N/A。骨架复用现有页面，不新增页面或状态容器；本轮没有改变 CSS。采样 selector：`.rc-card-tags > .rc-owner-tag`、`.rc-drawer header span`（实施前需浏览器核对）、`[data-testid="requirement-filter-trigger-owner"]`、`[data-testid="requirement-filter-options-owner"]`。批次为后端身份解析、前端名称及筛选、双视口视觉和真实产品验收。

静态样式基线：`.rc-owner-tag` 使用 `--rc-panel-2` 背景、`--rc-muted` 文字；标签继承 nowrap，负责人项 flex-shrink:1、min-width:0、overflow:hidden、text-overflow:ellipsis。以上来自样式源码，不能替代 computed style 或截图。历史执行器未取得修改前运行态基线，不补造历史截图。桌面续接已采集修复后双视口样式与截图，并按既有骨架完成局部目视签认。

实现使用 `ProjectReader` 已授权空间注入 `owner_space_id`；仅在可见卡片集合中去重查询 user_ 身份，SQLite/MySQL 通用参数化 IN，每批 500 条；无授权空间上下文的离线工具使用安全回退。独立 Change 卡片同样保留稳定键。API owner 字段兼容保留展示语义；两新增字段已同步 OpenAPI 和 Orval。

## 修复后交互证据

负责人筛选以 data-testid="requirement-filter-trigger-owner" 定位；详情以条目 capture.md 按钮打开抽屉，检查其头部可读名称。同名筛选、组合搜索、手动刷新和清空已在隔离运行态观察；项目切换由组件测试覆盖。完整记录见 verification.md 与 evidence/acceptance/owner-interactions.json。
