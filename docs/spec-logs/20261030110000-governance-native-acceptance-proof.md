---
title: 原生隔离验收证据接入
created_at: 2026-10-30 11:00:00
updated_at: 2026-10-30 11:00:00
---

# 原生隔离验收证据接入

来源：REQ-0048-chat-isolated-acceptance-orchestration / add-chat-isolated-acceptance-orchestration / sprint-016。

真实模型通过 moonbox_acceptance 原生工具执行验收，原自动验收器仅支持命令事件与受信归档事件，无法正确签认该协议。新增 isolated_acceptance_v1，只读核对真实控制账本；保留所有其他证据与完成门禁，不将工具调用改造成无实际效果的命令。

变化包括计划字段校验、只读证据适配、真实源轮次/尝试/确认/文件归集/资源释放/一次续接与剩余预算核对。错误身份、丢失确认、未归集、未知预算、错误尝试和不支持模式均拒绝。原命令与归档证明行为不变。

验证入口为 test_acceptance_proof.py、test_opsx_acceptance.py 和 Change 的 evidence/implementation/product/。真实样本与合成负向夹具分开，不持久化凭证、数据库或原始消息。不声明节省 Token 或时间：本次未取得可比较的独立优化收益样本。未创建额外 Issue/Change。
