---
bug_id: BUG-0049-archive-wrapper-workflow-sync-unrecognized
title: 归档包装脚本同步成功漏识别根因分析
created_at: '2026-10-19 23:00:04'
updated_at: '2026-10-19 23:00:04'
root_cause_status: confirmed
---

# 归档包装脚本同步成功漏识别根因分析

## 根因状态

status: confirmed

## 现象

归档包装脚本已成功完成，正式 BUG 为 done，但门禁保留 needs_review/result_unverified，看板显示归档前 acceptance。Chat 对象权限依据正式文件变为只读，与看板结论不一致。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | screenshot | 本会话两张用户附件及 explore 浏览器 /chat 观察；capture.md | 已归档回复与验收中卡片并存，Chat 对象只读 | 跨入口不一致 |
| E2 | data_sample | capture.md 已有证据表；BUG-0048 正式归档目录与 bug.md | 正式文件 done，归档结构 validate_result=true | 不是归档文件完全未应用 |
| E3 | runtime_log | 同会话 explore 读取本轮工具事件，脱敏摘要见 bug.md | archive-change.sh --finalize 最终退出 0 | 包装脚本执行成功 |
| E4 | data_sample | explore 对私有 operation 和门禁只读查询，摘要见 capture.md | terminal/partial_write，最终摘要当时匹配；所有同步标记 false，门禁 needs_review | 同步证明缺失是确认阻断点 |
| E5 | code_path | scripts/archive-change.sh finalize 分支 | 内部先 Workflow Sync 再迁移关联 Issue | 顶层命令未暴露内部同步调用 |
| E6 | code_path | src/backend/app/governance/direct_command_journal.py:is_formal_workflow_sync | 只匹配 commandExecution 顶层命令中的同步脚本名及 --event | 包装命令识别遗漏 |
| E7 | reproduction | 本次 bug-complete 内直接调用 is_formal_workflow_sync 的无写入三输入探针 | wrapper=False，direct=True，check=False | 最小输入稳定复现识别差异，检查命令仍被正确排除 |
| E8 | code_path | src/backend/app/governance/execution_context.py:reconcile；reader.py | 无同步证明不能 confirm；未放行对象采用 confirmed_stage | 漏识别传导至旧阶段显示 |

E1—E4 承接本会话 2026-10-19 真实运行取证；E5—E8 本次核对现有代码并运行无副作用探针。截图不复制敏感路径；运行样本不保存用户身份或完整消息。快照相等仅表示取证时事实，后续新增 Issue 会改变治理快照。

## 已排除假设

| 假设 | 排除依据 |
|---|---|
| 只有模型声称成功，正式文件完全未归档 | E2 正式文件与结构校验 |
| 只是前端缓存或文案错误 | E4 数据库门禁本身待核对，E8 可解释投影 |
| Worker 未就绪导致本轮根本未执行 | E3 有实际成功工具事件，轮次 completed |
| 最终脚本仍因验收格式失败 | 早期失败修正后最终退出 0；不能混淆前后尝试 |

## 已确认根因

同步观测协议与推荐归档包装脚本不一致：平台仅识别顶层显式同步命令，而归档 finalize 将同步封装在脚本内部。成功执行未产生平台可识别的同步证明，结果被记为 partial_write；reconcile 无法确认，reader 保留原验收阶段。正式文件已完成与门禁未完成可同时存在。

仅确认本例和相同识别路径；其他包装命令是否受影响需独立覆盖，不能泛化为所有治理操作故障。

## 修复方向

以可信结构化凭证关联原执行、对象、动作、同步和迁移结果以及最终摘要；对当前文件做业务校验及稳定摘要复核后确认门禁。不要简单将脚本名加入成功白名单，不信任模型正文或客户端成功布尔值。证据不足时提供具体缺口，保持安全阻断。

既有记录恢复须可重入、只校验并确认原成果，不重放归档。全局摘要随无关治理变更变化时，明确证据适用范围与重新核验策略，禁止无条件忽略差异。

## 验证闭环

本次最小探针确认缺陷机制，不是修复测试。修复后按 acceptance.md 验证成功、内部失败、摘要漂移、重复确认、重启和原执行恢复；以真实页面和可信完成状态共同验收。

## 数据采集与链路观测

product_data_collection_observability: applicable。affected_layers: 命令观测、operation、执行门禁、看板投影。validation: E3—E8 验证关联链；修复后保留阶段、失败原因及最终摘要证明。N/A：本次无 schema、API、客户端或部署变更，不采集原始 Prompt 或密钥。
