---
change_id: fix-requirement-center-html-preview-auth-lost
type: fix
status: applied
created_at: 2026-09-14 15:39:22
updated_at: 2026-09-14 15:56:44
bug_id: BUG-0022-requirement-center-html-preview-auth-lost
sprint_id: sprint-006
owner: product
source: issues/bugs/review/BUG-0022-requirement-center-html-preview-auth-lost/
specs:
  - web-catalog-requirement-center
product_data_collection_observability:
  status: applicable
  affected_layers:
    - request_logs
  reason: HTML 预览修复影响前端受控请求与后端 preview API 排障链路，需要确认请求日志可脱敏定位认证、权限和项目作用域失败。
  validation: 已通过前端组件测试验证受控 preview URL 携带项目作用域和 Bearer header、成功时打开 Blob URL、认证失败和缺 URL 使用脱敏 toast、popup blocked 不误报成功；测试输出未记录完整 HTML 正文、Bearer、Cookie、本机路径或无权对象内容。
execution:
  schema_version: 1
  started_at: 2026-09-14 15:52:38
  completed_at: 2026-09-14 15:56:44
  last_event: opsx.apply
---

# Change Trace

## 状态

```yaml
status: applied
bug_id: BUG-0022-requirement-center-html-preview-auth-lost
sprint_id: sprint-006
tasks_total: 11
tasks_done: 11
```

## Bug Readiness Report

| 检查项 | 结果 | 证据 |
|---|---|---|
| BUG 状态 | ready | trace 为 `in_sprint`，iteration 为 `sprint-006` |
| 根因证据 | ready | `root-cause.md` 为 confirmed，列出后端鉴权、前端请求封装、直开 URL 和测试断言证据 |
| 验收口径 | ready | `acceptance.md` 覆盖受控请求、Blob URL、错误反馈和不回退范围 |
| Observability Gate | ready | 适用 `request_logs`，不新增 DB、对象存储、Task Trace 或新的日志落库路径 |

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-14 15:55:27 | /opsx-apply | 实现受控 HTML 预览请求、Blob URL 打开、失败反馈与前端回归测试；聚焦测试和类型检查通过。 |
| 2026-09-14 15:39:22 | /bug-opsx | 创建 OpenSpec Change，生成 proposal/design/spec/tasks/trace，状态为 proposed。 |

## 实现证据

| 类型 | 结论 | 证据 |
|---|---|---|
| 前端请求封装 | 新增 `governanceTextRequest()`，用于受控读取 `text/html` 响应并复用 Bearer 与 `X-Chat-Client` header | `src/web/src/components/workbench/governanceApi.ts` |
| HTML 预览行为 | HTML / `new-tab` 文档入口改为 scoped URL + 受控文本请求 + `text/html` Blob URL；缺 URL、认证失败和 popup blocked 均使用原页面 toast 反馈 | `src/web/src/pages/catalog/RequirementCenterPage.tsx` |
| 回归测试 | 删除裸 preview API URL 直开断言，覆盖 Bearer、`space_id`、`repository_id`、Blob URL、认证失败、缺 URL 和 popup blocked | `src/web/src/requirement-center.test.tsx` |
| 安全与观测 | 不新增后端 API、DB、对象存储或 Task Trace；不把 token、Cookie、完整 HTML、本机路径或无权对象写入 URL/toast/测试输出 | `design.md`、`test-plan.md` |

## 验证记录

| 命令 | 结果 | 说明 |
|---|---|---|
| `./node_modules/.bin/vitest run src/requirement-center.test.tsx` | 通过 | 90 passed，覆盖 HTML preview 受控请求与不回退场景 |
| `./node_modules/.bin/tsc --noEmit` | 通过 | TypeScript 类型检查通过 |

## 归档前同步检查

| 检查项 | 结论 | 说明 |
|---|---|---|
| Delta spec | ready | `web-catalog-requirement-center` MODIFIED `卡片文档查看与详情跳转`，正式 spec 中存在同名 Requirement，可归档合并 |
| 长期文档 | N/A | 本次未新增或变更 API contract、DB schema、OpenAPI/Orval、部署、release、README 或 `.env.example`；归档只需合并 OpenSpec 正式规格 |
| 产品数据采集与观测 | ready | 影响层为 `request_logs`；验证已覆盖受控请求、脱敏失败反馈和测试输出安全边界 |
| Prototype/UI final consistency | N/A | 本 Change 修复 HTML 预览访问链路，不调整原型视觉、UI Reference Contract、selector 映射或 1440px 视觉验收口径 |
