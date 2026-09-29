---
bug_id: BUG-0021-requirement-center-bug-card-severity-display
title: 需求中心 BUG 卡片显示优先级 P 值而非严重性
status: active
created_at: 2026-09-14 14:01:07
updated_at: 2026-09-14 14:01:07
severity: medium
---

# 临时规避

正式修复前，不以需求中心 BUG 卡片上的 `P0` / `P1` / `P2` / `P3` 标签判断 BUG 严重性。

## 操作方式

1. 打开目标 BUG 的 `trace.md` 或 `bug.md`。
2. 以 Frontmatter 中的 `severity` 为准。
3. 需要跨条目核对时，读取 `issues/bugs/_registry.yaml` 对应 BUG 条目的 `severity`。
4. 评审、纳入 Sprint 或排序时，不使用卡片 P 值作为 BUG 严重等级依据。

## 适用范围

- 需求中心 BUG 卡片分级标签展示。
- 当前活动 BUG 和历史 BUG 的人工核对。

## 限制

- 该规避不能修复页面误导，只能避免人工误判。
- 如果 API 或前端测试仍使用 BUG `priority` fixture，后续修改仍可能回归；正式修复需要同步后端响应模型、前端渲染和测试。
