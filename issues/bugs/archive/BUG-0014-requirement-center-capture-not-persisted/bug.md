---
bug_id: BUG-0014-requirement-center-capture-not-persisted
title: 需求中心新建 Capture 仅创建前端临时卡片，未持久化 REQ/BUG 目录、文档、注册表与索引
status: done
owner: null
discovered_at: 2026-09-11 18:51:46
created_at: 2026-09-11 18:55:53
updated_at: 2026-09-14 08:50:10
environment: null
related_requirement: REQ-0012-frontend-requirement-center
related_change: fix-requirement-center-capture-persistence
iteration: sprint-005
source: capture.md
product_data_collection_observability:
  status: applicable
  affected_layers: [web, api, request_logs]
  reason: 后续修复需要让 Capture 表单调用持久化 API，并保留请求结果与关联标识；本次仅完善缺陷文档，不改变运行时采集行为。
  validation: 已复核提交函数无 API 调用；真实请求链路与修复后的成功、失败观测尚待验证。
severity: high
---

# 需求中心新建 Capture 未持久化

## 现象

在需求中心新建 Capture，提交后界面显示新卡片并提示“Capture 已创建并插入采集池”，但未创建对应 REQ/BUG 目录、`capture.md`、`trace.md`，也未更新注册表与当前态索引。REQ 与 BUG 共用此提交路径，按一条缺陷处理。

来源为用户反馈及本会话 `/bug-explore` 的代码分析与隔离执行。实际部署环境、镜像或提交版本尚未提供；以下代码结论针对当前工作区，不代表已完成生产复现。

## 复现步骤

### 页面复现路径（待真实环境验证）

1. 使用有目标项目写权限的账号进入需求中心，选择目标项目。
2. 点击“新建 Capture”，选择“需求”，填写无敏感信息的测试标题和描述，提交。
3. 观察新卡片及成功提示，同时在 Network 中检查是否发生创建请求。
4. 核对目标项目 `issues/requirements/plan/` 下目录与文档、`issues/requirements/_registry.yaml` 和 `issues/requirements/CHANGELOG.md`。
5. 完整刷新页面或重新进入需求中心，核对该条目是否从事实源重新加载。
6. 选择“Bug”重复上述步骤，核对 `issues/bugs/` 对应文件。

### 已执行的隔离验证

从当前 `RequirementCenterPage.tsx` 提取实际 `submitCapture` 函数，通过项目 TypeScript 转译后在 Node VM 中执行；注入空 Issue 列表、合成标题与描述、React setter 替身，并监测 `fetch` 与 `governanceRequest` 调用。未修改业务代码或创建测试业务数据。

| 输入类型 | 生成临时编号 | 内存卡片数 | 网络调用数 | 描述保留 | 提示 |
|---|---|---|---|---|---|
| requirement | REQ-0001 | 1 | 0 | 否 | Capture 已创建并插入采集池 |
| bug | BUG-0001 | 1 | 0 | 否 | Capture 已创建并插入采集池 |

两种类型均执行完成且断言通过。这是提交函数的合成验证，未覆盖真实浏览器、鉴权、后端部署与文件系统端到端验收。

## 期望与实际

| 维度 | 期望 | 实际或证据边界 |
|---|---|---|
| 创建成功 | 后端完成持久化后返回成功并展示卡片 | 仅调用 `setContext` 插入内存对象，直接提示成功 |
| 编号 | 服务端按目标注册表分配正式、唯一的完整 ID | 前端按已加载卡片最大编号加一，仅产生短 ID |
| 文档与索引 | 创建 plan 目录、capture、trace 并同步注册表与 CHANGELOG | 提交函数未发起持久化请求，仅声明文档名与 available 状态 |
| 表单内容 | 描述等有效字段被保存 | 描述未写入新卡片，随后表单重置 |
| 重新加载 | 条目可由后端事实源恢复 | 后端读取注册表，前端初始加载替换上下文；未落盘条目无法由此恢复，实际刷新结果待观察 |

## 证据摘要

| ID | 类型 | 来源 | 支持的判断 |
|---|---|---|---|
| E1 | code_path | `src/web/src/pages/catalog/RequirementCenterPage.tsx`，`submitCapture`，2022–2063 行 | 当前提交路径只有内存更新，无持久化调用；描述被遗漏 |
| E2 | reproduction | 本会话 `/bug-explore` 的实际函数提取与 Node VM 隔离执行摘要，见上表 | REQ/BUG 两种输入均产生成功提示，网络调用为 0 |
| E3 | code_path | `src/backend/app/services/requirement_center.py`，`_load_issues`；`RequirementCenterPage.tsx`，`loadContext` | 注册表是看板读取事实源，初始加载不恢复前端临时对象 |
| E4 | code_path | `src/web/src/requirement-center.test.tsx`，`creates a capture card from the reference-style modal` | 既有测试只断言界面卡片和提示，未断言落盘、描述保存或刷新恢复 |
| E5 | code_path | 探索时 `git show HEAD:src/web/src/pages/catalog/RequirementCenterPage.tsx` | HEAD 已有相同提交逻辑，非当前未提交改动新引入；首次引入边界未完成审计 |

代码层原因已确认：新建入口停留在前端状态模拟，未接入服务端持久化闭环。此结论不等于确认实际部署版本、生产影响数量或所有运行环境的表现；正式根因文档与修复评审由后续完善阶段承接。

## 影响范围

- 需求中心 REQ 与 BUG 的新建 Capture 共用路径均受影响。
- 卡片、文档标识与磁盘事实源不一致，后续文档查看、生成、评审和治理追溯缺少可靠条目。
- 表单描述被清空且未保留，存在用户输入丢失。
- 按客户端列表分配编号存在多窗口、并发或列表不完整时的冲突风险，尚未执行并发复现。
- 相关需求候选为 `REQ-0012-frontend-requirement-center`；其主文档“采集池”要求存在 capture 与 trace。`REQ-0013-requirement-center-real-data-integration` 提供注册表读取背景。本次完善依据阶段模型正式关联 REQ-0012。

## 严重等级说明

暂定 high / P1：核心采集操作显示成功却未保存治理记录，且丢弃描述，直接影响后续需求和缺陷流转。当前没有生产大面积故障或 P0 紧急证据，建议按常规 fix 流程处理。

## 后续验证范围

- 分别验证 REQ/BUG 完整目录、文档、注册表与索引的一致性，以及完整 ID 和描述保留。
- 创建成功后重新加载，记录仍存在且文档可读取。
- 检验并发编号、重复提交、持久化部分失败时的一致性与错误反馈，不能出现虚假成功或静默丢失输入。
- 核对项目隔离与写权限；未授权请求不能修改文件。
- API、OpenAPI、客户端生成与请求观测随修复同步；DB 是否调整由修复设计确认，不预设新增业务表。
- 观测依据 `docs/standards/product-data-collection-observability.md`：本次未改变 DB、对象存储、Task Trace 或行为事件实现；后续是否使用异步任务及对应采集层级由 Change 设计确定。

## 日志与截图

尚无实际部署截图或请求日志。现有证据为代码定位及脱敏合成验证摘要；尚未形成实际环境验收结论。
