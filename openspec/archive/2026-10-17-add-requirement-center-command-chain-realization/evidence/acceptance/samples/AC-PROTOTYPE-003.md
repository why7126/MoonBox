---
title: AC-PROTOTYPE-003 当前构建视觉矩阵验收证据
created_at: 2026-10-13 08:47:00
updated_at: 2026-10-13 17:55:00
status: passed
---

# AC-PROTOTYPE-003 当前构建视觉矩阵验收证据

- 环境：独立本地验证项目 `moonbox-validation`；Playwright Chromium 使用真实登录、真实 API 和 REQ-9098 卡片，无接口拦截或合成页面。搜索只显示隔离对象。
- 已采集并目视核对：`visual/AC-PROTOTYPE-003/board-{dark,light}-{1440,390,short}.png` 六个看板组合，以及 `drawer-light-{1440,390,short}.png` 三个已加载的文档抽屉组合；同名 `-computed-style.json` 记录看板或抽屉的样式与尺寸，九轮浏览器页面错误数均为 0。
- 目视结论：1440px 深浅主题下标题、统计、搜索与卡片可读；390px 深浅主题下滚动至卡片后动作和文档入口可见，没有发现卡片横向溢出；1440×640 矮视口下卡片与主动作可见。抽屉在 1440px、390px 和矮视口均显示标题、已加载正文、操作区，390px 没有发现抽屉横向溢出。
- 限制：当前隔离服务仍使用启动时的 Web 构建包；本轮 AF-035 源码修复尚未部署到该隔离服务。此组截图只签认看板状态，不能代替修复后 HTML 预览的浏览器复验。
- 未覆盖：计划中的 dialog、loading、error、permission、overflow 等阶段和所有交互结果；AC-PROTOTYPE-003 整项仍待验收。
- 数据边界：只保留过滤后的合成验证对象截图和计算样式，不含原始聊天、凭据、数据库或网络响应。

## 新隔离对象待评审看板复核

- Firefox 在 `127.0.0.1:39032` 登录真实隔离项目，筛选 `REQ-9100-governance-completion-validation` 后，取得 `board-{dark,light}-{1440,390,short}.png` 六张当前产品截图；对象已由产品轮次 `9cb22262-60ba-412f-a9c5-52eeafa617cd` 推进至待评审，卡片提供“发起评审”。
- 新截图的矮视口为 1440×600；上节既有 `-computed-style.json` 来自旧隔离对象、1440×640 等视口，**不与本组截图配对签认**。本组需要重新采样 computed style 与焦点交互，并完成其余阶段矩阵后才能给出视觉整项结论。
- 截图只含合成对象与产品界面，不含聊天正文或真实客户数据。

## 当前新构建补样（2026-10-13）

隔离项目 `REQ-9105` 在真实登录、真实 API、无网络拦截的 1440px 与 390px 页面显示验收中；[截图与计算样式](../visual/AC-007-real-product/computed-style.json)归入 AC-007 的共享证据目录。目视可见 0/3 人工验收、卡片文档入口与窄屏布局；两视口未出现页面横向溢出。该补样为深色看板的验收阶段，不代替本项计划中仍缺的 dialog、loading、error、permission、overflow、浅色与矮视口矩阵，故保持 partial。

## 当前构建真实浏览器补采（2026-10-13）

- 独立验收项目 `REQ-9105`，本地当前 Web 源码与完整隔离 API 配对，使用测试账号真实登录；没有拦截请求。通过产品用户菜单切换深浅主题，在 1440×900、390×844、1440×600 三个视口分别保存[深色 1440 看板](../visual/AC-PROTOTYPE-003-current/board-dark-1440.png)、[浅色 390 看板](../visual/AC-PROTOTYPE-003-current/board-light-390.png)等六张截图及同名计算样式。样式显示两主题分别为深色与浅色，六组 `documentElement.scrollWidth` 等于视口宽度。
- 这组六张截图主要呈现看板外壳；九阶段横向滚动导致目标验收卡片并非每张都在可见画面内，故不替代计划里的完整卡片矩阵，也不替换旧图。
- 打开真实 `requirement.md` 后，补采[浅色 1440 抽屉](../visual/AC-PROTOTYPE-003-current/drawer-light-1440.png)、[浅色 390 抽屉](../visual/AC-PROTOTYPE-003-current/drawer-light-390.png)及矮视口截图和同名样式。抽屉宽度分别为 760、390、760px，三视口无页面横向溢出；截图可见已加载正文，未将短暂的 `Markdown 加载中` 当作完成态。
- dialog、loading、error、permission、overflow 及相应计算样式仍缺；旧构建证据未因新补采自动升级。整项保持 partial，未勾选。

