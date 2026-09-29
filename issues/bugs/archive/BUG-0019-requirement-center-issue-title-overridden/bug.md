---
bug_id: BUG-0019-requirement-center-issue-title-overridden
title: 需求中心阶段业务标题来源与文档中文标题校验
owner: 产品团队
status: done
created_at: '2026-09-14 11:02:20'
updated_at: 2026-09-29 14:18:37
discovered_at: '2026-09-14 10:25:53'
environment: 部署方式未确认；已完成本仓库只读函数验证
related_requirement: null
related_change: null
related_bug: null
severity: medium
---

# 需求中心阶段业务标题来源与文档中文标题校验

## 现象与复现

关联唯一 Change 时，卡片可能采用追溯文档标题，且 Issue 标题固定读取注册表，未实现按阶段读取主文档/proposal 的来源契约。打开包含两个样本的需求中心，对照卡片、注册表、Issue 主文档及 proposal 标题即可检查。历史用户观察位于验收阶段；不修改真实阶段重放。

| 样本 | 实际标题 | 期望标题 |
|---|---|---|
| BUG-0016-capture | BUG-0016修复追溯 | 需求中心刷新缓慢，MD 文档右侧抽屉加载缓慢或无法加载 |
| REQ-0022-local-project-import-product-iteration | Change 实施与验证记录 | 本地存量项目导入 MoonBox 并支持产品内迭代闭环 |


以上期望适用于 proposal 无有效业务标题且 Issue 主文档业务标题与原业务主题一致的回退场景；有有效 proposal 标题时，开发及后续阶段显示 proposal 标题。

## 阶段标题来源契约

| 阶段 | 首选来源 | 回退 |
|---|---|---|
| 采集池 | _registry.yaml 的 title | 对象 ID |
| 规划中、待评审、已评审、迭代规划 | requirement.md / bug.md 中文业务标题 | 注册表 title，再对象 ID |
| 待开发、研发中、验收中、已完成 | 唯一关联 Change 的 proposal.md 中文业务标题 | Issue 主文档中文业务标题，再注册表 title，再对象 ID |

零个或多个关联 Change 均回退 Issue 主文档，不任意选择 Change。已完成读取关联 Change 对应归档版本，保持现有身份与可见性判定；不存在唯一可判定版本时回退。Change 卡片标题来源不再读取 design.md、trace.md 或其他文档的标题。独立 Change 使用 proposal.md 中文业务标题，缺失回退 Change ID。

中文业务标题以 Frontmatter title 为机器读取事实源，正文一级标题与之保持一致。历史文档缺少 title 时可兼容读取有效中文业务一级标题；空值、纯英文/ID、纯文档类别名视为缺失。历史回退提示资料缺失，不阻断看板读取。前台按选定来源显示，不将阶段显示标题误写回注册表或源文档。Issue 详情保留 Issue 标题，Change 详情显示 Change 标题，并用对象 ID 清晰关联，不能再强制不同业务对象标题相同。

## 文档中文标题生成与校验要求

所有生成的 Markdown 文档都具有非空中文标题；范围包括 capture.md、trace.md、user-stories.md、review.md、requirement.md、bug.md、business-flow.md、acceptance.md、root-cause.md、workaround.md、proposal.md、design.md、tasks.md、spec.md，其他生成文档同样适用。用户输入 proprosal.md 统一按标准文件名 proposal.md 处理。

- 每份文档生成 Frontmatter title 与一致的正文一级标题。业务主文档及 proposal 的 title 表达对象业务目标；辅助文档标题结合业务主题和文档用途，不能只有 ID、slug、Trace、实施与验证记录等类别名称。
- _registry.yaml 是结构化数据，不增加 Markdown 标题；每条记录生成非空中文业务 title。采集时来自采集业务主题，生成或更新 Issue 主文档时同步其业务 title；Change 标题允许描述更细的交付目标，不覆盖 Issue 注册表标题。
- 中文标题可含 MoonBox、API 等专名。字段存在、非空、含中文、非模板/纯类别名、一级标题一致均纳入可自动校验项；业务语义准确性纳入评审，不以含中文一个条件替代。
- capture、generate、complete、review、req/bug-opsx、后续文档生成/重生成入口均在声明生成完成前校验本次产物；错误定位到文件/字段，阻止本次生成完成及状态推进，修正后重验。包括产品内 Agent 生成与 CLI/技能生成路径。
- 生成模板、规则与校验脚本同步落实；支持按当前 Issue/Change 聚焦校验。无关历史残留单独报告，不批量改写历史归档。保留 OpenSpec Requirement、Scenario 等解析关键字，不损坏其语法。

## 影响与严重度

severity 保持 medium：影响业务识别、阶段标题选择及生成资料完整性；没有数据损坏或权限越界证据。范围涉及后端治理文档读取、Web 展示、文档生成模板/技能及校验门禁，不再限定为一行前端修复。不改变阶段判定、权限和业务动作。

## 证据及交付边界

见 root-cause.md、capture.md。已确认旧提取与展示路径不符合来源契约；全体生成入口是否已具备中文标题门禁尚未逐一审计，不能宣称每个入口都有同样缺陷。本轮补齐目标与验收，未修改 src、openspec、全局规则或技能脚本；后续经评审、Sprint、Change 执行。

product_data_collection_observability: not_applicable

affected_layers: web、治理文档读取、文档生成与校验。当前无新增行为事件、日志字段、Task Trace、请求封装、DB 或存储行为；validation：本轮文档一致性与根因门禁，后续实现如改变 API/观测边界则重新评估并同步契约、客户端和测试。
