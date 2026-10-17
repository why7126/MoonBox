---
title: Chat 非空白对话滚动修复追溯
created_at: 2026-10-06 21:29:10
updated_at: 2026-10-12 22:57:00
change_id: fix-chat-workbench-nonempty-page-scroll
bug_id: BUG-0029-chat-workbench-nonempty-page-scroll
related_bug: BUG-0029-chat-workbench-nonempty-page-scroll
iteration: sprint-008
status: applied
execution:
  schema_version: 1
  started_at: 2026-10-07 13:23:54
  completed_at: 2026-10-07 18:22:57
  last_event: opsx.apply
---

# Chat 非空白对话滚动修复追溯

## 来源与状态

来源 BUG-0029-chat-workbench-nonempty-page-scroll，已纳入 sprint-008，根因 confirmed。局部 CSS 修复、双浏览器合成布局回归和本地登录产品 Firefox 真实会话观察完成；正式验收仍由后续验收流程确认。

## 验证记录

2026-10-12 `/opsx-accept` 复验：当前产品 Firefox 1419×832、1440×900 脱敏视觉矩阵与独立发送轮次已补齐；合成 Firefox/Chromium 20 场景回归通过。完整验收清单 `evidence/acceptance/20261012225450951391-49d8f1dd/summary.md` 为 6/6 passed，readiness 为 ready、无 stale；视觉与发送记录见 `evidence/acceptance/current-visual-matrix.md`、`current-product-send.md`。原反馈环境构建来源未逐项比对，验收结论限定当前本地产品。Change 保持 applied，待后续归档授权。

2026-10-12 `/opsx-accept` 首轮：已生成六项计划和完整验收清单，6 项未通过本轮验证，归档尚未就绪。当前 Playwright Firefox 浏览器缺失；产品会话历史最终加载，但“全部”状态搜索 `BUG-0029` 无匹配；当前视觉矩阵与发送轮次证据缺失。证据入口 `evidence/acceptance/20261012222543561929-92bbe2cb/summary.md`。本轮未改变 `applied` 执行事实，也未同步为验收通过。

根因证据来源为目标 BUG root-cause.md E1–E5。2026-10-07：`.chat-message` 增加定位上下文，保留隐藏的角色标签。`src/web/tests/chat-scroll-boundary.cjs` 在 Firefox/Chromium、1419×832/1440×900 的 20 个合成场景通过；页面外层溢出 0 px，消息区可达首尾，输入区可见且可编辑。脱敏截图位于 Git 忽略的 `logs/bug-0029-scroll-boundary/`。`npm run build` 通过。API、DB、部署、安全、客户端生成及数据采集观测均不涉及；仅改变 Chat UI 局部定位，N/A。

本地登录产品 Firefox 1419×832 的长对话有 22 个角色标签。计算样式：`.chat-message` 为 `relative`，角色标签为 `absolute`，`offsetParent` 指向消息卡片。页面 `body.scrollHeight/clientHeight=832/832`，`window.scrollY=0`；`.chat-conversation` 高度 `541/4740`，滚动到底 `scrollTop=4198.5` 时页面仍为 832/832。输入编辑器底边约 711 px，目视无背景露底和遮挡。新建独立测试会话，输入、编辑并发送无敏感内容的测试消息，消息显示且收到“收到”回复；发送后页面仍为 832/832、`scrollY=0`，两张消息卡片为 `relative`。真实会话截图只在浏览器内目视核对，未保存含会话内容的截图。原反馈环境与本地产品构建来源未逐项比对，故不将这一观察表述为原环境复验。

收尾校验：浏览器回归脚本复跑 20 个合成场景通过；`openspec validate fix-chat-workbench-nonempty-page-scroll --strict` 通过；中文标题校验通过 12 份文件；`npm run build --prefix src/web` 通过。全仓 Design System 扫描仍报 178 项既有颜色值和原生控件违规，本次新增的 `position: relative` 不涉及这些项目。已评估 incident 知识库沉淀：本缺陷的定位因果、最小修复和回归边界已经在 BUG root-cause、Change trace 和浏览器测试中完整保留，本次不额外创建重复文档。

## 上轮实施前阻塞检查点（已解除）

以下为前次执行环境的历史记录。本轮已取得源码写入权限并完成局部样式与测试修改；当前未完成项是跨端口认证后的真实会话行为验收。

- 对象：BUG-0029-chat-workbench-nonempty-page-scroll；Change 为 fix-chat-workbench-nonempty-page-scroll；Sprint 为 sprint-008。
- 已验证：根因 confirmed，5 条证据门禁通过；BUG 为 in_sprint，Sprint 同时包含 BUG 和 Change；CLI apply 显示 0/7。
- 硬阻塞：当前执行环境只允许治理目录写入，src 为只读，无法修改 src/web/src/styles/chat-workbench.css 或新增 src/web 内回归测试。没有尝试越过权限限制。
- dry-run 结果：opsx.apply 预演提示先执行 opsx.start；因源码写入权限门禁未通过，未记录正式启动，也未执行完成态同步。
- 剩余任务：全部7项未完成。样式实施和测试新增直接依赖源码写入能力；修复后浏览器回归与交付文档依赖实施完成。现有根因浏览器证据不代表本轮修复前后验收。
- 恢复动作：切换至允许该项目源码写入且具备浏览器测试能力的执行环境，复核当前差异后执行 opsx.start，从任务1.1继续；用户 apply 授权已具备，无需重复请求。
- 本轮未修改业务代码，未勾选任务，未声明修复完成。API、DB、部署、安全与客户端生成边界保持原规划。

## 本次续接复核

实际源码已包含 `.chat-message { position: relative; }`，回归脚本 `src/web/tests/chat-scroll-boundary.cjs` 存在，保留既有实现与4/7任务状态。本轮未重复修改源码。

上次执行该浏览器脚本失败于 browserType.launch：当时 Playwright 所需 Firefox 可执行文件未安装，未进入测试场景。上次访问产品端口18102和18121返回 PermissionError / Operation not permitted。上述环境限制已在本轮解除：浏览器脚本重新运行通过 20 个场景，Firefox 图形界面可访问 18102 的已登录产品并完成长会话与发送观察。

任务2.2和2.3已完成；任务3.2待最终验证与同步。本节记录的是历史续接状态，最终执行状态以 frontmatter 和任务清单为准。
