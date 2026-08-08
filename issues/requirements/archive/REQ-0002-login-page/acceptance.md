---
requirement_id: REQ-0002-login-page
title: Web 端登录页验收标准
acceptance_status: passed
owner: product
source: requirement.md
created_at: 2026-08-07 18:03:38
updated_at: 2026-08-08 23:37:38
---

# Web 端登录页验收标准

## 功能 AC

- [ ] AC-001 首页所有登录相关入口或 CTA 点击后进入同一个登录页。
- [ ] AC-002 登录页显示时，首页主体内容不再作为当前主交互界面展示。
- [ ] AC-003 直接访问带 `#login` 的地址时，应显示登录页。
- [ ] AC-004 登录页左上角显示“返回首页”入口。
- [ ] AC-005 点击“返回首页”后恢复首页视图，并清除 `#login` 或等价登录页状态。
- [ ] AC-006 登录卡片顶部显示 MoonBox 产品 Logo，且不是旧 Logo、占位图或纯文本替代。
- [ ] AC-007 登录页背景复用首页产品视觉，并通过深色遮罩保证表单区域清晰可读。
- [ ] AC-008 登录表单包含用户名输入框、密码输入框、记住我控件和登录按钮。
- [ ] AC-009 用户名与密码均为必填；为空提交时应阻止提交并出现浏览器原生或字段级提示。
- [ ] AC-010 密码输入框默认以密码类型展示，不直接显示明文。
- [ ] AC-011 登录按钮文案应表达“登录并进入 MoonBox”的主操作语义，可使用“登录并开启宝盒”或等价中文文案。
- [ ] AC-012 当前原型提交不发起真实鉴权请求，不生成 Token，不改变真实会话状态。
- [ ] AC-013 登录页不展示忘记密码、申请体验、注册、第三方登录、邮箱验证码或手机号验证码入口。
- [ ] AC-014 桌面视口下登录卡片居中，背景产品视觉可见但不干扰表单阅读。
- [ ] AC-015 移动视口下登录卡片、输入框、按钮和返回入口不得横向溢出，关键文案不得互相遮挡。

## UI AC

- [ ] AC-UI-001 登录页使用深色 MoonBox 主题，主背景接近 `#0A0C1B`，卡片接近 `#12142B`，主按钮使用金色强调。
- [ ] AC-UI-002 登录卡片使用近直角和细线边框，不使用大圆角、厚重阴影或蓝紫科技渐变。
- [ ] AC-UI-003 表单 Label、Placeholder、辅助说明、按钮文字在深色背景下具备足够对比度。
- [ ] AC-UI-004 登录页品牌 Logo、标题、说明文案、表单字段、记住我和按钮的视觉层级与原型截图一致或更清晰。
- [ ] AC-UI-005 返回首页入口视觉层级低于登录按钮，但在页面左上角保持可发现。

## 横切 AC（knowledge-base）

本需求不命中 `admin-list`、`admin-form`、`admin-modal`、`media-upload` 标签；无横切 AC。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-08 23:37:38
accepted_by: workflow-sync
source_change: add-login-page
source_sprint: sprint-001
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

