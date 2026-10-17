---
title: API 契约与客户端生成物同步审计
created_at: 2026-10-14 09:00:00
updated_at: 2026-10-14 09:00:00
---

# API 契约与客户端生成物同步审计

当前后端 `app.openapi()` 与 `src/web/openapi.json` 结构完全相等，均为 77 条路径。使用仓库锁定的 Orval 8.29.0 在独立临时目录从当前 `openapi.json` 重生成 `capture.ts`、`governance.ts`、`chat.ts`，三个文件与仓库 `src/web/src/api/generated/` 对应文件逐字节一致；未覆盖工作区既有生成物。

`docs/03-api-index.md` 已记录 governance-preparations 的 REQ/BUG generate 能力、object-sessions 的已接入白名单与未知动作 422/2604，以及候选和 application 写入边界。Change `tasks.md` 中 API schema 或客户端类型变化时同步 OpenAPI、Orval 和 API 文档的任务已完成。当前条件性同步要求成立。

全仓 `validate-api-standard.py` 仍报告 `src/backend/app/api/v1/capture_drafts.py:53` 的 image 路由缺少 `response_model`；该现存全仓门禁问题与本项 OpenAPI/Orval 一致性分别记录，不把它解释为本项同步已失效。
