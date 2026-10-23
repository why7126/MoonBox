---
title: 直接命令完成证明与安全恢复追溯记录
created_at: '2026-10-21 11:44:06'
updated_at: 2026-10-21 14:07:28
change_id: fix-direct-command-completion-proof
bug_id: BUG-0060-direct-command-completion-proof-drift
status: applied
iteration: sprint-012
execution:
  schema_version: 1
  started_at: 2026-10-21 11:47:14
  completed_at: 2026-10-21 14:07:28
  last_event: opsx.apply
---

# 直接命令完成证明与安全恢复追溯记录

## 来源与范围

来源 BUG-0060-direct-command-completion-proof-drift，sprint-012，8人天。关联已归档BUG-0052能力及sprint-011的BUG-0055历史样本；不迁移BUG-0055，不实施其排序功能。

## 当前状态

实现、部署和16项验收已通过；REQ/BUG真实收尾、产品与CLI一致性、BUG-0055历史恢复及视觉检查均完成。正式对象未归档，历史逐文件归因缺口保留。

## 观测门禁

product_data_collection_observability: applicable；affected_layers与N/A见design.md；validation: 16项完整验收、真实REQ/BUG产品收尾和CLI对照通过。

## 规划验证记录

OpenSpec strict、6份中文标题、当前Change中文及全仓残留分离、Sprint Scope、上下文预算、目录结构均通过；Workflow Sync bug.opsx errors=0，验收not_started。目录仅有既有legacy SQLite路径警告；未修改运行时数据。任务16项未开始，验收16项未执行。


## 实施与验证记录

2026-10-21 实现相关依赖清单、终态持久交接、原轮次核验接口和 CLI 共用核验器。直接评审/归档继续走既有专用协议。历史清单缺失保留 unknown 归因，只允许当前充分验证后的新签认。

入口前检：产品实际 object-session 与 turns 接口；正式 BUG-0055 为旧 journal（无文件清单）、Sprint scope_estimates 使用 estimated_person_days；CLI 与 API 使用同一 verifier；source 模式检查原工作区身份。已发现并修正估算字段兼容，真实 BUG-0055/0060 投影分别覆盖 50/40 项相关文件。前检不能替代完整发送与终态验证。

稳定回归：SQLite 151 项通过（另 6 个子测试），包含专用评审/归档兼容；独立 MySQL 8.2 87 项通过（另 6 个子测试，证明/交接/保护），数据库回归后变动为纯投影字段与错误展示，无 SQL schema 变动。Web 28 项通过，TypeScript 与构建通过。最终部署与真实轮次观察仍进行中，不声明已完成或 ready。

真实观察：用户本轮授权 REQ/BUG 各一次隔离模型完整样本，未授权正式归档。REQ 实际发送 HTTP 200，但累计用量达到单轮 100 万限额后 stopped（最终计量约115万），没有有效完成证明，不能记通过。BUG 样本已入队观察。BUG-0055 产品核验首次拒绝，发现新投影估算字段不匹配；未释放保护、未重放原业务，修复后待部署复验。

product_data_collection_observability：适用；affected_layers 为 API、私有完成证明存储、交接队列、Chat 展示。沿用 ChatRoute 请求审计与 guard observe，不伪造业务 usage_events，不新增数据库字段；文件证据仅含相关路径及 SHA-256，不存凭证/无关正文。validation 为接口权限/竞态测试、SQLite/MySQL、生成客户端与真实产品核验。


## 中断续接检查点

2026-10-21：稳定版本已部署。标准 Compose 构建后，对最终纯应用代码修正复用已验证依赖层，后端、worker、controller 三个服务源码哈希全部一致，见 evidence/acceptance/implementation/deployment.json。无数据库 schema/权限配置变更。

逐 AC 清单：evidence/acceptance/20261021123611523281-f7365cd8/manifest.json；12 passed、2 failed、2 blocked。一次执行测试命令、11次去重复用；未把诊断清单当成 ready。

- AC-002：REQ 隔离样本 HTTP 200 入队后达到100万Token单轮限额而停止，正式收尾未完成。
- AC-014：BUG 隔离样本对话 completed，但正式 Workflow Sync 退出1，隔离副本缺少 titles.py 固定路径依赖；保护未解除，不能记为成功。
- AC-013/015：最终部署后 Mac 锁屏，原生浏览器工具明确无法解锁。BUG-0055 仍为 needs_review/version14，未重放 bug-opsx、未重复创建 Change。

追加两次模型样本及解锁问题已通过交互卡片提出，尚未收到答复；不新增模型调用。后续隔离夹具已修正标题校验辅助文件、真实 estimated_person_days 字段和 trace 标题，中文标题及正式 sprint.propose dry-run 通过，两个对象真实阶段均为 sprint-planning。新单轮预算计划200万，仅在用户许可后启用。

