---
title: 需求中心阶段业务标题与中文文档生成修复设计
created_at: '2026-09-15 23:04:19'
updated_at: '2026-09-15 23:04:19'
---

# 需求中心阶段业务标题与中文文档生成修复设计

## 背景与现状

根因 confirmed，六条证据见来源 BUG root-cause.md。中文黑名单不能替代来源限制；前端统一 current_change.title 优先不能表达阶段契约。旧方案“所有阶段统一 Issue 标题”已失效。

## 修复方案

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

## 接口与实现边界

在后端治理读取层集中解析标题，复用授权快照与唯一版本解析，不额外读取未授权文件。保留 issue.title 的 Issue 语义，新增可选 display_title、title_source、title_warning 展示投影，前端优先消费 display_title；旧接口无字段时使用 issue.title，禁止恢复 trace/design 标题覆盖。title_source 仅返回受控相对来源或枚举，不暴露本机路径。Issue 抽屉仍展示 Issue 标题，Change 详情展示 proposal 标题。

共享标题解析/校验规则由后端生成路径与治理 CLI 复用或以契约测试保证等价。先盘点 capture/generate/complete/review/opsx 等技能模板及产品 Agent 实际产物入口，生成结果在正式应用/完成之前验证；失败不得持久化部分成果或推进状态，使用既有失败恢复边界，不新增平行写入机制。规则变更通过治理日志记录，避免仅靠 prompt 要求。

## 测试策略与 UI Contract

保持现有页面壳、.rc-card-title、文档入口及动作结构，只调整标题文本来源与必要缺失提示。数据为真实授权 API；九阶段边界使用受控合成数据，1440px 真实页面观察独立记录。无新增 modal 或原型重构。检查文本、点击目标、长标题布局、font-size、line-height、white-space、overflow；不以合成测试替代真实观察。

按来源 BUG AC-001 至 AC-013：后端阶段/回退/权限单测，前端 DOM 和详情身份测试，全部文档类型正反样本及生成入口失败不写入/不推进状态测试，OpenAPI/客户端生成一致性，聚焦文档标题与 OpenSpec 语法校验。

## 产品数据采集与链路观测

product_data_collection_observability: applicable

affected_layers: API响应、Web消费、request_logs。

reason：新增可选显示字段，复用既有请求日志与鉴权。usage_events、task_traces、task_trace_spans 不新增事件或节点，生成结果校验沿用原链路，DB和对象存储结构不变。

validation：验证请求链路ID/既有日志不回归、响应无敏感路径、直接API与前端投影一致、OpenAPI/Orval同步；文档内容不新增写入日志。若实际生成入口需新节点，在实施前补映射与测试。

## 风险与回滚方案

纯类别名判断需自动规则与业务评审结合；历史缺失只提示并回退，不批量重写归档。并行活动 Change 可能编辑相同前端或生成路径，实施前复核最新代码并保持其功能。容量缓冲仅7人天，范围增长重新估算。回滚代码及生成规则，不删除合法标题资料。
