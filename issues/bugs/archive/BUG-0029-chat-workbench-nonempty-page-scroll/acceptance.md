---
bug_id: BUG-0029-chat-workbench-nonempty-page-scroll
title: Chat 工作台非空白对话出现页面级滚动条及底部布局异常验收标准
acceptance_status: passed
owner: 产品团队
created_at: 2026-10-05 23:22:51
updated_at: 2026-10-17 16:45:28
---

# Chat 工作台非空白对话出现页面级滚动条及底部布局异常验收标准

## 验收范围与前置条件

已实施局部样式修复，以项目 CSS 和合成消息在 Firefox、Chromium 完成浏览器布局回归，并在已登录的本地产品 Firefox 会话复验长对话、空白会话、短会话及发送。2026-10-12 的当前产品逐 AC 验收通过；原反馈环境与本地产品的构建来源仍未逐项比对。

## 回归验收项

以下复选框是需求中心的验收进度来源。2026-10-12 已在当前本地产品完成正式逐 AC 验收；下表保留实施阶段的历史结果，当前验收结论以本节后续的本轮验收记录为准。

- [x] AC-001：非空白对话滚动到底后页面外层无异常垂直滚动。
- [x] AC-002：长内容在消息容器内独立滚动，首尾可达且外层稳定。
- [x] AC-003：消息滚动后输入区可见、可聚焦、可编辑且无遮挡。
- [x] AC-004：工作台底部背景和悬浮元素无露底、重叠或截断。
- [x] AC-005：空白与非空白对话切换及约定视口下滚动边界稳定。
- [x] AC-006：授权测试会话发送消息后正常显示且不重新触发布局异常。

| 编号 | 场景与操作 | 通过标准 | 证据要求 | 当前结果 |
|---|---|---|---|---|
| AC-001 | 非空白对话加载并滚动到消息底部 | 页面外层不产生异常垂直滚动；标准桌面视口下页面 scrollHeight 与 clientHeight 差不超过 1 CSS px，页面 scrollTop 不因消息区滚动而变化 | 页面及消息容器滚动尺寸、前后截图 | 合成双浏览器通过；本地产品 Firefox 长对话通过 |
| AC-002 | 长内容与多条消息超出消息可视区 | 消息容器能够独立滚动到首尾，内容完整可达，外层保持稳定 | selector、scrollTop/scrollHeight/clientHeight、首尾截图 | 合成双浏览器通过；本地产品 Firefox 底部通过 |
| AC-003 | 消息滚动前后及底部检查输入区 | 输入区可见、不被遮挡、不被裁切；可聚焦和编辑测试文本，未发送前可清除 | 输入区边界、computed style、交互观察 | 合成通过；本地产品 Firefox 输入编辑通过 |
| AC-004 | 检查工作台底部背景和悬浮元素 | 无异常露底、重叠、截断或脱离预期容器；具体基准先由视觉对照明确 | 标注对照图、元素 selector 和样式 | 合成截图通过；本地产品 Firefox 目视通过 |
| AC-005 | 同环境切换空白与非空白对话，再调整至已约定视口 | 两类场景均遵守滚动边界，切换后不遗留外层滚动偏移 | 场景矩阵及各场景测量结果 | 合成双浏览器四视口矩阵通过；本地产品 Firefox 长短切换通过 |
| AC-006 | 在授权测试会话发送一条无敏感内容的测试消息 | 发送和显示正常，新增消息不重新触发异常；当前无证据表明发送已损坏，此项仅作回归保护 | 测试动作及脱敏结果摘要 | 本地产品 Firefox 发送、显示及回复通过 |

## 验收记录要求

每项记录时间、版本、环境、动作、实际值、结论和证据引用。自动化断言与真实浏览器观察分别记录，不能用合成测试结果替代视觉和交互观察。失败项说明偏差；未执行项保持待执行。没有截图、computed style 和因果验证时不判定整体通过。

## 完成门禁

当前根因 confirmed。2026-10-12 的逐 AC 证据包已通过且 readiness 为 ready；正式验收状态由 `opsx.accept` Workflow Sync 投影。

## 本轮实施证据（2026-10-07）

