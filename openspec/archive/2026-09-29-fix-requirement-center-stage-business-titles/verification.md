---
title: 需求中心阶段业务标题修复验证记录
created_at: "2026-09-15 23:33:05"
updated_at: "2026-09-15 23:33:05"
---

# 需求中心阶段业务标题修复验证记录

## 实现与范围

BUG-0019，sprint-007，Change fix-requirement-center-stage-business-titles。共享 titles.py 解析与校验；change_index.py 在完成阶段判定及权限过滤后生成 display_title、title_source、title_warning。Issue title 保持主文档业务身份，独立 Change 仅从 proposal 取标题。注册表同步使用 Issue 标题并保留引号与反斜杠。

采集池取注册表；规划中、待评审、已评审、迭代规划取主文档；待开发、研发中、验收中、已完成取唯一 proposal，失败回退主文档、注册表、ID。历史仅缺失 title 时读取有效 H1；显式无效 title 不借 H1 掩盖。trace/design 不作为提案标题来源。缺失及归档歧义返回受控中文提示。

## 合成回归

- 后端最终集合：test_document_titles、test_change_visibility、test_governance_candidates、test_governance_capture、test_capture_drafts、test_document_title_gate、test_workflow_sync_patch、test_workflow_sync_engine。覆盖九阶段 × REQ/BUG、有效提案与 Issue 不同、零/一/多关联、权限、归档版本歧义、trace/design 排除、14类文档正反例、候选原子应用边界和状态写入前拒绝。最终162项通过（6.09秒）。
- 前端：`cd src/web && ./node_modules/.bin/vitest run src/requirement-center.test.tsx`，106项通过；`./node_modules/.bin/tsc -b` 通过。覆盖九阶段消费服务端展示字段、旧接口回退、Issue详情身份及现有文档交互。
- OpenAPI导出完成，Orval三个配置生成成功，Vite生产构建通过。默认生成包装脚本的 pnpm 缓存入口缺失，改用已安装的 Orval 可执行文件完成相同配置生成。
- OpenSpec strict校验通过，Requirement/Scenario解析关键字保留。Sprint Scope通过；中文标题聚焦BUG、Change及两份注册表通过。最终文档落盘后再次校验。

## 真实页面观察

使用 Python Playwright + Chromium，1440 × 1000。独立临时数据库与治理目录，实际后端鉴权/API及构建后的Web页面，无网络Mock；数据是按用户两个异常样本构造的隔离测试资料，未修改用户历史Issue或生产数据。本次不是生产环境验收。

- REQ-0022：本地存量项目导入 MoonBox 并支持产品内迭代闭环。
- BUG-0016：需求中心刷新缓慢，MD 文档右侧抽屉加载缓慢或无法加载。
- 两份proposal无有效标题且trace含错误标题，实际卡片正确回退主文档；有效且不同proposal切换由后端与DOM合成回归覆盖。
- `.rc-card-title`：font-size 13.5px，line-height 20.25px，white-space normal，overflow visible，宽264px；截图核查两行长标题无截断、无溢出，标签和文档入口仍清晰。
- 点击两卡片实际新开页路径分别保留 REQ-0022-title-probe 与 BUG-0016-title-probe 身份，未跳至Change。该观察验证导航目标；不冒充详情页完整功能验收。
- 证据：[1440px截图](evidence/titles-1440.png)、[文本与样式](evidence/titles-observed.json)、[点击身份](evidence/titles-interactions.json)。

## 生成入口矩阵

| 入口 | 产物及规范 | 执行门禁 |
|---|---|---|
| req/bug-capture | capture、trace、注册表；新建索引也有中文title/H1 | 技能标题契约、Capture请求校验、plan正式写入前校验、Workflow Sync标题门禁 |
| req/bug-generate | requirement/bug、trace；主标题同步注册表 | 技能契约、聚焦脚本、状态投影前校验与注册表同步 |
| req/bug-complete | user-stories、business-flow、acceptance、root-cause、workaround及既有主文档/trace | 技能契约、当前Issue所有Markdown标题校验 |
| req/bug-review | review、trace | 技能契约、评审完成同步前校验 |
| req/bug-opsx | proposal、design、tasks、spec、trace | 技能契约、当前Change递归校验、必需主产物缺失拒绝 |
| opsx-propose / openspec-propose | proposal、design、tasks、spec等 | 两份技能中文契约、聚焦标题脚本；遵循语言规则后完成 |
| 产品Agent req-generate | requirement、trace、注册表、索引 | 隔离工作区复制标题门禁依赖，candidate应用前共享校验，title同步与变更边界验证；非法结果拒绝且不写来源文件 |
| 其他文档生成/重生成 | 所有Markdown适用 | rules/language.md统一要求，明确本次路径聚焦校验后才声明完成 |

辅助文档需业务主题加用途；不能仅用类别名。产品现有正式生成入口按实际能力覆盖，未新增未授权工作流能力。CLI技能生成的无效草稿可能保留用于修正，但不能推进完成状态；产品候选正式应用前拒绝整批，不部分写入。未批量改写历史归档，业务语义准确性仍由评审判定。

## 验收对应

AC-001/002/003：阶段矩阵；AC-004/005/007：Change索引、回退与归档歧义；AC-006：两个真实页面样本加不同proposal的合成回归；AC-008：多关联测试、DOM与真实点击身份；AC-009/011：14类文档及无效标题正反例；AC-010：候选标题同步、注册表反斜杠回归；AC-012：候选失败来源不变、SyncEngine写入前阻断、聚焦校验和OpenSpec解析；AC-013：独立真实页面证据。

## 产品数据采集与链路观测

product_data_collection_observability: applicable

affected_layers: API响应、Web消费、request_logs。

validation：既有HTTP鉴权、跨对象隔离、文档读取审计和请求失败回归通过；来源字段为受控文件名或id，不返回文件系统路径。OpenAPI/Orval已同步。未改变请求封装、request_id等字段；不新增日志正文采集。DB、usage_events、Task Trace节点、对象存储、部署和安全策略无结构变化，无数据库迁移或部署配置变更。

## 连续执行与自修记录

工作流旧夹具未创建标题文档导致5项失败，补齐隔离真实文档后13项工作流测试通过，未绕过门禁。新增归档歧义投影回归发现warning遗漏，在当前apply补齐后复验。测试路径和Sprint Scope参数错误已纠正并执行；这些错误未推进完成状态。上下文压缩后直接续做待办。未观察用户停止、平台停止或全部任务依赖外部输入情形，不伪造这些场景证据。

## 完成同步

opsx.progress及opsx.apply成功，Errors=0；Change execution schema v1保留首次started_at并记录completed_at，BUG trace关联状态applied，当前态索引下一步保留完整BUG身份。评审文档status=approved为评审结论，Workflow Sync的语义提示已人工复核，未改写为Issue状态。AI Usage Hook已自动发现尝试，usage_mode=unavailable，command_run_count=0，原因无可归因命令用量；不影响交付，未虚构用量。

全仓diff空白检查发现无关正式规格issue-classification-metadata末尾空行，本轮未修改；本次范围检查单独执行。
