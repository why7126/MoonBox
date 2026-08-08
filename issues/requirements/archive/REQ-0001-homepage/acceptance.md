---
requirement_id: REQ-0001-homepage
acceptance_status: passed
created_at: 2026-07-30 08:21:16
updated_at: 2026-08-08 23:37:38
---

# 首页验收标准

## 功能 AC

- [ ] AC-001 首页左上角展示 `Logo1-20260728001940.png`，且不使用签名插画代替小尺寸 Logo。
- [ ] AC-002 顶部导航保留右侧 `Open first project` CTA，点击后进入既有登录页入口。
- [ ] AC-003 首屏左侧展示 `AI Native Software Factory`、`Open the box, own a software company` 和既有说明文案。
- [ ] AC-004 首屏左侧展示 `Open MoonBox` CTA，点击后进入与顶部 CTA 相同的登录页入口。
- [ ] AC-005 首屏右侧展示 `image.png`，图片主体清晰可辨，无明显变形、遮挡或过度裁切。
- [ ] AC-006 首页下方保留三项能力摘要：`Agent Workflow`、`Product Knowledge`、`Delivery Harness`。
- [ ] AC-007 除 Logo 与首屏右侧产品视觉外，v1.0.1 首页 Features、Closing、Footer、布局结构和既有交互保持不变。
- [ ] AC-008 首页不出现登录页表单字段、返回首页入口、忘记密码、申请体验或登录页深色遮罩规则。

## UI AC

- [ ] AC-009 首页主背景使用 MoonBox 深色主题基调，主背景接近 `#0A0C1B`。
- [ ] AC-010 CTA 保持金色强调和近直角按钮风格，圆角不超过 `2px`。
- [ ] AC-011 页面不引入蓝紫科技渐变、明亮发光、大圆角卡片或厚重阴影等非 MoonBox 设计语言。
- [ ] AC-012 桌面端首屏维持左文案右产品视觉的双栏结构，移动端允许重排但文本不得溢出或相互遮挡。
- [ ] AC-013 首屏右侧产品视觉每屏仅出现一次，不作为重复图标使用。

## 原型 AC

- [ ] AC-014 `prototype/web/homepage.html` 可独立打开并展示首页首屏、三项能力摘要、Logo 和产品视觉。
- [ ] AC-015 `prototype/web/context.md` 记录首页原型来源、资产、组件、跳转边界和登录页排除范围。
- [ ] AC-016 首页 PNG 截图可后续从 `prototype/web/homepage.html` 导出；当前以用户提供截图和 HTML 原型作为评审依据。

## Knowledge-base 横切检查

本需求为官网首页视觉与入口更新，不涉及管理端 CRUD 列表、管理端表单页、管理端弹窗或媒体上传状态机；未命中 `req-complete` 横切标签，因此不生成 `AC-XCUT-*`。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-08 23:37:38
accepted_by: workflow-sync
source_change: add-homepage-brand-visual
source_sprint: sprint-001
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

