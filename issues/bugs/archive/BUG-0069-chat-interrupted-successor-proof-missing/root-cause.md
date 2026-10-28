---
bug_id: BUG-0069-chat-interrupted-successor-proof-missing
created_at: '2026-10-27 16:38:20'
updated_at: '2026-10-27 16:38:20'
title: Chat 中断缺少旧同步证明导致外部接续完成后仍受限根因分析
status: confirmed
historical_attribution_status: partial
---

# Chat 中断缺少旧同步证明导致外部接续完成后仍受限根因分析

复用来源：[BUG-0061的2026-10-27复发材料](../../archive/BUG-0061-cross-entry-continuation-guard-convergence/trace.md)。用户明确授权承接，不继承原历史验收passed或原已归档Change。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| R1 | reproduction | capture.md 的2026-10-27补证；本会话 Chrome 新开 /requirements | BUG-0056 验收8/8，结果待核对；展开详情为缺少正式同步成功证明，最近核验06:57:57 | 最新验收与旧执行保护同时存在，并非仅旧截图 |
| R2 | code_path | src/backend/app/governance/direct_completion.py：status | can_verify要求terminal、has_sync、needs_review；无成功同步记录时为false | UI不提供核验入口 |
| R3 | code_path | src/backend/app/governance/direct_completion.py：recover、verify | 无completion_manifest的apply/modify提前报历史缺证；direct_sync_missing不在后继核验兜底原因中 | 调用恢复也无法进入后继核验 |
| R4 | code_path | src/backend/app/governance/successor_completion.py：verify_successor | proofs仅接收sync_succeeded且有completion_manifest的旧步骤；空集合即拒绝 | 后继证明实现仍依赖旧同步证明 |
| R5 | config_diff | 本会话docker exec只读sha256sum，与工作区shasum比较 | 后端direct_completion.py SHA256=b480e866962b88350f521f384da79b86c4a2b4d8769cf38dfdd9dc9d8680e97c；successor_completion.py SHA256=0a9d8b9fc4c65b80b9049b175aa187691a3df035a5c3c6e571ef47c05b68f8b5；两者均一致 | 排除这两个后端核心文件未部署；不外推全部服务版本一致 |
| R6 | code_path | src/backend/tests/test_successor_completion.py：successor_scene；test_direct_completion.py：test_failed_sync_is_not_mislabeled_as_historical_missing | 正向后继样本预先设置旧completion_manifest；空steps样本断言不可核验 | 现有测试没有覆盖无旧证明但后继证据独立完整的正向链路；本轮仅审阅未运行测试 |


根因状态：confirmed，限于本次分支阻断机制。复用本会话 bug-explore 的新页面观察、部署只读哈希和源码分析；本次完善不冒充再次运行产品恢复。旧执行为什么未留下同步证明、修复后当前现场是否可安全放行仍需分别验证。

### 已确认机制与排除项

历史修复覆盖“已有旧同步清单，后续合法交付与其不同”，未覆盖“旧执行已停止且无成功同步清单”。入口、恢复分派、后继验证器三个层级共同阻断；刷新或仅修复提示文字无法解除限制。停止状态本身允许核验，缺少旧同步证明才是此次关键条件。页面仍在验收中，本次未观察阶段回退，不将历史阶段回退现象套用于本次。

排除这两份核验代码未部署和单纯前端文字滞留的解释。未证明所有对象受影响、没有执行真实恢复请求，也未确认当前BUG-0056后继证据满足全部权限、版本、依赖和收据条件。历史归因保持partial，不能补造旧执行成功。

### 修复方向与验证闭环

建立不以旧成功同步为必要条件的独立后继核验协议：以可信原操作身份与可用启动基线定位对象、绑定、动作及时间关系，核验后续正式完成收据、当前输入指纹、逐项验收、权限和并发版本。缺少可信身份或基线则继续阻断并明确缺口；不可将“没有旧证明”改为无条件成功，也不可只删除has_sync判断。

保留旧停止状态与事件；单独保存后继证明及审计结果，原子解除当前对象限制。旧有证明恢复与review/archive专用协议保持隔离。验证采用acceptance.md的AC-001至AC-008；合成回归、真实产品、当前现场恢复分别记录，不以静态校验替代行为通过。
