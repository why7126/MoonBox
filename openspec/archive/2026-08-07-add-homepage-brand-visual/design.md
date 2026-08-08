## 背景

来源 REQ：`issues/requirements/review/REQ-0001-homepage/`。

REQ-0001 已从 MoonBox Landing v1.0.2 的首页+登录页混合原型中抽取出首页范围，并完成评审通过。首页原型位于 `issues/requirements/review/REQ-0001-homepage/prototype/web/homepage.html`，上下文位于 `prototype/web/context.md`，资产为 `Logo1-20260728001940.png` 与 `image.png`。

本 Change 只定义首页能力，不创建登录页能力。首页 CTA 继续指向既有登录页入口；登录页返回首页、用户名密码表单和登录背景遮罩归属 `REQ-0002-login-page`。

## Goals / Non-Goals

**Goals:**

- 将 REQ-0001 首页品牌视觉与首屏结构转为 OpenSpec 可验收规格。
- 约束 Web 首页使用指定 Logo 和产品视觉资产。
- 约束首页首屏文案、CTA、三项能力摘要和响应式展示。
- 保持 Patch 影响面，只改首页品牌资产和首屏视觉相关内容。

**Non-Goals:**

- 不实现登录页表单、认证、会话或后端接口。
- 不调整 API、数据库、对象存储或管理后台。
- 不重构全站设计系统 token。
- 不新增移动端、小程序或桌面端能力。

## Decisions

### D1. UI 策略：asset-port + scoped-css-port

选择基于需求原型资产的 `asset-port + scoped-css-port` 策略：实现时复用 `Logo1-20260728001940.png` 和 `image.png`，并将首页布局、按钮和首屏视觉约束限定在首页视图范围内。

理由：

- REQ 已提供明确首页 HTML 原型、上下文和截图，不需要重新设计。
- 当前变更是 Patch 型首页视觉更新，局部 CSS 对齐比引入全局设计系统改造更稳。
- MoonBox UI 规则要求深色背景、金色强调、近直角按钮和克制排版，局部实现即可满足。

备选方案：

- 全量 DS 重构：影响面过大，不符合本次 Patch 范围。
- 直接嵌入原型 HTML：可追溯性弱，且不利于接入现有 Web 应用结构。

### D2. CTA 行为只保持入口，不定义登录页

首页 `Open MoonBox` 与 `Open first project` 两个 CTA 只要求进入既有登录页入口。本 Change 不规定登录表单字段、`#login` 状态或返回首页行为。

理由：

- 登录页已有独立需求 `REQ-0002-login-page`。
- 首页与登录页混在同一原型中，但需求治理已拆分，避免 Change 范围耦合。

### D3. 原型冲突优先级

若实现过程中出现原型、验收和规则冲突，优先级为：

```text
prototype/web/homepage.html > 用户提供 PNG 截图 > prototype/web/context.md > acceptance.md > rules/ui-design.md > openspec/specs
```

Conflict Resolution：

- HTML 原型和截图均要求首页首屏左文案右产品视觉；实现必须保留该结构。
- `context.md` 提到 `loginPage` 和 `[data-back-home]`，但本 Change 只抽取 `landingPage`，登录相关内容不进入首页规格。
- `acceptance.md` 中首页 PNG 可后续导出，不阻塞 Change 创建；实现验收时应补截图或视觉验证记录。

## Risks / Trade-offs

- [Risk] 首页 CTA 与登录页 Change 分属不同需求，可能出现 Sprint 范围不一致。→ Mitigation：纳入 Sprint 时同时确认 `REQ-0002-login-page` 的状态或将 CTA 行为作为 mock/既有入口处理。
- [Risk] 原型资产较大，前端打包可能受影响。→ Mitigation：实现阶段评估 public asset 与优化策略，但不得改变视觉主体。
- [Risk] 移动端双栏折叠后文字或图片遮挡。→ Mitigation：任务中加入桌面与移动端视觉验收。

## Migration Plan

1. 在 Web 首页视图中接入 Logo 与产品视觉资产。
2. 对齐首页首屏布局、CTA、三项能力摘要和响应式规则。
3. 使用前端测试或截图检查验证桌面与移动端不溢出、不遮挡。
4. 若需要回滚，仅回退首页视图和资产引用，不影响 API/DB。

## Open Questions

- 首页 CTA 在本 Change 单独实施时，是连接现有登录入口还是等待 `REQ-0002-login-page` 同 Sprint 实施？默认连接既有入口。
