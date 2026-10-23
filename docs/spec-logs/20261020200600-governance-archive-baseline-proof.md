---
title: 归档恢复基线连续证明
created_at: '2026-10-20 20:06:00'
updated_at: '2026-10-20 20:06:00'
---

# 归档恢复基线连续证明

来源：REQ-0046 / BUG-0052 的 opsx-modify，沿用两个已实施 Change 和 sprint-011，不新增业务对象。

问题：独立 Change 归档使全树规格哈希前进，旧恢复记录拒绝刷新；产品验收准入未包含恢复门禁。历史四条已完成归档构成可验证的连续哈希路径，原始恢复记录无需删除。

调整：共享只读恢复判定，要求每条边哈希相接、归档唯一且完成、增量结果有效、capability 不与当前对象重叠；新记录绑定 delta 哈希。显式刷新保留 previous_record 和 baseline_transition，已合并状态不重置。无法证明或并发变化仍阻断，准入读取不执行仓库代码。

验证：181 项聚焦回归通过，追加真实 turns 正反向验证后跨入口 94 项通过；含真实 OpenSpec 临时归档。产品部署与正式对象准入证据归属两 Change 的 evidence/archive-baseline-admission.json。此记录不代表已归档正式对象；无新增模型调用。
