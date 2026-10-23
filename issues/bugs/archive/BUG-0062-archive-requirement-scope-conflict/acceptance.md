---
bug_id: BUG-0062-archive-requirement-scope-conflict
title: 归档恢复条文冲突判定与迭代关闭验收标准
created_at: '2026-10-21 17:58:42'
updated_at: 2026-10-23 22:43:12
acceptance_status: passed
manual_acceptance_status: passed
---

# 归档恢复条文冲突判定与迭代关闭验收标准

## 验收状态

本BUG已完成源码修复和隔离回归；逐AC证据已采集11项，部署产品AC-010已采集，Agent按证据签认通过。原REQ-0046的36项通过是现场复核，不替代本修复验收。

## 回归验收

### AC-001 同模块不同条文安全承接

- [x] AC-001 连续且唯一的已完成归档链只改同模块其他Requirement时允许承接；原条文与后继最终效果匹配。覆盖当前REQ-0046四条后继现场，不能对ID特判。
- 证据要求：解析与恢复单元测试＋现场只读核验。

### AC-002 真实条文冲突拒绝

- [x] AC-002 同一模块同一Requirement的修改、删除及重命名仍拒绝，返回具体冲突身份；不以原AC通过绕过冲突。
- 证据要求：参数化正反例。

### AC-003 不确定解析安全拒绝

- [x] AC-003 重复标题、未知操作、缺少有效delta、无法可靠解析及未经支持的重命名均拒绝，不按空集合视为无冲突。
- 证据要求：解析负向用例。

### AC-004 归档链完整性保护

- [x] AC-004 断链、身份重复、活动与归档并存、未完成归档、符号链接、交付或delta篡改、未知规格变化继续阻断；合法链到达当前全量哈希并校验最终效果。
- 证据要求：恢复负向矩阵。

### AC-005 验收进度保真

- [x] AC-005 36项证据有效但恢复受阻时保留36/36，并单独呈现恢复阻塞；附件确实损坏时只按真实有效结果计数，不能以历史passed掩盖失败。
- 证据要求：验收聚合及响应契约测试。

### AC-006 诊断原因贯通

- [x] AC-006 保留恢复错误码、相关Change和条文范围；区分附件失效、身份问题、链缺失和范围冲突，不全部转成通用证据无效。诊断不得泄漏凭证或本机路径。
- 证据要求：CLI与产品共享判定及脱敏测试。

### AC-007 Sprint预检与同步一致

- [x] AC-007 相同输入下产品、CLI、Sprint预检与Workflow Sync结论一致；深层失败在目录迁移和状态写入前阻断。若原有命令返回结构不能表达失败，明确修正契约并覆盖调用方。
- 证据要求：隔离Sprint集成测试＋真实现场dry-run。

### AC-008 历史不可变与只读幂等

- [x] AC-008 反复只读判定不改变原manifest、journal、归档交付、Issue终态及首次execution时间；不重复合并规格、迁移或模型调用。
- 证据要求：调用前后哈希比对。

### AC-009 并发变化与缓存失效

- [x] AC-009 证明期间规格、journal、交付或附件变化应拒绝或重做完整只读判定；不得消费过期成功快照。
- 证据要求：可控并发负例。

### AC-010 产品表达与部署一致

- [x] AC-010 若响应/展示受影响，部署产品正确区分已通过AC与恢复阻塞，刷新后保持；实际返回与CLI同源。涉及UI时留1440px截图、selector和computed style，未影响UI则给出代码和契约依据说明N/A。
- 证据要求：部署运行态观察，不以单测冒充。

### AC-011 文档与最终收尾

- [x] AC-011 同步冲突粒度规格、API契约或生成客户端的实际影响说明、治理规则与测试；重新验证REQ-0046和sprint-011，归档操作仍按显式授权，修复ready不等于已关闭迭代。
- 证据要求：聚焦门禁与最终只读预检。

## 观测与边界

product_data_collection_observability: applicable；affected_layers: agent_workflow_governance、归档准入、验收及错误投影、Sprint预检与Workflow Sync。validation：AC-005—010验证进度、诊断、跨入口与只读边界。N/A：当前实现复用既有API字段，内部诊断与共享判定已更新；无DB或客户端生成契约变化，部署产品观察待完成。无新增原始Prompt、客户数据、凭证或主机路径采集。数据库迁移、对象存储、权限扩展及新增模型调用不在本次推荐范围。

## 证据组织

当前Change的acceptance-plan已将AC映射到命令、文件完整性或产品观察，长期脱敏证据置于该Change内。产品视觉证据按实际影响建立阶段与视口矩阵；不复制原始会话，不修改旧清单。每项记录执行版本、命令或观察结果及证据入口。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-23 22:43:12
accepted_by: workflow-sync
source_change: fix-archive-requirement-scope-conflict
source_sprint: sprint-012
evidence: [openspec/archive/2026-10-21-fix-archive-requirement-scope-conflict/evidence/acceptance/20261021190708396912-c279401f/summary.md]
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

## 当前逐项证据

AC-001—009、011：当前Change稳定证据批次20261021190708396912-c279401f通过；AC-010：统一部署后运行代码匹配、36/36、页面与刷新证据通过。源码回归、现场只读、部署观察分别签认。当前源码、只读及部署观察均已通过，人工验收状态已由Agent按证据签认passed，未宣称归档就绪。
