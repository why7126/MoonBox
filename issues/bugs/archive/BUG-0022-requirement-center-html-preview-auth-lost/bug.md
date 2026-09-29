---
bug_id: BUG-0022-requirement-center-html-preview-auth-lost
title: 需求中心卡片 HTML 预览直开受保护接口导致认证失败
status: done
owner: 产品团队
discovered_at: '2026-09-14 15:10:06'
environment: local
related_requirement: REQ-0012-frontend-requirement-center
related_change: fix-requirement-center-html-preview-auth-lost
created_at: 2026-09-14 15:12:25
updated_at: 2026-09-14 18:20:41
severity: medium
---

# 需求中心卡片 HTML 预览直开受保护接口导致认证失败

## 现象

用户在需求中心点击卡片中的 HTML 文件后，无法正常预览。新 Tab 显示受控接口错误：

```json
{
  "code": 1001,
  "message": "认证或权限校验失败",
  "data": null
}
```

该问题主要影响 `prototype.html` 或 `prototype/**.html` 等原型/HTML 文档入口。Markdown 文档抽屉读取不在本缺陷范围内。

## 复现步骤

1. 登录 MoonBox 前台。
2. 进入需求中心。
3. 找到包含 `prototype.html` 或 `prototype/**.html` 文档入口的 REQ/BUG 卡片。
4. 点击该 HTML 文档入口。
5. 观察新 Tab 是否直接打开 `/api/v1/requirement-center/issues/{issue_id}/documents/{document_name}/preview` 并返回 `code=1001`。

## 期望结果

- 登录用户点击卡片 HTML 文件后，可以正常打开受控 HTML 预览。
- HTML 预览请求携带当前项目作用域：`space_id` 与 `repository_id`。
- 预览链路复用前端登录态，不因新 Tab 直接导航丢失 Bearer 鉴权信息。

## 实际结果

- HTML 入口当前会打开受保护 preview API。
- 浏览器新 Tab 直接导航无法附加前端存储中的 Bearer header。
- 当前链路疑似未经过项目作用域 URL 拼接，存在缺少 `space_id` 与 `repository_id` 的风险。
- 用户观察到接口返回 `code=1001`、`message=认证或权限校验失败`。

## 影响范围

- 影响需求中心卡片上的 HTML / prototype 文档预览。
- 影响 UI 参考稿、原型拆解、视觉验收和需求评审时对 HTML 原型的查看效率。
- 该问题关联 `REQ-0012-frontend-requirement-center` 的需求中心文档查看体验。
- 当前未发现 Markdown 文档读取、文档保存、Chat 会话、对象存储头像读取或后台管理能力受影响的证据。

## 严重等级说明

严重等级暂定为 `medium`。该问题阻断一个明确的用户工作流，但现有证据未显示数据丢失、权限越界、全站不可用或生产数据风险。

若后续补证显示大量验收流程依赖 HTML 原型预览、或该问题阻断 Sprint 验收与发布门禁，可在缺陷完善或评审阶段重新评估严重等级。

## 待补证

- 浏览器 Network 记录：失败请求的 method、path、status、响应摘要和 `X-Request-ID`。
- 触发问题的具体 BUG/REQ 卡片 ID 与 HTML 文档名。
- 当前页面 URL 中是否已有 `space_id` 与 `repository_id`。
- 浏览器 Console 中是否存在与 `window.open`、Blob URL 或 popup 拦截相关的错误。
