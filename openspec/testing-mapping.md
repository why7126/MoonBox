---
purpose: 验收项与测试映射
content: REQ/BUG acceptance 与自动化测试的追踪索引
created_at: 2026-07-29 23:10:00
updated_at: '2026-10-26 19:09:24'
owner: MoonBox 产品团队
---

# 测试映射

```yaml
REQ-0000-build-design-system:
  acceptance: [DS-AC-001]
  tests:
    - scripts/validate-design-system.py
    - src/web/src/design-system.test.tsx
REQ-0000-build-api-standard:
  acceptance: [API-AC-001]
  tests:
    - scripts/validate-api-standard.py
    - src/backend/tests/test_health.py
    - tests/integration/api/test_health_contract.py
REQ-0000-build-test-standard:
  acceptance: [TEST-AC-001]
  tests:
    - scripts/validate-test-framework.py
    - tests/unit/test_baseline.py
```

## REQ-0047 治理持久恢复

| 验收范围 | 自动化与证据入口 |
|---|---|
| AC-001/002、AC-KB-001：启动记录、运行能力 | `src/backend/tests/test_review_operation_record.py`、`test_durable_recovery.py` |
| AC-003/006/007/008/009/010/014/015：状态、CAS、预算、停止、权限与保留 | `src/backend/tests/test_durable_recovery.py`、`test_recovery_integration.py`、`recovery_mysql_matrix.py` |
| AC-005：写入/删除/同步中断与原 journal 重放 | `src/backend/tests/test_governance_review.py`、`test_governance_writer.py` |
| AC-011/012/013：API、UI 能力与直接 API 观测 | `src/backend/tests/test_recovery_integration.py`、`src/web/src/recovery-operation.test.tsx`、`src/web/src/chat-workbench.test.tsx` |
| AC-004/016、AC-KB-002/003：真实轮次 | `src/backend/tests/governance_recovery_live_harness.py`、`recovery_fixture_preflight.py`、`src/web/tests/recovery-live.cjs`；当前证据见 Change verification.md，未用合成测试替代 |
| AC-PROTOTYPE-001至004 | Change design.md、用户骨架确认、`evidence/visual/` 与 computed-style.json；模拟 API 边界明确 |

## BUG-0063 同条文兼容追加

| 验收范围 | 验证入口 |
|---|---|
| AC-001—010、013—014、016 | tests/unit/test_compatible_successor.py、test_archive_requirement_scope.py、test_archive_baseline_transition.py；跨入口恢复回归 |
| AC-011—012 | 后端 test_archive_blocker_diagnostics.py、前端 archive-blockers.test.tsx；真实产品证据另见 Change evidence/product |
| AC-015 | Change evidence/product 的 1440/390 截图、computed-style 与部署版本核对；允许路径单独记录 |
| AC-017—018 | Change verification.md、compatibility-contract.md、正式 Sprint 只读预检；显式替代阻断保留 |

## REQ-0050 受控规则替代证明（实施中）

| 验证范围 | 测试与证据入口 |
|---|---|
| 精确差异、义务、未知结构和可信配置 | tests/unit/test_replacement_proof.py、test_replacement_authorization.py |
| 授权事件、审批权限、幂等和领取竞争 | tests/unit/test_replacement_authorization.py、test_replacement_commit.py、tests/integration/api/test_replacement_api.py |
| 首次启用用途隔离、检查点、原操作恢复 | tests/unit/test_replacement_bootstrap.py、test_replacement_bootstrap_commit.py、test_replacement_bootstrap_executor.py |
| 历史逐边核验、旧证明刷新与普通协调器 | tests/unit/test_controlled_successor.py、test_replacement_proof_refresh.py、test_replacement_coordinator.py |
| 签名进程重启、可信工具上下文 | tests/unit/test_replacement_signing_service.py、test_replacement_tool_context.py |
| 审阅/确认/未知结果、草稿与焦点 | src/web/src/components/chat/ReplacementReview.test.tsx、PolicyInstallation.test.tsx、ChatDialog.focus.test.tsx、src/web/src/chat-composer.test.tsx |
| 真实产品、双视口深浅主题、实际重启 | openspec/changes/add-controlled-rule-replacement-proof/evidence/product/；逐项状态以 acceptance-plan.json 与 trace.md 为准，固定合成样本不替代正式全部 AC |

以上为实施测试映射，完整验收和跨入口覆盖尚未完成，不构成归档就绪声明。

## REQ-0050 受控规则替代

| 验收范围 | 自动化与产品证据 |
|---|---|
| AC-001/002/005/007 | test_replacement_proof、test_replacement_proof_refresh、test_replacement_admission |
| AC-003/004/006/015/020 | test_replacement_authorization、test_replacement_api、test_controlled_successor |
| AC-008/009/010/011/012 | test_replacement_coordinator、test_archive_coordinator、test_sprint_archive_coordinator、test_cross_entry_archive_admission；runtime-v7/v8-summary |
| AC-013/014 | test_replacement_bootstrap、test_replacement_bootstrap_commit、test_replacement_bootstrap_executor；隔离真实启用 |
| AC-016/017/019 | ReplacementReview/PolicyInstallation/ChatDialog.focus；真实 UI、权限 403、存储与遥测分离 |
| AC-018 | 通用合成对象、正式 BUG-0063/sprint-012 只读门禁报告 |
| 横切与原型 | evidence/product 截图、样式、真实附件 ready 后拒绝保留；逐 AC 计划记录样本边界 |

逐项执行命令及指纹以 add-controlled-rule-replacement-proof/acceptance-plan.json 为准。

## Chat 回答去重与核验刷新回归
- BUG-0065：src/backend/tests/test_chat_final_answer.py、test_chat_content_store.py、test_chat_assistant_output.py，SQLite/MySQL验证来源幂等、完整版本、历史投影及分页隔离。
- BUG-0066：src/backend/tests/test_direct_completion.py、src/web/src/direct-completion-auto.test.tsx、direct-completion.test.tsx，覆盖队列归属、请求预算、取消与人工版本保护。
- 联合浏览器：src/backend/tests/test_chat_fixes_browser.py（CHAT_BROWSER_TEST=1），真实HTTP/控制器/Chromium，隔离合成数据，不冒充真实模型执行。需CHAT_BROWSER_EVIDENCE指定脱敏证据输出目录；e2e/chat-fixes为测试夹具，不打包生产页面。

## BUG-0067 流式预览

关联 fix-chat-stream-preview-premature-truncation。后端 test_chat_preview.py 覆盖 AC-001/002/003/004/006/007；test_chat_final_answer.py 覆盖 AC-005；前端 full-output.test.tsx、unified-run-status.test.tsx、chat-assistant-output.test.tsx 覆盖范围提示、复制、分页与竞态；AC-008 的隔离浏览器阶段×视口证据见 Change evidence/acceptance/visual。真实 Agent 轮次单独记录，不由合成数据代替。

## BUG-0068 治理核验事务与锁恢复

`fix-chat-database-lock-execution-interruption`映射到test_verification_transaction.py、test_direct_completion.py、test_archive_proof.py、test_completion_handoff.py及test_verification_live.py。AC-001至009的命令、双库、真实执行器与隔离浏览器证据分别归属Change/evidence；原生产部署不因源码验收而更新。
