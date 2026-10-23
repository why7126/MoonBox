---
bug_id: BUG-0028-requirement-center-card-owner-raw-user-id
title: 需求中心 Capture 卡片负责人可读名称修复评审
status: done
created_at: 2026-10-09 23:21:33
updated_at: 2026-10-19 11:23:32
owner: 产品团队
---

# 需求中心 Capture 卡片负责人可读名称修复评审

## 评审结论

通过，确认按常规 Sprint 流程修复负责人标签直接显示内部身份标识的问题。本结论不表示代码已修复、回归已通过或 BUG 已纳入 Sprint。

## 评审依据

| 检查项 | 结论 |
|---|---|
| 可复现与根因 | Firefox 刷新后在 REQ-0038 卡片复现；同条目治理 owner、后端原样映射及前端直接渲染构成闭环。`root-cause.md` 为 confirmed，根因证据校验通过。 |
| 严重等级 | medium：负责人难以辨认，影响协作；目前没有权限绕过、数据损坏或创建失败的证据。 |
| 回归验收 | `acceptance.md` 的 AC-001 至 AC-008 覆盖名称优先级、缺失回退、REQ/BUG、历史 owner、详情/筛选、长名称布局及权限；修复后全部待执行。 |
| 名称契约 | 推荐沿用现有用户上下文顺序：昵称 → 用户名 → 明确的通用用户文案；空 owner 显示“未分配”。稳定身份键继续用于归属、权限和筛选，不能直接替换为昵称。具体字段与通用文案在 Change 设计中定稿。 |
| 热修路径 | 不按 P0 热修；现有 workaround 仅作人工核对建议，按正常 Sprint 纳入并实施。 |
| 影响边界 | 已确认当前本机 REQ-0038 页面；其他部署、BUG 卡片、详情与筛选仍属实施和验收范围，不预先宣称受影响。 |

## 数据采集与链路观测

`product_data_collection_observability: not_applicable`，`affected_layers: []`。本次评审仅更新治理文档，不调整 API、DB、请求日志、行为事件、Task Trace 或端请求封装。后续 Change 如触及身份解析 API、Web 请求或持久化字段，应重新声明受影响层、脱敏边界与验证结果。
