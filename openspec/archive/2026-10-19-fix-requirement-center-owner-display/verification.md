---
title: 需求中心负责人名称修复实施验证与续接记录
created_at: 2026-10-19 10:56:07
updated_at: 2026-10-19 11:18:00
---

# 需求中心负责人名称修复实施验证与续接记录

## 修复与影响面

授权 context 读取层批量解析昵称 → 用户名 → 未知用户；空 owner 显示未分配。owner_key 保持稳定身份，owner_display_name 与兼容 owner 提供安全名称。卡片、title、详情、搜索及筛选共用规则，同名用户按身份键区分。旧响应中的内部标识安全回退。

后端涉及 services/requirement_center.py、schemas/requirement_center.py、governance/reader.py 与 change_index.py；Web 涉及 RequirementCenterPage.tsx、requirementOwner.ts；OpenAPI、生成客户端、API 索引与数据库只读契约已同步。没有修改持久化 owner、DB schema、权限规则、部署或对象存储。本修复不改 CSS；工作区原有卡宽变更保留，相应旧测试期望同步为现有 380px。

## 验证结果

- 后端单元与直接 HTTP：5 项通过。覆盖安全回退、目录空间隔离、批量解析、实际 Capture confirm/writer、首次读取与刷新、未登录 401、无权限 403、查看者可读不可写，注册表身份不变。
- 前端 Vitest：139 项通过。Node 25 需 NODE_OPTIONS=--no-experimental-webstorage，由测试进程继承；根目录运行和只传 node flag 不足。旧测试预期暴露内部 ID 已按新契约修正。
- TypeScript 构建和 Vite 生产构建通过；现有 bundle 大小警告不阻断。名称模块合成断言由验收队列执行。
- 真实产品观察使用当前源码 FastAPI、实际治理 controller 和生产 Web 构建，在本机隔离数据库/项目中进行，没有 mock 浏览器响应。测试入口仅监听回环地址；样本与账号全部合成。
- REQ-0001、BUG-0001 经实际 Capture API 确认和 writer 完成；第一次 context、浏览器显示及刷新名称一致。候选通过 API 审阅，没有宣称 AI 整理过程已验收。
- 同名筛选（1）结合搜索仅保留对应条目，刷新保留选择；详情与卡片名称一致。页面可见文本无内部身份标识，控制台无 error。
- Capture 深浅主题、待研发和验收阶段：1440×900、390×844 截图及 computed style 已采集并目视核对。长名称实际 scrollWidth 356 大于 clientWidth 290/284，ellipsis 与完整 title 生效；390px 延续现有横向看板滚动布局。

## 证据与边界

逐项计划见 acceptance-plan.json；证据见 evidence/acceptance/product-capture.json、owner-interactions.json 和 visual/，机器逐 AC 报告位于同目录运行子文件夹。阶段样本为隔离项目预置的 proposed/applied 文档，不代表实际研发/验收状态迁移。用户原部署仍在登录页，未升级、未声称修复后通过；当前验收针对源码交付的隔离运行态。原反馈视口未知，390px 是补充视口；设计允许明确该缺口，不能冒称原反馈复验。

最早执行器的 Rollup、pytest/AnyIO 与浏览器缺失是历史环境阻塞，当前桌面环境已解除。UI 骨架沿用现有页面，未更改布局，不伪造修改前运行态基线；修复后局部截图和样式为当前验证基线。父 REQ 原型与归档事实不变。无需新增事故知识库条目，根因、实现和证据已在 BUG/Change 完整追溯。

## 数据采集与链路观测

product_data_collection_observability: applicable；affected_layers: [api, web, database_read, openapi_client]。直接 API 授权与身份查询回归通过，OpenAPI/生成客户端已同步；不新增日志、行为事件、Task Trace、请求封装、链路字段、对象存储或保留策略，以上为 N/A。证据仅保存合成名称和脱敏摘要。用量单独通过 AI Usage hook 处理，不以测试次数估算 Token。
