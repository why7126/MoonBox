---
requirement_id: REQ-0056-requirement-center-change-delivery-cards
title: 需求中心交付阶段按 Change 独立成卡原型拆解与视觉契约
created_at: '2026-10-29 18:38:41'
updated_at: '2026-10-29 18:55:21'
---

# 需求中心交付阶段按 Change 独立成卡原型拆解与视觉契约

## 参考事实源与范围

本轮用户要求按照 cards-minimal-change-v2.png 更新 HTML。该图为本轮卡片视觉事实源，优先于上一版四列、大标题原型。业务边界仍由 requirement.md 定义；当前产品 renderIssueCard 和 rc-card 样式作为结构与设计系统参照。历史截图仅用于说明原多Change聚合问题。

保真模式为参考图卡片结构复刻、既有产品局部一致；不是重做产品布局。使用浅灰蓝底、细描边、左侧REQ金色/BUG红色色条、11px基础圆角、等宽斜体身份、Sprint描边标签、彩色元信息、金色文档链接和底部文字动作。

## 页面与组件拆解

默认三列：研发中、验收中、已完成；每列一张卡，与图一致。无大标题、指标区或前期需求区。原型演示选项在底部默认折叠，不挤占参考构图。前期Issue、多来源、独立Change等功能仍在PRD/AC范围，本次参考画面不展示这些样本，不能据此删除实现范围。

卡片层级：Issue编号及Sprint → 完整Change ID → 中文交付标题 → 元信息标签 → Issue/Change/Sprint三组文档 → 当前交付状态/进度 → 更新时间及文字动作。每张卡仅一个Change文档组，来源文档明确标Issue。历史子交付保留自身Sprint，并说明整体需求仍有未交付范围。

## 页面状态与数据依赖

所有内容为本地合成示例，零网络、零持久化，不读取真实文档，不执行治理命令。默认全部迭代以同时显示三张参考卡；底部筛选分别测试sprint-014/015/016及空列。统计按Change和来源去重，筛选当前迭代以Change归属为准。示例任务数与时间不是当前产品事实。

| 动作 | 浮层 | selector | 状态/边界 | 后续验收证据 |
|---|---|---|---|---|
| 来源编号 | 右侧dialog抽屉 | .issue-id[data-action=source] | 需求整体范围、partial；受限态待正式API | 来源权限与整体范围截图 |
| 中文标题/查看交付 | 同一抽屉 | .title-button / [data-action=delivery] | 归档只读摘要 | 归档与父需求分层 |
| 文档链接 | 同一抽屉 | [data-action=document][data-source][data-document] | 显示对象归属，非真实内容 | URL与对象绑定 |
| 研发/测试/查看进度 | 同一抽屉 | [data-action=tasks] | 对应Change与章节，示例任务只读 | 版本/权限/迟到响应 |
| 验收进度/查看验收 | 同一抽屉 | [data-action=acceptance] | 不使用Issue整体验收计数 | 验收事实与缺证据态 |
| 核对阶段目标 | 抽屉内演示 | #prepare | 仅回显目标，无执行 | 后续真实预填/会话恢复 |
| 关闭 | 关闭按钮/Esc/遮罩 | #close / #detail | 返回触发器焦点 | 键盘与外部点击 |
| Sprint筛选 | 原生select | #sprint-filter | 筛选、计数、空列 | 归属与去重 |

多来源选择、loading/error/permission-hidden/任务写入是后续产品验收范围，本参考画面不伪造已经覆盖。所有正式selector需在Change设计阶段映射至真实组件。

## 样式采样与响应式

默认参考画布2068×760，1800以上按参考图放大字号/间距；1440基准三列紧凑卡片。1000以下保留340px列宽并在board横向滚动，390视口不挤压长ID；抽屉宽度最大560px且不超视口，高度100dvh内部滚动。长ID换行，浅色模式与参考一致，本轮不声称覆盖深色产品。

采样 .board/.card/.card-top/.change-id/.tags/.docs/.progress/.footer/#detail：font-size、line-height、padding、gap、border、radius、background、color、width、overflow及层级。CSS声明可静态核对，不等于浏览器computed style。列头、卡片、动作及浮层、窄屏分批视觉验收，仍归后续Change evidence。

## 本轮检查与限制

HTML脚本语法与模拟DOM检查通过：默认3卡、关联需求去重为1、缺陷为1、各Sprint筛选1卡、任务绑定当前Change、BUG文档归属、归档只读、零网络。此为合成逻辑验证，不是浏览器点击、渲染或可访问性通过。

此前浏览器安全策略拒绝本地file协议，本轮不绕过该限制；未取得截图或computed style。cards-minimal-change-v2.png是生成的设计稿，不是HTML截图。HTML视觉还原度、真实点击、焦点陷阱及产品API需在允许的预览环境验证。UI Skeleton、1440视觉和REQ最终一致性门禁仍pending。
