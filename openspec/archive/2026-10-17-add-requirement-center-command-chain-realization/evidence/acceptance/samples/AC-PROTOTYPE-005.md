---
title: AC-PROTOTYPE-005 浮层交互命令回归样本
created_at: 2026-10-13 15:00:00
updated_at: 2026-10-13 18:34:00
status: passed
---

# AC-PROTOTYPE-005 浮层交互命令回归样本

## 2026-10-17 整项复验与签认

结论：通过。逐一目视复核已归档的 12 组 Capture 阶段×视口截图及其同名 computed style：1440 与 390 的打开、内部点击、外部关闭、嵌套取消、提交后关闭和焦点返回均与场景一致。提交后关闭图片显示界面当时有刷新失败提示；只采用确认任务 completed、Issue 关联与随后弹窗关闭的独立事实，不把截图中的刷新状态当作提交成功证明。两个确认任务和完整 ID 见下文。

在当前隔离产品 `39029` 的已登录 Chrome 页面复查：Capture 打开后焦点位于关闭按钮；点击原始材料输入区仍保持弹窗；点击删除草稿打开顶层确认弹窗，取消只关闭确认弹窗且焦点回到外层“删除草稿”；关闭 Capture 后焦点回到“新建 Capture”。未执行删除。原有 [Tab 记录](../visual/AC-PROTOTYPE-005/tab-focus-1440.json)、[嵌套 Tab 记录](../visual/AC-PROTOTYPE-005/nested-tab-1440.json)和 Escape、遮罩关闭记录共同覆盖焦点约束与返回。文档抽屉的内部点击、遮罩/Escape 关闭与触发器焦点返回见下文的前后对照；Agent 助手浮层内部、Escape、外部关闭由聚焦 UI 回归覆盖。卡片的“发起评审”实测导航到 Chat 工作台，属于页面导航而非浮层，不纳入浮层关闭矩阵。

运行中关闭不取消任务采用 [AC-013 真实浏览器关窗轮次](AC-013.md)：同一 `REQ-9300` 产品轮次关窗后仍在运行，重新进入后保留原 turn ID；该场景与两个已完成 Capture 确认任务分开记录。故此项签认仅针对已实现的 Capture、嵌套确认、文档抽屉及 Agent 助手浮层，不扩展到不存在的其他弹窗类型。

以下为 2026-10-13 的增量采集记录；各段当时的 partial 与“仍缺”是历史状态，最终结论以本页 2026-10-17 整项复验为准。需求中心当时的聚焦前端测试 122/122 通过，其中含 Agent 助手浮层交互回归。

## 当前构建抽屉交互补查（2026-10-13）

在已登录的独立隔离需求中心，以 `REQ-9105` 的 `requirement.md` 按钮打开真实文档抽屉。点击抽屉标题后 `role=dialog` 仍存在；点击外部蒙层后抽屉关闭；再次打开后按 Escape 也关闭。首次观察外部关闭后焦点落在 `BODY`，Escape 后落在用户菜单，[返修前焦点记录](../visual/AC-PROTOTYPE-005-current/drawer-escape-focus.json)和[关闭后截图](../visual/AC-PROTOTYPE-005-current/drawer-after-escape.png)可复核。

在当前 Change 范围内修复文档抽屉触发器焦点记录与关闭后恢复。聚焦前端测试 1 passed、121 skipped，Web 生产构建通过；HMR 后再次使用真实隔离产品依次验证 Escape 与蒙层关闭，两个动作都把可访问性焦点返回 `requirement.md` 按钮，[返修后焦点记录](../visual/AC-PROTOTYPE-005-current/drawer-focus-return-after-fix.json)和[关闭后截图](../visual/AC-PROTOTYPE-005-current/drawer-focus-return-after-fix.png)可复核。其他 modal、取消、提交关闭、Tab 约束和 1440/390 完整证据矩阵仍待采集，AC-PROTOTYPE-005 保持 partial、未勾选。

另在当前真实页面的新建 Capture 浮层补采[1440px 打开状态](../visual/AC-PROTOTYPE-005-current/capture-open-1440.png)和[390px 打开状态](../visual/AC-PROTOTYPE-005-current/capture-open-390.png)，同名 JSON 记录视口、浮层宽高及页面溢出。390px 点击原始材料输入区后浮层仍在，[内部点击截图](../visual/AC-PROTOTYPE-005-current/capture-inside-click-390.png)可复核；点击外部区域会关闭。首次外部关闭焦点落在 BODY，返修后外部区域和 Escape 关闭均回到“新建 Capture”按钮；[焦点记录](../visual/AC-PROTOTYPE-005-current/capture-focus-return-after-fix.json)及[截图](../visual/AC-PROTOTYPE-005-current/capture-focus-return-after-fix.png)保留脱敏结果。两个聚焦前端测试通过、121 skipped；完整取消、提交后关闭和 Tab 约束仍缺，不能签认整项。