- 修复：`src/web/src/styles/chat-workbench.css` 的 `.chat-message` 增加 `position: relative`；角色标签仍是视觉隐藏的 `strong`，浏览器测得 `position: absolute` 且 `offsetParent.className=chat-message`。
- 基线：修复前 Firefox 1419×832 长对话 `body.scrollHeight=2021`、`clientHeight=832`，见 root-cause.md E1–E5。
- 回归：`node src/web/tests/chat-scroll-boundary.cjs`，Firefox 与 Chromium 的 1419×832、1440×900，共 20 个合成场景通过；各场景外层溢出 0 px、`window.scrollY=0`。长对话 `.chat-conversation` 溢出 Firefox 3232/3164 px、Chromium 3235/3167 px，滚动至首尾后外层仍为 0；输入区边界留在视口内，可编辑测试草稿。
- 脱敏截图：Git 忽略的 `logs/bug-0029-scroll-boundary/{firefox,chromium}-{1419x832,1440x900}-{top,bottom}.png`。截图仅含合成消息，不能代替登录产品视觉验收。
- 真实产品观察：2026-10-07，本地登录产品 Firefox 1419×832 长对话有 22 个角色标签，`.chat-message` 计算样式为 `position: relative`，标签为 `absolute` 且 `offsetParent` 为对应消息卡片。`body.scrollHeight=clientHeight=832`，`window.scrollY=0`；`.chat-conversation` 为唯一纵向滚动容器，`clientHeight=541`、`scrollHeight=4740`，滚动到底 `scrollTop=4198.5`，页面仍为 832/832。输入编辑器位于视口内，底部约 711 px；目视无背景露底或输入框遮挡。切换至新会话并发送一条无敏感内容的测试消息，消息显示且助手回复“收到”；发送后的 2 张消息卡片仍为 `position: relative`，页面 832/832、`scrollY=0`。真实会话截图仅在浏览器内目视核对，未保存含会话内容的截图。
- 证据边界：Firefox 的真实产品观察补充了 1419×832 的长短会话和发送证据；1440×900 及 Chromium 结果来自使用项目 CSS 的合成浏览器矩阵。隔离开发版跨端口认证重定向 `/login`，未搬运凭据；未声称原反馈环境已复验。

## 2026-10-12 当前产品逐 AC 验收

完整运行 `20261012225450951391-49d8f1dd`：6 项 passed、0 项 failed、0 项 blocked、0 项 reused；[证据包](../../../../openspec/archive/2026-10-12-fix-chat-workbench-nonempty-page-scroll/evidence/acceptance/20261012225450951391-49d8f1dd/summary.md)与 [脱敏视觉矩阵](../../../../openspec/archive/2026-10-12-fix-chat-workbench-nonempty-page-scroll/evidence/acceptance/current-visual-matrix.md)、[发送轮次记录](../../../../openspec/archive/2026-10-12-fix-chat-workbench-nonempty-page-scroll/evidence/acceptance/current-product-send.md)分别提供命令、图片、尺寸与产品终态。

| AC | 结论 | 当前产品证据 |
|---|---|---|
| AC-001 | passed | 1419×832、1440×900 外层高度等于视口，滚动后 `scrollY=0`。 |
| AC-002 | passed | 1419×832 长对话消息区首尾 `scrollTop=0/1719.5`，首尾脱敏截图。 |
| AC-003 | passed | 滚动后输入区在视口内，测试草稿可编辑且已清除。 |
| AC-004 | passed | 两视口底部背景、输入区和悬浮元素目视无露底、重叠、截断。 |
| AC-005 | passed | 空白、长对话、发送后短会话切换；当前产品截图与合成双浏览器 20 场景矩阵。 |
| AC-006 | passed | 独立测试 turn 为 `completed`、用户与助手消息各 1 条；发送后两张卡片为 `relative`，页面 832/832。 |

边界：当前产品本地 v0.1.0 验收通过；原反馈环境构建来源未逐项比对。截图中的产品消息文字已脱敏，未保存消息正文或原始事件。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-17 16:45:28
accepted_by: workflow-sync
source_change: fix-chat-workbench-nonempty-page-scroll
source_sprint: sprint-008
evidence: [openspec/archive/2026-10-12-fix-chat-workbench-nonempty-page-scroll/evidence/acceptance/20261012225450951391-49d8f1dd/summary.md]
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```
