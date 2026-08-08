## 背景

来源 REQ：`issues/requirements/review/REQ-0002-login-page/`。

REQ-0002 已从 MoonBox Landing v1.0.2 的首页+登录页混合原型中抽取出登录页范围，并完成评审与 `sprint-001` 纳入。登录页原型位于 `issues/requirements/review/REQ-0002-login-page/prototype/web/login-prototype.html`，上下文位于 `prototype/web/context.md`，截图位于 `prototype/web/prototype-login.png`。

本 Change 只定义登录页前端体验，不创建真实认证能力。后端登录接口、Token、会话刷新、权限校验和登录后工作台跳转均由后续独立需求承接。

## Goals / Non-Goals

**Goals:**

- 将 REQ-0002 登录页页面状态、品牌视觉与表单结构转为 OpenSpec 可验收规格。
- 约束首页 CTA 进入登录页后隐藏首页主体、显示登录页并写入 `#login` 或等价状态。
- 约束返回首页入口清除登录页状态并恢复首页视图。
- 约束登录卡片、用户名密码表单、记住我、必填校验和非支持认证入口的排除。
- 约束登录页使用 MoonBox 深色主题、金色强调、近直角和细线风格，并保持桌面/移动端可读。

**Non-Goals:**

- 不实现后端鉴权接口、Token、会话刷新、权限校验或登录后工作台跳转。
- 不实现忘记密码、注册、申请体验、第三方登录、邮箱验证码或手机号验证码。
- 不调整首页 Logo、首页首屏右侧产品视觉或首页信息结构；这些内容归属 `REQ-0001-homepage`。
- 不调整 API、数据库、对象存储、管理后台、小程序或移动端能力。

## Decisions

### D1. UI 策略：asset-port + scoped-css-port

选择基于需求原型资产的 `asset-port + scoped-css-port` 策略：实现时复用 MoonBox Logo 和首页产品视觉资产，登录页样式限定在登录视图范围内。

理由：

- REQ 已提供明确 HTML 原型、上下文和 PNG 截图，不需要重新设计。
- 登录页是 Patch 型前端体验更新，局部 CSS 对齐比引入全局设计系统改造更稳。
- MoonBox UI 规则要求深色背景、金色强调、近直角、细线和克制排版，局部实现即可满足。

备选方案：

- 全量认证模块建设：超出当前原型范围，会引入 API、安全和会话边界。
- 直接嵌入原型 HTML：可追溯性弱，且不利于接入现有 Web 应用结构和测试。

### D2. 登录表单只做前端体验，不连接真实认证

登录表单包含用户名、密码、记住我和登录按钮，但提交时仅进行必填校验与阻止默认提交，不发起真实鉴权请求。

理由：

- REQ 明确当前原型提交不连接后端。
- 真实认证会引入 API、Token、权限、安全和工作台跳转，需要独立需求与规格。

### D3. 原型冲突优先级

若实现过程中出现原型、验收和规则冲突，优先级为：

```text
prototype/web/login-prototype.html > prototype/web/prototype-login.png > prototype/web/context.md > acceptance.md > rules/ui-design.md > openspec/specs
```

Conflict Resolution：

- HTML、PNG、context 均要求登录页包含返回首页、背景产品视觉、深色遮罩、登录卡片、MoonBox Logo、用户名密码、记住我和登录按钮；实现必须保留该结构。
- 原型截图按钮文案为英文 `Sign in and open MoonBox`，需求验收允许“登录并开启宝盒”或等价中文主操作文案；实现应以中文产品文案为准，并保持“登录并进入 MoonBox”的语义。
- `acceptance.md` 要求不展示忘记密码、申请体验和未定义认证入口；若 HTML 原型后续出现这些入口，以验收标准排除。
- `ui-design.md` 中按钮圆角、金色强调和深色主题约束与原型一致；若局部视觉微调，应优先保证表单可读性和移动端不溢出。

### D4. 与首页 Change 的关系

登录页入口依赖首页 CTA，但登录页能力与首页品牌视觉能力分属两个 Change：

- `add-homepage-brand-visual` 负责首页 Logo、首屏产品视觉和 CTA 入口。
- `add-login-page` 负责登录页显示、返回首页、登录表单和登录页视觉。

实现阶段若两个 Change 同 Sprint 执行，CTA 可直接进入本登录页；若单独执行，应保持既有登录入口兼容。

## Risks / Trade-offs

- [Risk] 登录页与首页共用产品视觉资产，可能出现加载体积或裁切策略不一致。→ Mitigation：实现阶段复用同一资产来源，首页保持清晰展示，登录页叠加深色遮罩。
- [Risk] 表单看似可登录但不连接后端，可能造成用户预期偏差。→ Mitigation：当前范围仅原型/前端体验，后续真实认证需求中再定义提交结果和错误提示。
- [Risk] 移动端登录卡片可能溢出或遮挡返回入口。→ Mitigation：任务中加入桌面和移动端视觉验收。

## Migration Plan

1. 在 Web 前端增加登录页状态与视图，实现首页 CTA 进入登录页。
2. 接入 MoonBox Logo 和首页产品视觉背景，添加深色遮罩与登录卡片样式。
3. 实现用户名、密码、记住我和登录按钮，保持必填校验且阻止真实提交。
4. 实现返回首页入口，恢复首页视图并清除 `#login` 或等价状态。
5. 使用前端测试或截图检查验证桌面与移动端不溢出、不遮挡。
6. 若需要回滚，仅回退登录页视图和入口状态，不影响 API/DB。

## Open Questions

- 真实认证、登录失败提示、会话保持和登录后默认跳转目标是否由后续独立 REQ 承接？默认是。
