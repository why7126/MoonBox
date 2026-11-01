---
title: 独立 Change 可信时间验收映射
created_at: "2026-10-31 22:52:19"
updated_at: "2026-10-31 22:52:19"
---

# 独立 Change 可信时间验收映射

## 验收范围

完整覆盖 BUG-0070 AC-001–007。实现与聚焦验证已完成；结构化执行结果以 evidence/acceptance 最新完整 manifest 为准，产品观察不是模型执行轮次证明。

| 验收项 | 验证入口 |
|---|---|
| AC-001 | test_change_time 缺字段投影、product-* 原故障样本截图 |
| AC-002 | test_change_initialization、test_workflow_execution |
| AC-003 | start/apply与共享正文写入的modify/archive参数化回归，保留首次完成 |
| AC-004 | 重放字节相同、历史只读及无查询时间回退 |
| AC-005 | 非法候选矩阵、missing标签与synthetic截图 |
| AC-006 | 主题×视口截图及computed-style，来源卡、API、优先级与动作回归 |
| AC-007 | OpenAPI/Orval、规则/API索引、真实刷新观察与合成证明分层 |

## 签认

AI 已目视核对 verification.md 中列明的截图和样式事实；完整机器结果由 opsx-accept 回填。未执行正式归档。

