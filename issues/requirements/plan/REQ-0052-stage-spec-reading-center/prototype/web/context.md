---
requirement_id: REQ-0052-stage-spec-reading-center
title: 九阶段流转规范查阅与研发规范中心原型说明
created_at: '2026-10-23 09:38:16'
updated_at: '2026-10-23 09:38:16'
---

# 九阶段流转规范查阅与研发规范中心原型说明

## 定位与边界

prototype.html 是独立交互草图，所有内容为虚构 Mock，不连接 API、不执行治理命令。无用户提供的参考稿，不是既有页面一对一复刻。PNG 本阶段暂不要求，待实现阶段输出真实产品截图；当前 readiness 为 Partially Ready，不能宣称视觉通过。

## 页面与组件拆解

| 页面 | 区域与层级 | 数据依赖 | 1440px 焦点 |
|---|---|---|---|
| 阶段规范 | 导航 → 九阶段卡 → 阅读抽屉 → 摘要/原文 | 阶段映射、对象类型、版本、权限 | 九列横滚、标题与入口密度、抽屉宽度 |
| 规范中心 | 导航 → 搜索/分类 → 目录 → 原文 | 清单、过滤结果、正文 | 两栏比例、正文行宽、表格滚动 |
| 迭代日志 | 导航 → 日志条目 → 详情 | 时间、原因、版本引用 | 元信息与正文层次、缺失提示 |

状态矩阵：default/loading/empty/error/permission-denied/stale/history-missing；原型状态选择器演示这些状态，真实状态由 API 决定。搜索原型仅过滤本地示例标题；正文搜索、真实授权、版本冲突由后续实现与验收覆盖。

响应式：≥1000px 双栏；600–999px 缩窄目录；<600px 单栏，抽屉占满视口。九阶段横向滚动，不强压列宽。支持系统深色主题。样式采样 font-size、line-height、padding、gap、border、background、width、overflow、z-index。

## 动作与选择器

| 动作 | 容器 | selector | 状态与证据 |
|---|---|---|---|
| 流转规范 | dialog | .stage-open / #reader | 开关、键盘、焦点返回；后续截图与交互断言 |
| 完整原文 | dialog 内阅读区 | #original | 摘要切换；同版本验证由真实 API 验收 |
| 规范中心/日志 | 页内 | [data-view] | 切换、筛选、空态；截图 |
| 关闭 | dialog | #close | Escape/遮罩/按钮，焦点返回 |

## 来源与后续

设计复用 src/web/src/styles/tokens.generated.css 和 Button.tsx 的细线、近直角原则。实现阶段使用正式组件与 token，当前独立 HTML 仅表达布局意图。后续设计需要绑定项目标识、规范标识、相对路径、章节、内容指纹、可用提交版本、工作区脏状态、生效证据及读取权限。
