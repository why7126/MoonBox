---
title: 聊天旧面板清理边界修复设计
created_at: '2026-10-19 18:50:12'
updated_at: '2026-10-19 18:50:12'
---

# 聊天旧面板清理边界修复设计

## 根因

removeLegacyGovernancePanels 候选包含所有 [aria-label] 和 dialog；textContent 将后代正文纳入判断。真实历史会话出现确认应用文字即可误删 chat-main。

## 修复方案

候选只包含 .chat-main > .pg-result、governance-result-preview 标识以及明确命名为审阅治理成果的 dialog/role=dialog。保持既有关键词判断，避免删除不含旧文案的明确候选。禁止通用标签容器和普通 dialog 进入候选。重复清理返回零且保留外壳。

## 验证与边界

AC-001/002 使用实际函数 DOM 测试先红后绿；AC-003 使用 1440px 真实会话，刷新、对话/轨迹切换、composer 可用及 computed style；AC-004 在页面恢复后真实发送 req-review 并回读新轮次、文件、状态和应用记录。

本次不是原型复刻，不新增布局、样式、按钮或 modal；UI Reference Replication 与新 Skeleton 不适用。以现有聊天外壳为结构契约：.chat-main、[data-testid=chat-conversation]、.chat-composer、#chat-execution-panel 都不得被清理。截图是故障证据，不是新视觉参考稿。

## 横切门禁

AC-XCUT: n/a；非 admin-list/admin-form/admin-modal/media-upload。复用 Sprint-009 复盘中真实产品与合成证据分离、避免重复样本的经验。

product_data_collection_observability: not_applicable；affected_layers: web。DOM 清理不改变 API、DB、request_logs、usage_events、Task Trace、请求封装或保留周期；validation 为 DOM 回归及现有应用状态回读。

## 风险与回滚

未知无标识历史面板不再凭正文删除，优先保护现有会话；明确旧面板仍保留清理测试。只更新 Web 服务，保留原镜像供回滚。

## 真实评审返修补充

AC-004 首轮真实评审完成但被 review_state 拒绝。REQ-0046 trace 使用 req_id，主文档使用 requirement_id；Workflow Sync 已支持二者，评审校验只认 requirement_id。校验需接受 trace 保留原有 req_id，同时拒绝缺失、错误或冲突身份；不修改文件身份、不放宽其他写入边界。补充 backend 单元回归并更新 backend/worker/controller 本地镜像后再次执行真实评审。API、DB schema、客户端生成无需变化；affected_layers 增补 backend governance，观测只复用既有错误码/应用记录，无新埋点。

### 同步回读补充

修复身份后第二轮成果已通过 validate_review 并保存 result.json，但 source-mode 正式 Workflow Sync check 发现 acceptance 来源事件仍为 req.complete。模型依据“保留所有子文档”提示用临时限制保留原文；后端校验允许旧来源，最终同步却要求 req.review。临时副本 dry-run 确认仅该子文档需同步。收尾应在完整文档校验成功后把允许的 complete→review 来源事件归一，再完整复验；不改验收状态/内容。同时提示明确允许这项元数据同步，禁止修改或绕过同步工具。

补证限制：原始保留成果在补齐依赖的临时副本调用相同 _verify_source_workflow_sync 也通过，故来源事件漂移是已证实的契约不一致，但尚不能单独归因为真实环境 generic 拒绝的唯一原因。最终以更新后的真实轮次与应用回读判断，不能以临时副本成功替代产品成功。

### 原生同步末尾换行兼容

第三轮使用原始同步，真实 worker check 零差异，但校验拒绝 review_acceptance_scope。upsert_acceptance_block 的纯函数复现显示仅 source_event 更新与文末增加一个空行；校验以正文逐字节比较导致误判。仅对验收正文比较忽略末尾换行，保留元数据、正文语义及不相关内容严格边界；测试正例为原生同步换行，负例为追加验收正文。

### Source-mode 真实部署根因确认

第四轮文档校验通过并保存 result.json，仍 generic 拒绝。运行配置检查确认治理投影 root 与真实 source_root 不同；root 不含 scripts/sync-workflow-status.py，source_root 存在。_verify_source_workflow_sync 错误从投影目录寻找脚本，造成确定性拒绝；此前临时副本将两者合一所以无法复现。修复从可信 source_root 定位脚本和工作目录，在调用前后同时核对投影与源码治理事实，任一漂移均拒绝，不接受客户端路径。
