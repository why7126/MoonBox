---
title: Admin Modal Width CSS Cascade
purpose: 管理后台弹窗宽度与滚动治理，预防 CSS 级联覆盖导致弹窗尺寸异常
source: REQ-0004-admin-user-management
status: active
created_at: 2026-08-07 22:21:34
updated_at: 2026-08-07 22:21:34
---

# 管理后台弹窗宽度与 CSS 级联

## 适用范围

适用于管理后台新增、编辑、重置、确认等弹窗，尤其是需要专属宽度、表单较长或低视口滚动的场景。

## 验收 gate

- TSX 或模板实现中不得让通用 `modal-card` 与专属宽度类并存，避免通用样式覆盖业务弹窗宽度。
- 弹窗实现必须在浏览器 computed style 中验收宽度，确认最终宽度与设计预期一致。
- 低视口下弹窗 body 必须可滚动，底部主操作和取消操作必须可访问。
- 弹窗背景遮罩不得吞掉内部滚动，也不得导致页面主体误滚动。
- 必填字段、错误提示和底部操作区不得互相遮挡。

## 落地要求

- `/req-complete` 命中 `admin-modal` 时，必须将 class 并存禁用、computed width 验收和低视口 body scroll 转化为横切 AC。
- `/opsx-apply` 需要用浏览器检查新增/编辑弹窗的实际宽度和低视口滚动行为。

