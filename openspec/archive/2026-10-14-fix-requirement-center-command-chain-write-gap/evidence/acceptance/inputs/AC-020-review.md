---
title: "共享产品运行构建与治理应用复验"
created_at: 2026-10-14 10:03:00
updated_at: 2026-10-14 14:40:00
---

# 共享产品运行构建与治理应用复验

结论：通过。当前构建、历史入口 DOM 与既有自动应用事实已闭环；单项验收 `20261014143738272820-64f73d0b` 中 AC-020 为 passed。

指定端口已按用户确认改为 `localhost:39002`。共享 Web 容器原入口引用旧 `index-DkadcIt4.js`，已在 `/private/tmp` 保存入口和 bundle 备份，并同步当前 `src/web/dist` 的 `index-zZOrD37_.js`。容器与本机 SHA256 均为 `3719119dc4dc09d67343b1d4df818cbb7a4842bb8412430093fb31dcc9290465`；真实浏览器 39002 登录页亦加载该 bundle。容器 bundle 中“待应用成果”“查看成果”“审阅治理成果”“确认应用”四词均为 0。

共享产品后端只读数据库已有 BUG-0037、BUG-0038、REQ-0045 的 generate candidate/application `applied/verified` 记录；对应事实源回读见 Issue acceptance.md 既有真实产品轮次。隔离新构建 BUG-1001 和 BUG-1002 亦完成自动应用与事实源回写。

用户已在 Chrome `localhost:39002` 登录。当前产品 Chat 页实际加载 `/assets/index-zZOrD37_.js`；可见按钮与 dialog 的 DOM 中上述四类治理面板文案为 0。当前账号显示“平台超级管理员 / AI原生软件工厂”，Chat 提示“当前空间尚未配置仓库”，本地项目未连接，新会话和发送均禁用。历史入口切至“全部”后仍显示 0 个会话，无法打开已有 Generate 会话。截图见 `AC-020-shared-unbound-history.png`。空间设置页仅显示当前空间 `moonbox`，集成配置项为预留状态；管理后台空间列表只有 `moonbox` 一个空间，无现成的已绑定空间可切换。

恢复前诊断：空历史页没有被当作历史 Generate 会话的无面板证据。共享产品治理数据与空间绑定均未修改；所需 1440×900 截图与 computed style 已在下述恢复轮次补采。

部署排查：共享 `moonbox-backend` 原运行容器未注入 `MOONBOX_CHAT_REPOSITORIES` 与 `MOONBOX_CHAT_REPOSITORY_BINDINGS`，而本机 `.env` 的仓库 ID、空间 ID、源仓库目录与运行根均已设置，`bash scripts/docker-up.sh self-storage-sqlite --chat-platform --check` 通过。现有 30 个 Chat 会话与 7 个治理应用记录均属于当前登录账号、当前空间和 `moonbox` 仓库；因此产品空历史是运行态仓库绑定缺失造成的可见性阻塞，不是数据库无记录。

## 配置恢复后的真实产品轮次

经用户授权，运行 `bash scripts/docker-up.sh self-storage-sqlite --chat-platform`；后端、Web、Chat worker、治理控制器均健康，后端已注入上述两项仓库绑定。共享数据库与空间绑定未修改。部署前镜像 ID 已记录，生成的本机 dist 已备份到临时目录，可回滚。

当前 Web 容器、本机 `src/web/dist` 与 Chrome `localhost:39002/chat` 均引用 `/assets/index-evpnFHfi.js`。容器与本机 JS SHA256 均为 `30ff6825590c713ad77f21c686868a8ee59294915901aea4d2ff381687302a65`；运行 bundle 与本机 dist 的全部 JS 中四个禁用文案字面串均为 0。构建 ID 带随机值，本轮同步的是实际部署产物。

仓库恢复后，Chat 显示 `moonbox · 已连接`，历史筛选“全部”可见 24 个会话。通过产品历史入口打开 `BUG-0036-bug · 生成 Bug`，会话 `f44e9702-bd35-4ad4-8626-2b2ca3191d05`，保留两次旧 `/bug-generate` 输出及校验失败提示。1440×900 当前 DOM 有 2 条助手消息、0 个 dialog、0 个禁用文案按钮，页面可见文本中四个禁用文案均为 0；助手消息与 `.chat-message-history` 宽度均为 1168px。证据为 `AC-020-当前产品场景-1440x900.png` 与同名 `-style.json`。旧候选未被误触发应用。

共享数据库的 BUG-0037 generate application `ae1dadf5-b3b5-4cc3-8c61-1d0659858af1` 与 REQ-0045 generate application `cabd516b-16a3-485c-9c6a-a6615b3aba09` 均为 `applied/verified`，此前产品轮次已回读事实源。独立数据源 BUG-1001、BUG-1002 亦由产品 Generate 自动应用并回读 bug.md、trace、registry、CHANGELOG，详见 `AC-015-review.md`。共享项目旧 BUG-0037、REQ-0045 验收夹具已被同编号业务对象覆盖，本轮未在共享源重放写入，也未把旧会话当作当前文件状态证据。