2026-10-13 在真实隔离产品深色主题补入计划规定的 [modal-open 1440](../visual/AC-PROTOTYPE-005/modal-open-1440.png) 与 [modal-open 390](../visual/AC-PROTOTYPE-005/modal-open-390.png) 截图及同名计算样式；这两对文件与 AC-PROTOTYPE-003 的深色弹窗同轮采集，是共享场景的副本，不是新增独立轮次。其余 10 个阶段×视口组合和提交后关闭语义仍缺，整项保持 partial。

## 当前构建内部点击、外部关闭与 Tab 返修（2026-10-13）

- 在真实隔离项目的深色 Capture 浮层补采 [1440 内部点击](../visual/AC-PROTOTYPE-005/inside-click-1440.png)、[390 内部点击](../visual/AC-PROTOTYPE-005/inside-click-390.png)、[1440 外部关闭](../visual/AC-PROTOTYPE-005/outside-click-1440.png)、[390 外部关闭](../visual/AC-PROTOTYPE-005/outside-click-390.png)；同名计算样式记录 dialog 可见性、视口和横向溢出。内部点击保持打开，遮罩点击关闭，两个视口无横向溢出。
- 返修前产品观察：浮层打开后焦点仍在“新建 Capture”触发按钮，首次 Tab 跳到背景统计按钮，违反焦点约束。AF-043 在 CaptureDialog 挂载时将焦点移到关闭按钮，并把 Tab 边界限制在最上层弹窗。当前产品 HMR 后再次打开，首次 Tab 进入“来源材料”，连续四次 Tab 均留在浮层，最后回到关闭按钮；[焦点路径](../visual/AC-PROTOTYPE-005/tab-focus-1440.json)保留脱敏结果。
- Escape 后 [1440 焦点返回截图](../visual/AC-PROTOTYPE-005/focus-return-1440.png) 与同名计算样式显示弹窗已关闭、焦点回到“新建 Capture”；390 外部关闭的 [焦点返回截图](../visual/AC-PROTOTYPE-005/focus-return-390.png) 与同名样式同样确认。聚焦前端测试 1 passed。
- 随后对“删除当前草稿？”嵌套弹窗复验，发现其初始焦点也留在外层“删除草稿”按钮；AF-043 补上最上层嵌套弹窗的初始焦点、Tab 循环与取消后返回外层触发器。当前产品的 [1440 取消前](../visual/AC-PROTOTYPE-005/cancel-before-1440.png)、[取消后](../visual/AC-PROTOTYPE-005/cancel-1440.png)、[390 取消前](../visual/AC-PROTOTYPE-005/cancel-before-390.png)、[取消后](../visual/AC-PROTOTYPE-005/cancel-390.png)及同名计算样式表明：取消只关闭嵌套弹窗，外层仍在，焦点回到“删除草稿”。[1440 焦点循环](../visual/AC-PROTOTYPE-005/nested-tab-1440.json)记录关闭→取消→删除草稿→关闭三次 Tab 全在顶层弹窗。
- 隔离 SQLite 在取消前后均只有同一草稿 `2084b919-c512-4252-bde2-eb343eeac9b4`，revision 1、state `editing`、更新时间未变，确认任务数 0；未执行删除。两项聚焦焦点测试通过。`submitted-close` 双视口及其他动作族仍待验收，整项保持 partial，不勾选。

## 提交后关闭补采（2026-10-13）

- 为隔离项目的两个合成 Capture 分别在 1440 与 390 视口执行真实确认。1440 的确认任务 `92f58918-8be6-4e07-90ba-9266d338a2bc` 于 10:40:07 UTC 完成，关联 `REQ-9106-capture`；390 的确认任务 `8f9f0a02-2429-4d39-9868-507858f1e3f3` 于 10:41:51 UTC 完成，关联 `REQ-9107-capture`。确认任务状态与 Issue 关联来自隔离 SQLite 只读查询，不保存提交正文。
- 完成后关闭浮层分别采集 [1440](../visual/AC-PROTOTYPE-005/submitted-close-1440.png) 和 [390](../visual/AC-PROTOTYPE-005/submitted-close-390.png) 及同名计算样式：浮层隐藏且焦点回到“新建 Capture”。两次关闭分别约在 10:40:15 和 10:41:57 UTC，均晚于任务完成；只能证明关闭结果反馈没有撤销已完成提交，不能代替“运行中关闭不取消任务”的证据。
- 计划的 12 个阶段×视口截图和计算样式已具备文件，但其他浮层动作族、运行中关闭语义及各组合的最终目视签认尚未完成；整项仍为 partial，不勾选。