续接顺序：解锁后从原会话“核验当前成果”恢复并回读卡片和下一动作；保存1440px/窄视口与computed style；获追加授权后串行完成两条隔离发送至收尾，检查CLI一致；按相同输入复用12项有效证据，仅复验缺口与受影响项。全部门禁通过后才 opsx.apply / opsx-accept；当前只做 opsx.progress，不归档。

自动审批拒绝了后端直接 recover 诊断，因为它可能绕开产品入口写状态；已改用只读诊断，正式恢复始终保留产品入口要求。无绕过正确性门禁。

## 授权后续接记录

用户已明确允许 REQ、BUG 各补跑一次隔离样本，单轮200万Token，并确认电脑解锁。原两次失败证据保留。REQ 新样本已由实际发送接口 HTTP 200 入队，等待终态。

BUG-0055 已在产品原轮次点击“核验当前成果”，请求 HTTP 200，界面显示“成果已核验，原执行历史保留”。只读 CLI 同源核验确认 recovered_valid、ready-dev，原28条步骤 SHA-256 与恢复前完全一致；未重放原命令、未重复创建 Change。刷新看板后会话过期，需要重新登录才能核对卡片动作；不把后端阶段替代产品可见验收。窄视口设置工具异常，异常截图不计为通过，待重采。

## 最新验证检查点

2026-10-21：已完成重新登录、最终版本部署及产品复验。BUG-0055 刷新后位于待开发；点击“开始修复”完成实际 object-session 准备，进入原会话且对应命令可发送，随后清空草稿，未发送正式实现命令。原28条 journal 步骤哈希保持不变。当前守卫经外部同步更新后，原轮次仍通过只读历史签认入口显示核验结果；历史读取不授予当前动作权限，POST 继续校验当前操作身份。该边界新增2项后端、1项前端回归；后端52项、前端29项通过。三个部署服务源码哈希及前端入口文件与已测版本一致。

1440×900 与390×900截图、computed style、刷新与卡片证据均已保存。最新逐AC报告为 evidence/acceptance/20261021132733432600-55fc26e0/manifest.json：14 passed、2 failed、0 blocked，2次命令执行、11次去重、1项证据复用。AC-002/014保留真实失败：REQ临时trace缺原型字段，BUG正式同步缺生命周期辅助模块。均未绕过门禁。

已在另一个临时预检副本补齐原型引用和生命周期辅助模块，实际执行正式 req.opsx、bug.opsx 同步均退出0、errors=0，证据见 implementation/req-formal-preflight.txt 与 bug-formal-preflight.txt。用户已追加一次REQ额度；必要 lifecycle.py 的外发及一次BUG收尾调用等待本轮交互确认。原样本运行环境已停止，数据库与失败证据保留；不重发已消费的请求。后续获授权后重启最终版本隔离环境，串行执行已授权REQ及BUG收尾，保留200万Token单轮上限，仅复验AC-002/014和受影响项。当前 tasks 13/16，Workflow Sync opsx.progress errors=0；未执行opsx.apply、正式归档或伪造ready。

## 本次授权续接

用户已允许提供 lifecycle.py 并追加一次 BUG 收尾；REQ 沿用已授权的一次额度。REQ 实际发送 HTTP 200，生成文档后模型错误拼接隔离 sprint.yaml，产生重复 changes 字段和错误缩进，解析在第13行失败；运行权限被撤销，未取得成功同步/完成证明。证据为 implementation/req-additional-failure.json，原副本及数据库保留，不通过改写保护记录修复样本。BUG 采用新的独立运行环境复用已生成文档和有效原始 Sprint 夹具，格式前检通过后发送；不影响正式数据。REQ 额外一次收尾需新增调用授权，已提出，尚未执行。

## 最终验证记录

用户追加授权已逐次承接。BUG与REQ收尾分别使用独立副本，正式同步及最终签认成功，均为completed/validated，产品卡片进入ready-dev，下一动作准备HTTP 200且CLI退出0。原失败记录未覆盖，未清空保护、未重放BUG-0055业务、未归档正式对象。两个样本运行环境均已停止，数据库只作为只读验收数据源保留。

完整报告：evidence/acceptance/20261021140608208403-5a55718c/summary.md；16 passed、0 failed、0 blocked，3次命令执行、11次去重、1项复用。隔离规格合并预演通过，未修改正式specs。最终工作流与归档准入将在收尾后回读。

收尾：Workflow Sync opsx.apply 与 opsx.accept 均 errors=0，Issue acceptance_status=passed；readiness为ready、stale为空。交付证据门禁通过。AI Usage标准hook已执行；最终共享归档准入在所有文档及hook写入后回读。
