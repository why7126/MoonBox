---
bug_id: BUG-0061-cross-entry-continuation-guard-convergence
title: 跨入口续接执行保护不收敛根因分析
created_at: '2026-10-21 15:55:12'
updated_at: '2026-10-21 15:55:12'
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