## 当前构建深色弹窗三视口补采（2026-10-13）

- 在同一真实登录的隔离产品中，使用页面“新建 Capture”按钮打开第一步浮层，采集计划入口 [1440](../visual/AC-PROTOTYPE-003/dialog-dark-1440.png)、[390](../visual/AC-PROTOTYPE-003/dialog-dark-390.png)、[矮视口](../visual/AC-PROTOTYPE-003/dialog-dark-short.png)及同名 `-computed-style.json`。视口实际尺寸分别为 1440×1000、390×844、1440×600；计算样式记录深色背景、弹窗矩形和横向溢出检查，三组均无页面横向溢出。
- 矮视口初始画面中底部按钮只露出上缘；向下滚动遮罩层后，[底部按钮可见](../visual/AC-PROTOTYPE-003/dialog-dark-short-scrolled.png)，同名样式文件保留滚动后尺寸。此项仅证明当前浮层可到达，不替代键盘与提交语义检查。
- 目视核对以上截图为当前真实 Capture 浮层。loading、error、permission、overflow 等阶段以及其余交互矩阵仍未完成，整项仍为 partial。

## 当前构建 AI 整理加载态补采（2026-10-13）

- 在独立隔离产品真实提交 Capture 的 AI 整理动作，分别于 [1440](../visual/AC-PROTOTYPE-003/loading-1440.png)、[390](../visual/AC-PROTOTYPE-003/loading-390.png)、[矮视口](../visual/AC-PROTOTYPE-003/loading-short.png)采集加载过程及同名计算样式；矮视口截图已目视确认显示旋转指示器、`AI 正在整理候选...` 与 `running`，没有将整理后的待确认页误标为加载态。
- 这三组仅覆盖真实加载显示。错误、权限、溢出状态及相应视口矩阵仍缺；AC-PROTOTYPE-003 保持 partial，未勾选。

## 当前构建需求中心读取错误态补采（2026-10-13）

- 仅在独立隔离环境暂时停止 API 后刷新真实前端，产品显示“需求中心暂时无法加载”和重试入口；取得 [1440](../visual/AC-PROTOTYPE-003/error-1440.png)、[390](../visual/AC-PROTOTYPE-003/error-390.png)、[矮视口](../visual/AC-PROTOTYPE-003/error-short.png)及同名计算样式。390 页面滚动后采集，使失败提示与操作按钮位于可见区域。三组 `documentScrollWidth` 均等于对应视口宽度；截图已目视核对。
- 隔离 API 随后恢复，`/health` 返回 200。此轮只证明读取错误态的产品视觉；权限态与长内容溢出态仍缺，整项保持 partial。

## 真实权限与长内容溢出矩阵（2026-10-13）

