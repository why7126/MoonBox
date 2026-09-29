---
change_id: fix-requirement-center-html-preview-auth-lost
bug_id: BUG-0022-requirement-center-html-preview-auth-lost
status: applied
---

# Test Plan

## 自动化

| 范围 | 命令 | 目的 |
|---|---|---|
| 前端需求中心回归 | `./node_modules/.bin/vitest run src/requirement-center.test.tsx` | 验证 HTML 文档入口受控请求、Blob URL 打开、错误反馈和不回退场景 |
| 前端类型检查 | `./node_modules/.bin/tsc --noEmit` | 若调整 helper 或类型，验证类型兼容 |
| OpenSpec | `openspec validate fix-requirement-center-html-preview-auth-lost` | 验证 Change 文档与 delta spec 合法 |

## 执行结果

| 命令 | 结果 | 摘要 |
|---|---|---|
| `./node_modules/.bin/vitest run src/requirement-center.test.tsx` | 通过 | 90 passed |
| `./node_modules/.bin/tsc --noEmit` | 通过 | 无类型错误 |

## 手工或浏览器验收

- 登录后进入需求中心，点击带 HTML / prototype 文档入口的卡片。
- 确认新 Tab 地址不是裸 `/api/v1/requirement-center/.../preview` URL。
- 确认无权或会话失效时原页面展示脱敏失败反馈。
- 确认 Markdown 文档仍从右侧抽屉打开，卡片标题和查看归档仍按既有详情跳转行为工作。

## 观测与安全

- 后端 request log 只保留脱敏路径、状态码和必要排障字段。
- 前端 toast、console、测试输出不得包含完整 HTML 正文、Bearer、Cookie、本机路径或无权对象内容。
- 本次变更不新增 API contract、DB、对象存储、部署拓扑或后台任务；后端 preview API 鉴权契约保持不变。
