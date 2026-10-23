---
requirement_id: REQ-0050-controlled-rule-replacement-proof
title: 规则修改说明与安全归档原型交互契约
created_at: '2026-10-22 13:11:21'
updated_at: '2026-10-23 20:55:00'
---

# 规则修改说明与安全归档原型交互契约

## 定位与事实源

`prototype.html` 仅演示对象归档阻断项、规则差异抽屉和重新检查；不发请求、不作权限或归档判断。事实源顺序为本版 `requirement.md`、`acceptance.md`、本契约、HTML、现有 Chat 页面与设计 token。正式页面复用 Chat 壳、对象会话、Composer 和主题；无常驻治理按钮，旧确认弹窗退场。

## 页面结构与状态

只有相关对象的归档诊断出现规则修改时展示“查看修改”。抽屉按“原规则、修改后、修改理由、仍禁止、受影响验收、归档检查”排列，提供“重新检查归档”和关闭动作。无确认、拒绝、撤销动作。状态包括待检查、验收未签署、版本变化、权限不足、加载失败、结果未知、可继续与已归档。关闭抽屉保留 Chat 会话、草稿和附件。

## 动作按钮矩阵

| 动作 / 位置 | 类型 | selector | 状态 | 验收证据 |
|---|---|---|---|---|
| 查看修改 / 对象阻断项 | drawer | `rule-change-open`, `rule-change-drawer` | 显示、加载、错误、无权 | 页面、差异和焦点归还 |
| 展开差异 / 抽屉 | inline-expanded | `rule-change-diff` | 折叠、展开、长文本 | 1440/390 换行 |
| 重新检查归档 / 抽屉 | read-only refresh | `rule-change-recheck` | 加载、阻断、可继续、结果未知 | 只刷新诊断，不发送、不归档 |
| 返回 Chat / 抽屉 | close | `rule-change-close` | 默认、焦点恢复 | 草稿与附件保留 |

旧 `rule-change-confirm/reject/revoke/dialog` 在正式页面均不存在；旧 API 新写入被拒绝，旧记录只读。用户不靠点击查看或刷新获得批准。

## 视觉与组件契约

1440×900：保留 Chat 壳，抽屉最大宽 720px，差异两列。390×844：抽屉全宽，差异单列，内容区滚动、操作区不遮挡、无页面横向滚动。沿用深浅主题、Inter/Noto Sans SC、细边框、8px 以内圆角。采样 `rule-change-drawer/diff/recheck` 字体、行高、宽度、间距、颜色、层级和 overflow。新旧两版截图分开标记，旧确认弹窗截图不能充当新版视觉证据。

## Mock / API 边界

原型中的状态切换只是结构示意。正式 API 必须读取当前未归档对象的差异和现行验收/归档门禁；查看或刷新不能写入批准事件。旧版确认历史只读，旧版新写入入口拒绝；不能通过 Mock 判定真实权限、并发或归档成功。
