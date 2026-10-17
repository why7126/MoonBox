---
bug_id: BUG-0028-requirement-center-card-owner-raw-user-id
title: 需求中心 Capture 卡片直接显示内部用户标识
status: approved
owner: 产品团队
created_at: 2026-10-07 14:23:41
updated_at: 2026-10-09 23:22:31
discovered_at: 2026-10-05 22:23:03
environment: 本机 MoonBox v0.1.0，Firefox，/requirements；其他部署待验证
lifecycle_stage: plan
related_requirement: REQ-0012-frontend-requirement-center
related_change: null
root_cause_status: confirmed
severity: medium
---

# 需求中心 Capture 卡片直接显示内部用户标识

## 现象

根据 capture.md，用户通过需求中心“新建 Capture”创建卡片后，REQ-0038 的负责人标签显示 `user_` 内部标识并被截断。2026-10-09 本轮已在 Firefox 的本机 MoonBox v0.1.0 `/requirements` 页面刷新并筛选该条目，独立复现同一显示现象；原始身份值未落盘。

## 复现步骤

前置条件：在有权访问的测试项目中登录具备 Capture 创建权限的账号，并确认账号有可读名称。原反馈的环境、版本、角色、浏览器及视口待补证。

1. 进入需求中心，使用“新建 Capture”输入测试需求。
2. 完成候选审阅与确认，等待生成 REQ 卡片。
3. 查看卡片负责人标签，并对照账号可读名称。
4. 刷新页面，检查该标签是否仍直接显示内部标识；记录首次展示与刷新后的差异。
5. 在同一测试环境对 BUG 候选执行相同步骤，核实共用链路的影响范围。

本轮对已有 REQ-0038 执行了页面刷新、筛选和标签观察，未新建业务样本；步骤 1–2 的新建流程及 BUG 候选影响仍待修复验收。

## 期望与实际

| 维度 | 期望 | 实际证据 |
|---|---|---|
| 负责人标签 | 显示可辨识的名称或明确的身份标签 | Firefox 刷新后 REQ-0038 标签显示并截断 `user_` 内部标识；可访问性树保留完整值 |
| 名称缺失 | 使用清晰的回退文案，不以内部标识充当用户名称 | 缺失名称场景尚未实测 |
| 展示一致性 | 卡片、负责人筛选与详情使用一致的身份展示规则 | 代码直接使用 issue.owner；实际页面影响待验证 |

建议后续评审确认昵称、用户名与缺失名称回退的优先级。当前不把建议视为已批准展示契约；身份标识与可读名称应区分，避免修改展示时破坏归属或权限判断。

## 影响范围与严重等级说明

- 已报告范围：需求中心由新建 Capture 生成的 REQ 卡片。
- 潜在范围：同一 Capture 批量生成链路支持 REQ 与 BUG；凡 owner 为内部标识且经过同一展示逻辑的条目均可能受影响。BUG、历史导入及其他来源仍需验证。
- 关联展示：负责人筛选使用 issue.owner，详情也引用该字段，可能有同类可读性问题，尚未作运行态确认。
- 严重度保留 `medium`：已报告影响负责人辨识与协作体验；没有足够证据断言创建、后续操作、权限或数据完整性完全不受影响，也无证据将其定性为越权事件。
- 不与 BUG-0014 的 Capture 持久化或 BUG-0021 的严重度字段展示混同；REQ-0038 仅为原反馈样本。

## 证据与已确认根因

根因状态：`confirmed`。Firefox 在本机需求中心刷新后仍显示 REQ-0038 的 `user_` 内部标识；同条目治理注册表 owner 为内部身份键，后端 `_owner_name` 对该值原样返回，前端 `.rc-owner-tag` 直接渲染 `issue.owner`。因此标签宽度只造成截断，名称解析缺失才是负责人难以辨识的根因。完整脱敏证据链、排除假设和确认范围见 [根因分析](root-cause.md)。

| 编号 | 类型 | 来源 | 证据摘要 |
|---|---|---|---|
| E8 | 浏览器复现 | Firefox，`/requirements`，2026-10-09 23:12（Asia/Shanghai） | 刷新完成后筛选 REQ-0038，卡片仍显示并截断 `user_` 标识；可访问性树呈现完整标签，截图视觉观察一致 |
| E9 | 治理数据 | `issues/requirements/_registry.yaml` 同一 REQ 条目 | owner 为内部身份键、source 为 capture；文档仅保留类型，不保存原始值 |
| E10 | 代码与隔离断言 | `requirement_center.py:210,1406`、`RequirementCenterPage.tsx:3214` | 同一 owner 经 `_owner_name` 原样返回，标签文本和 title 直接取 `issue.owner`，三项断言通过 |

上述证据确认当前本机页面与治理事实源解释的缺陷，不把结论扩大到其他部署、BUG 卡片、详情或筛选。未抓取 Network 响应，也未在本轮重新创建 Capture。

## 自主取证与后续范围验证

前一轮浏览器清单超时和终端连接失败曾被误判为无法访问；随后直接连接已运行的 Firefox 找到页面，本轮又刷新复现，误判已撤回。修复验收时继续核查昵称、用户名、缺失名称、无法解析身份、中文团队 owner、REQ/BUG 卡片、刷新、详情、筛选及权限。Network 字段与其他部署版本可在授权测试环境补充，以确定修复层和影响范围；不作为当前根因确认的阻塞条件。

## 后续修复与验证边界

本轮只完善缺陷治理文档，不实施业务修复。workaround.md 保留尚未验证的人工核对建议；acceptance.md 保留待执行的回归场景。`product_data_collection_observability: not_applicable`，`affected_layers: []`；原因是本轮未变更 API、DB、请求日志、行为事件、Task Trace 或端请求封装。validation：Firefox 已复现，静态同条目链路断言 3/3 通过；修复后的跨层和权限验收待执行。后续若调整 API 身份解析或持久化契约，应重新声明适用层级并同步相应文档与测试。