- 权限态：在独立隔离 SQLite 中短暂把验收账号置为 `已冻结`，由真实认证链路返回 403/错误码 1002；需求中心清空对象，详情显示“当前访问权限已失效”。保存 [1440](../visual/AC-PROTOTYPE-003/permission-1440.png)、[390](../visual/AC-PROTOTYPE-003/permission-390.png)、[矮视口](../visual/AC-PROTOTYPE-003/permission-short.png)与同名 `-computed-style.json`。三组计算样式均记录权限文案、弹窗焦点和页面无横向溢出；截图已目视核对。账号随后恢复为 `正常`，隔离看板重新显示原对象。
- 长内容溢出态：仅在隔离副本 `_registry.yaml` 把 `REQ-9106` 标题临时改为 307 字连续测试串，经真实 API 在页面渲染；保存 [1440](../visual/AC-PROTOTYPE-003/overflow-1440.png)、[390](../visual/AC-PROTOTYPE-003/overflow-390.png)、[矮视口](../visual/AC-PROTOTYPE-003/overflow-short.png)和同名样式。窄屏与矮视口另有 `-scrolled.png` 补图，展示滚动后的操作区。三组标题 `overflow-wrap: anywhere`、卡片和标题 `scrollWidth <= clientWidth`、页面 `scrollWidth == clientWidth`；截图已目视核对。窄屏看板本身保留预期的横向阶段滚动。
- 隔离注册表已恢复到原 SHA-256 `5489055ffabd2b8713fb308e5cca671b8e72c4f5542d255f59ae8ce226ba24cd`，被测文档原 SHA-256 `4065e5785424462e3204b9dc1261464fe1bede6d356e92860668112d6a924935` 也已恢复；未把长标题写入主仓库。
- 计划的阶段×视口文件现在齐备；看板与抽屉基线已在下节由当前构建重采。焦点与取消交互仍需按同一构建逐项复核，本项暂不勾选。

## 当前构建看板与文档抽屉基线重采（2026-10-13）

- 通过当前 Web 源码配对的隔离 API、真实登录和页面筛选，重新采集 `REQ-9106` 的 [深色看板](../visual/AC-PROTOTYPE-003/board-dark-1440.png)与[浅色看板](../visual/AC-PROTOTYPE-003/board-light-1440.png)，各含 1440×900、390×844、1440×600 三视口 PNG 和同名 `-computed-style.json`。窄屏滚动到首列后整张卡片、文档入口与动作均可见；两主题三视口均无页面横向溢出。旧基线已被覆盖，不再作为当前证据引用。
- 在 `REQ-9105` 卡片上打开真实 `requirement.md`，等待 Markdown 正文加载完成后重采 [浅色桌面抽屉](../visual/AC-PROTOTYPE-003/drawer-light-1440.png)、[浅色窄屏抽屉](../visual/AC-PROTOTYPE-003/drawer-light-390.png)及矮视口，均有配对 computed style。抽屉宽度依次为 760、390、760px；正文可读且 `documentScrollWidth == documentClientWidth`。
- 本轮目视核对窄屏看板和抽屉，旧图与当前样式不再混配。[焦点与取消交互记录](../visual/AC-PROTOTYPE-003/focus-cancel-interaction.json)显示新建 Capture 打开时焦点在关闭按钮，按 Escape 后浮层关闭，焦点回到“新建 Capture”；未触发提交。八阶段×三视口截图、配对样式和焦点/取消复核齐备，本项按当前构建签认。

## 当前隔离项目的补充权限与长文档截图（2026-10-13）

- 预置查看者 `bob` 登录后，合成对象卡片在 [`1440`](../visual/AC-009-permission-live/viewer-card-1440.png)、[`390`](../visual/AC-009-permission-live/viewer-card-390.png)、[`390×620`](../visual/AC-009-permission-live/viewer-card-390x620.png) 三视口可读；点击“完善需求”得到 [`不可写反馈`](../visual/AC-009-permission-live/viewer-action-denied-390x620.png)。该补图属于权限交互，不替代已签认矩阵中冻结账号的权限态。
- REQ-0027 卡片自身包含 Issue、Change、Sprint 三组长文档入口；看板横向滚动到“验收中”后，保存 [`1440`](../visual/AC-PROTOTYPE-003-overflow-live/req0027-card-1440.png)、[`390`](../visual/AC-PROTOTYPE-003-overflow-live/req0027-card-390-visible.png)、[`390×620`](../visual/AC-PROTOTYPE-003-overflow-live/req0027-card-390x620-visible.png)。矮视口实测卡片为 300×285.7px、页面 `scrollWidth == clientWidth == 390px`，阶段区通过 `.rc-board-wrap` 横向滚动；卡片内容在截图中未裁断。该补图不改变功能 AC 的 2/20 计数。
