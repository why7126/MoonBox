---
bug_id: BUG-0061-cross-entry-continuation-guard-convergence
title: 跨入口续接执行保护不收敛根因分析
created_at: '2026-10-21 15:55:12'
updated_at: 2026-10-27 16:15:21
status: confirmed
historical_attribution_status: partial
---

# 跨入口续接执行保护不收敛根因分析

## 现象与确认范围

旧产品执行仅完成进度同步，CLI续接完成后，当前验收ready但旧needs_review保护仍阻断并回退卡片。confirmed仅指可解释此现象的后继证明缺口、投影机制和dry-run误识别；不表示历史每一行变化及写入者均可归因。历史归因partial。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | screenshot | capture.md附件名及同会话产品/requirements只读观察 | BUG-0055开发5/5、测试7/7，待开发、结果待核对、归档禁用 | 交付进度与产品准入分离 |
| E2 | data_sample | 部署execution_guards/completion_handoffs；对象BUG-0055，2026-10-21 14:36:07本地核验 | opsx-apply，needs_review，ready-dev，direct_dependency_conflict，blocked | 持久旧保护，非刷新缓存 |
| E3 | runtime_log | 原轮direct-command journal；chat_events seq669、683/684 | 140个边界；最后正式同步opsx.progress，9/12、pending；其后写verification.md和trace.md；终态sync_incomplete | 原执行业务未完成，存在同步后收尾 |
| E4 | data_sample | bug.md“19项文件差异清单”；direct_completion.manifest/differences | 6个既有文档修改、13份新增摘要；规则/相关正式规格/注册信息/Sprint投影无差异 | 累计变化路径明确，不能整体忽略 |
| E5 | code_path | src/backend/app/governance/execution_context.py：reconcile_external | 有operation_id且running/needs_review直接返回，评审之外无后继承接分支 | CLI合法完成不能收敛旧apply保护 |
| E6 | code_path | src/backend/app/governance/direct_completion.py：verify/recover | 有原清单时恢复要求当前清单完全相同 | 显式核验也不能承接后继交付 |
| E7 | code_path | src/backend/app/governance/reader.py：执行保护投影 | 未核验时以旧confirmed_stage覆盖并禁用动作 | 待开发和归档阻断的展示来源 |
| E8 | runtime_log | 原轮chat_events seq71与同步journal | opsx.apply --dry-run; 后续命令令外层退出0，内部报任务未完成，仍记sync_succeeded | 文本和外层退出码产生伪成功观察 |
| E9 | reproduction | direct_command_journal.is_formal_workflow_sync纯函数复核 | --dry-run; true返回True，结尾--dry-run返回False，opsx.progress返回True | 分号边界遗漏，事件级成功不等于交付完成 |
| E10 | data_sample | opsx_acceptance.py --change fix-chat-turn-message-order --archive-readiness；既有验收报告 | 12/12、ready=true | 当前验收通过不替代保护与实际发送准入 |

| R1 | reproduction | capture.md 的2026-10-27补证；本会话 Chrome 新开 /requirements | BUG-0056 验收8/8，结果待核对；展开详情为缺少正式同步成功证明，最近核验06:57:57 | 最新验收与旧执行保护同时存在，并非仅旧截图 |
| R2 | code_path | src/backend/app/governance/direct_completion.py：status | can_verify要求terminal、has_sync、needs_review；无成功同步记录时为false | UI不提供核验入口 |
| R3 | code_path | src/backend/app/governance/direct_completion.py：recover、verify | 无completion_manifest的apply/modify提前报历史缺证；direct_sync_missing不在后继核验兜底原因中 | 调用恢复也无法进入后继核验 |
| R4 | code_path | src/backend/app/governance/successor_completion.py：verify_successor | proofs仅接收sync_succeeded且有completion_manifest的旧步骤；空集合即拒绝 | 后继证明实现仍依赖旧同步证明 |
| R5 | config_diff | 本会话docker exec只读sha256sum，与工作区shasum比较 | 后端direct_completion.py SHA256=b480e866962b88350f521f384da79b86c4a2b4d8769cf38dfdd9dc9d8680e97c；successor_completion.py SHA256=0a9d8b9fc4c65b80b9049b175aa187691a3df035a5c3c6e571ef47c05b68f8b5；两者均一致 | 排除这两个后端核心文件未部署；不外推全部服务版本一致 |
| R6 | code_path | src/backend/tests/test_successor_completion.py：successor_scene；test_direct_completion.py：test_failed_sync_is_not_mislabeled_as_historical_missing | 正向后继样本预先设置旧completion_manifest；空steps样本断言不可核验 | 现有测试没有覆盖无旧证明但后继证据独立完整的正向链路；本轮仅审阅未运行测试 |

