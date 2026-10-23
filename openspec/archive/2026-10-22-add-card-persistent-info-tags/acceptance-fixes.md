---
title: 卡片标签验收返修台账
created_at: 2026-10-22 18:52:00
updated_at: 2026-10-22 19:20:00
---

# 卡片标签验收返修台账

## 2026-10-22 标签一致性及人天分档

状态：返修实施及验证完成，待自动验收同步。保留canonical applied和首次完成时间。用户明确确认S≤1、M≤3、L≤5、XL≤10、XXL>10，显示“M · 3人天”，颜色沿用探索建议。属于原标签展示边界，无API/DB变化。

## 附件截图逐项视觉对照表

| 编号 | 页面/状态 | 对照对象 | 期望 | 实际与偏差 | 检查方式 | 处置 | 证据入口 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | /requirements，桌面浅色，验收/已完成卡片 | 同卡等级、负责人 | 共用字体、10px字号、1.2行高、3px 8px内边距、20px圆角，无描边 | 新标签覆盖12px并加1px描边；“开发 3 人天”较长 | 本会话真实Chrome截图与CSS规则对照 | 本次修复 | 旧证据product/local-done-document.png；globals.css rc-tag与末尾规则 |
| R2 | /requirements，1440×900及390×844，双主题 | ui阶段矩阵及原型 | 档位与精确值并列，五档区分；根因仍可点击且焦点可见 | 旧原型12px与用户最新要求冲突，尚无档位 | 新computed style、截图及边界测试 | 以本次用户要求覆盖原型旧规则 | 后续repair目录 |

## 局部视觉契约

所有标签共享rc-card-tags > .rc-tag样式：字体、字号、行高、padding、radius及border一致。根因按钮使用状态色、cursor和focus-visible表达交互，不增加描边。人天为只读span，S青/M蓝/L紫/XL橙/XXL玫红，浅底深字与深色主题对应色，title显示档位与预估值。顺序和共享抽屉动作族不变。

## 验证计划

覆盖0、1、3、5、10及各上界之后小数、非法数值；九阶段×双视口×双主题重新截图，采样新旧标签属性一致性；Enter/Space/Escape和焦点回归继续验证。真实本地Web重建后观察实际3/5/8/13人天卡片。原视觉截图保留历史，不作为本次样式签认。

## 验证与子文档一致性扫尾

专项Vitest 22通过，覆盖11个档位边界/小数、7类非法值、原三项标签行为及九阶段页面请求回归。九阶段×双视口×双主题36张当前截图在evidence/acceptance/repair/；computed-styles.json逐行对照六项样式全部相同，所有行不溢出。12组根因Space打开、Escape关闭、焦点回归及2px可见outline均通过，详见keyboard.json和drawer截图。桌面浅色M档、手机深色XXL档目视确认：同排尺寸一致，长行自然换行；手机保留横向看板。旧ui截图不再作为当前样式证据。

已更新requirement、business-flow、user-stories、acceptance、prototype HTML/context及Change design/spec。REQ trace由Workflow Sync维护；capture/review是历史决策记录，无需改写。Sprint验收报告和release-note、产品手册已同步。原API/DB/安全/采集/客户端类型不变，无需重新生成客户端；本轮只需Web构建部署。旧product证据仅保留数据、权限和生命周期事实，标签新样式以repair为准。

OpenSpec strict、中文校验、Mintlify校验及Web TypeScript/Vite构建通过。根因按钮动作族未改变，新增样式不改变共享抽屉权限或事件传播。

## 真实部署复验

本次Web镜像TypeScript/Vite构建及重启成功，bundle index-D7f8a3c8.js。业务聚合接口一度发生504，日志证实upstream timed out；在既有授权内重启API后页面恢复，实际卡片出现M · 3人天、L · 5人天、XL · 8人天、XXL · 13人天。未改超时配置或业务数据，不将恢复操作归因于样式逻辑。证据repair/local-observation.json、local-business-tags.png。

同一Web镜像产物另通过临时真实FastAPI与专用测试数据库验证，已完成样本显示S · 0.5人天（repair/isolated-real-http.png），无网络Mock。三类证据明确分列：Mock视觉矩阵、隔离真实HTTP、现有业务部署；不声明执行过正式归档。

## 第二轮：分隔点固定间距

状态：研发中，仅调整展示。沿用前轮及本轮explore实际页面证据，确认CardInfoTags文本中点两侧普通空格在等宽字体下显宽。

| 编号 | 页面/状态 | 对照对象 | 期望 | 实际偏差 | 检查方式 | 处置 | 证据入口 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R3 | /requirements桌面浅色，已完成及验收卡片 | 前轮repair截图与当前Chrome显示 | 中点左右各2px，无普通空格 | JSX使用空格分隔，内部留白偏大 | 源码与截图确认；返修后computed style和几何采样 | 独立separator span并设margin-inline:2px | repair/local-business-tags.png；本轮spacing目录 |

局部视觉契约：人天标签保持原共享字号、字体、外侧padding、圆角和颜色。内部中点使用.rc-effort-separator左右2px外边距，无额外gap或文本空格；数字与人天相连。根因及抽屉动作不变。本轮不修改API、DB、权限、采集或客户端类型。


### 第二轮验证与一致性扫尾

- 状态：实现与定向复验完成；等待本轮自动验收门禁。
- R3 处置：已移除可见文本中的普通空格；分隔点独立 span，margin-inline 为 2px。36 个阶段×视口×主题组合均通过，计算样式左右各 2px，文本无空格，标签行无溢出，旧标签共享尺寸保持不变。
- 12 个键盘场景通过：2px 焦点提示、Space 打开根因、Escape 关闭；见 `evidence/acceptance/spacing/keyboard.json` 与 drawer 截图。
- 22 项 Web 定向测试通过；Docker Web 已重建并重启。当前产物 index-Dh8ZUJtI.js 在隔离真实 HTTP API + 专用测试 SQLite 中实测 S·0.5人天左右各 2px；见 spacing/local-observation.json 与 isolated-real-http.png。
- 视觉矩阵使用真实生产组件与明确 Mock API；隔离真实 HTTP 样本无 API Mock。此前 product 数据/权限证据仅复用未变的后端行为，不代表当前样式；此前本地业务 API 间歇性超时不据此宣称修复。
- REQ 子文档一致性扫尾：requirement.md、业务流程、用户故事、acceptance.md、prototype/context.md 与 HTML 已同步紧凑格式和固定间距。trace.md 由 Workflow Sync 更新；capture/review 保留历史决策，无需更新。Change design/spec、Sprint 验收/发布说明及公开手册同步。
- API、DB、部署配置、安全、客户端生成无需同步：仅 Web 标签内部排版调整，无契约或边界变化。product_data_collection_observability: N/A；affected_layers: Web UI；validation: 定向测试、computed style 与真实 HTTP 样本。
