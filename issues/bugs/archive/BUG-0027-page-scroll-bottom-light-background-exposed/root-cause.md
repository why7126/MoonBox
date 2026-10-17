---
bug_id: BUG-0027-page-scroll-bottom-light-background-exposed
title: 页面向上滑动时底部露出浅色背景根因分析
status: confirmed
created_at: 2026-10-04 23:36:44
updated_at: 2026-10-04 23:36:44
owner: 产品团队
---

# 页面向上滑动时底部露出浅色背景根因分析

## 根因状态

status: confirmed

## 现象

页面向上滑动或触发宿主外层 overscroll 后，深色主界面底部露出大面积浅色背景。用户截图显示深色输入区下方出现浅色区域，右下角悬浮元素位于浅色区域上方，说明露出的不是 Chat 内容区自身背景，而是更外层的页面或宿主背景。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | screenshot | `screenshots/page-scroll-bottom-light-background-exposed.png` | 用户截图显示深色 Chat 界面下方露出大面积浅色背景 | 证明用户可见现象存在，且浅色区域位于深色页面壳之外 |
| E2 | computed_style | `logs/chat-page-computed-style.json` | Playwright 访问本地产品 Chat 壳，`body.backgroundColor=rgb(244, 246, 250)`，`[data-testid=chat-shell].backgroundColor=rgb(10, 13, 20)` | 证明产品页面存在浅色 body 背景与深色 Chat 根容器背景不一致；外层暴露时会显示浅色 |
| E3 | computed_style | `logs/chat-page-computed-style.json` | `html` 与 `#root` 背景为透明，`body` 是 scrolling element，`[data-testid=chat-shell]` 高度为 920px 且 `overflow: hidden` | 证明深色主题没有覆盖到浏览器滚动根层，外层滚动或宿主弹性滚动会落到 body 背景 |
| E4 | code_path | `src/web/src/styles/globals.css` `body` 与 `.requirement-center` 样式 | `body` 使用 `background: var(--mb-background)`；`.requirement-center` 才设置 `background: var(--rc-bg)` | 证明浅色 body 与深色业务页面壳来自样式作用域差异 |
| E5 | code_path | `src/web/src/pages/catalog/ChatWorkbenchPage.tsx` | Chat 页面将 `data-theme={theme}` 挂在 `<main className="requirement-center theme-${theme} chat-shell">` 上 | 证明深色 token 只在 Chat 根容器及其子树生效，未同步到 `html/body/#root` |
| E6 | code_path | `src/web/src/styles/chat-workbench.css` `.chat-shell` | `.chat-shell` 使用 `height: 100dvh; overflow: hidden` | 证明 Chat 壳按视口高度绘制且内部隐藏溢出，无法覆盖宿主 overscroll 暴露出的根层背景 |

## 已排除假设

| 假设 | 排除证据 |
|---|---|
| 浅色区域来自 Chat 内容区或输入框自身背景 | E2 显示 Chat 根容器背景为深色，`.chat-composer` 也位于深色面板内；浅色来自更外层 body |
| 深色主题已经覆盖整个页面根层，只是某个子组件高度不足 | E2、E3 显示 `html` / `#root` 透明、`body` 为浅色，深色只在 `[data-testid=chat-shell]` 层 |
| 这是纯粹截图误差，无法从产品页面复核 | E2、E3 为本地产品页面 computed style 证据，能复核背景层级差异 |
| 根因在后端接口或数据加载失败 | 现象发生在页面背景和滚动边界；E2-E6 均指向前端页面壳样式作用域，与 API 数据无关 |

## 已确认根因

深色主题只作用于 MoonBox Chat 页面根容器 `.requirement-center.chat-shell`，没有同步覆盖浏览器根层 `html`、`body` 和 `#root`。同时 `body` 默认背景仍是浅色主题色 `#F4F6FA`，`html` 与 `#root` 背景透明。

因此，当用户向上滑动触发宿主 WebView、浏览器或外层页面的 overscroll / 弹性滚动，或者根容器绘制边界之外被短暂暴露时，实际露出的就是浅色 `body` 背景，而不是 Chat 页面深色背景。

## 修复方向

- 在 Chat / 需求中心等深色工作台页面挂载时，同步让 `html`、`body` 或 `#root` 使用当前工作台背景色，避免宿主 overscroll 暴露浅色层。
- 或为产品工作台路由设置稳定的全局页面类，例如 `body.moonbox-workbench-dark`，进入工作台时设置深色背景，离开时恢复。
- 继续保持 `.chat-shell` / `.requirement-center` 自身深色背景，避免内部布局变化时出现透明穿透。
- 需要覆盖深浅主题切换，确认浅色主题下不会被错误设置为深色。

## 验证闭环

修复后需要验证：

- 1440px 桌面视口访问 `/chat`，`body`、`#root`、`[data-testid=chat-shell]` 背景在深色主题下均不暴露浅色。
- 在页面内向上滑动或触发外层 overscroll，不出现截图中的浅色底部区域。
- 切换浅色主题后，body/root 背景与浅色工作台背景一致。
- `/requirement-center` 等复用 `.requirement-center` 的页面不发生主题背景回归。