证据复用同会话explore与generate只读调查，不冒充本轮重新执行产品归档。私有原始journal与数据库不复制入仓库，证据按对象、事件序号及函数定位；19项完整路径以bug.md为单一清单。

## 已确认根因

1. 系统只验证“原同步证明与当前清单相等”，缺少“旧未完成操作→合法后继交付”的独立证据关系。原轮仅progress，CLI后继任务及验收变化本来就不应与原清单相等。
2. 外部同步为保留旧执行而直接返回；显式恢复仍要求原清单相等，形成恢复闭环缺口。正确保护不能删除，应补足后继核验能力。
3. 卡片沿用旧confirmed_stage，掩盖已发生的后继交付；泛化提示无法说明当前冲突及可用恢复路径。
4. 同步识别未正确解析--dry-run后的分号，且外层shell退出0不能证明内部同步成功。start/progress/完成事件需分别记录，不能将任意sync_succeeded当作完成。

## 已排除与未确认判断

- 非简单浏览器缓存：持久guard和reader路径解释刷新无效。
- 非缺少验收成果：当前ready已证实；但不能据此绕过其他准入。
- 不能全部归咎早期dry-run：最后清单来自后续真实opsx.progress。
- 没有证明当前19项全为安全派生输出：design、tasks等需语义核验及受影响范围复验。
- 没有证明所有命令、REQ或其他卡片均已复现；通用修复范围需用矩阵验证。

## 历史归因缺口

19项是最后同步到探索时当前态的累计差异，不是首次冲突文件列表。已读取baseline、operation、逐文件哈希及原工具事件；只有启动正文与同步时哈希，缺少同步时完整正文，不能精确还原所有历史行级变化、时间和写入者。seq683/684可证明收尾目标，不能证明全部19项由其造成。

后续发现可信历史快照可补充；否则保持partial，在隔离复现中记录同步、终态、CLI续接三时点清单。此归因缺口不阻断机制修复评审，但历史恢复仍需独立验证当前交付，不能伪造历史成功。

## 修复方向与验证闭环

保留旧操作、新建后继核验事实；验证对象/Change/项目绑定/权限/完成事件/输入指纹/当前验收，分类差异并以保护版本原子收敛。归档和评审保留专用协议；核验不重放命令、不重复合并。同步采集使用可校验结构化结果及实际事件身份，内部失败不被外层0掩盖。

验证见acceptance.md：纯识别与语义单测、并发接口测试、CLI隔离归档、部署后产品实际发送至归档终态分别取证。BUG-0055为恢复现场，不按ID特判。

## 本轮已部署修复

正式后继核验已实现并部署。BUG-0055通过产品核验及标准归档，两次隔离REQ/BUG实际发送均至validated/done。保留任务范围、有效验收、收据、权限与并发门禁，历史归因仍partial。证据见关联Change evidence/acceptance/implementation。核验响应曾出现504，回读确认已提交，不重放命令。

## 2026-10-27 复发根因：无旧同步证明的后继核验缺口

根因状态：confirmed，限于本次分支阻断机制。复用本会话 bug-explore 的新页面观察、部署只读哈希和源码分析；本次完善不冒充再次运行产品恢复。旧执行为什么未留下同步证明、修复后当前现场是否可安全放行仍需分别验证。

### 本次证据链

见上方统一证据链R1至R6；E1至E10为历史现场，不混用两次证据。

### 已确认机制与排除项

历史修复覆盖“已有旧同步清单，后续合法交付与其不同”，未覆盖“旧执行已停止且无成功同步清单”。入口、恢复分派、后继验证器三个层级共同阻断；刷新或仅修复提示文字无法解除限制。停止状态本身允许核验，缺少旧同步证明才是此次关键条件。页面仍在验收中，本次未观察阶段回退，不将历史阶段回退现象套用于本次。

排除这两份核验代码未部署和单纯前端文字滞留的解释。未证明所有对象受影响、没有执行真实恢复请求，也未确认当前BUG-0056后继证据满足全部权限、版本、依赖和收据条件。历史归因保持partial，不能补造旧执行成功。

### 修复方向与验证闭环

建立不以旧成功同步为必要条件的独立后继核验协议：以可信原操作身份与可用启动基线定位对象、绑定、动作及时间关系，核验后续正式完成收据、当前输入指纹、逐项验收、权限和并发版本。缺少可信身份或基线则继续阻断并明确缺口；不可将“没有旧证明”改为无条件成功，也不可只删除has_sync判断。

保留旧停止状态与事件；单独保存后继证明及审计结果，原子解除当前对象限制。旧有证明恢复与review/archive专用协议保持隔离。验证采用acceptance.md的RC-001至RC-008；合成回归、真实产品、当前现场恢复分别记录，不以静态校验替代行为通过。
