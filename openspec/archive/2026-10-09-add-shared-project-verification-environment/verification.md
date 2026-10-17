---
title: 跨空间项目验证环境阶段验证记录
created_at: '2026-10-08 23:30:00'
updated_at: '2026-10-08 23:30:00'
---

# 跨空间项目验证环境阶段验证记录

## 已验证事实

- 2026-10-09 在用户明确授权外部 npm 后，以独立准备网络从锁文件安装 Linux arm64 真实依赖制品，环境键为 `19b5d6ccd8841a44bdfee50ab424093f82cccab8ff0a8ede2e92b7871852c5ee`。完整性复核通过；同一锁文件与工具链的第二项目复用只读制品；切换 amd64 后缓存未命中。准备容器无凭证并禁用项目安装脚本。
- 已校验制品只读挂载到当前 runner，Firefox/Chromium 在 MoonBox 公开页面各执行双视口点击、刷新、可见性及样式断言，通过。与未挂制品的先前烟测分开记录。
- 隔离端到端探针使用独立 SQLite、合成用户/两个空间、同仓库双绑定及另一个独立 Git Web 项目。三项任务均经平台 API 预检、幂等创建、worker 领取与执行、结果查询和受权截图读取通过：`space-a/shared/firefox`、`space-b/shared/chromium`、`space-b/independent/firefox`。任务 ID 分别为 `1cb01e01-6272-4cb7-8ad7-7e573e0fea6e`、`f9f7d419-e7b6-4178-8975-177400560e3e`、`722f1beb-4cf6-4a94-9e74-6ed6ce3239b0`；跨用户查询返回 404。预检目标可达性在探针中由宿主机 DNS 限制而替代，真实浏览器目标访问未替代；随后在同一隔离探针中让前两项任务经两个执行槽并发运行，真实浏览器执行重叠 7.35 秒；第三个独立项目任务随后通过。并发任务 ID 为 `bfeb595e-62ea-4655-be0c-dc0cbbf1ef91`、`d6dfd9d7-a044-43a0-b645-4ef1e4b1c763`，独立项目任务 ID 为 `b9f1bd42-2a9f-4041-bc2e-d26f5ae1ea0b`。相同环境键并发准备只发布一个制品的测试通过。
- 一次性 MySQL 8.4 空库中 `migrate` 连续执行两次成功，`verification_tasks` 表、唯一约束及队列/空间索引存在；合成任务写入和读取通过。测试容器停止后自动删除；未连接业务数据库。
- BUG-0030 使用当前 Web 源码的独立 Vite 构建，真实 Firefox/Chromium 配合合成 API 各完成 16 个视口/状态/阶段场景并保留 16 张截图，覆盖 1440/390、unknown/stopped/failed/completed、刷新重进、轨迹切换与 computed style 无横向溢出。Firefox `1440-unknown-open.png` SHA256 为 `3b067252ce0e85f2bae1deb21885abec8d71c235de46113884b8190f016cd7a3`，Chromium 为 `49c6071faacd894dfb5c76f0fba7ce1eb49f8e2ed29527a816dee263bf07493c`；证据在忽略的私有运行目录。已目视核对 Firefox 1440/390 截图：部分正文与未知警告均可见。浏览器用例曾因 Vite Host 拦截和对隐藏 DOM 的测试断言错误失败，已使用网关 IP 并修正测试断言后按原业务期望复跑通过。详细边界同步至 BUG-0030 Change 的 `verification.md`。
- 已登录的本地历史会话只读观察：BUG-0030 对话当前有 9 个正文气泡，刷新后仍为 9 个且每条长度保持一致；轨迹切换隐藏对话视图，切回后正文仍为 9 个。1440px 首条助手列 computed style 为 flex、宽 1126px、scrollWidth/clientWidth 均 1126；390px 时宽 252px、scrollWidth/clientWidth 均 252。未保存真实会话正文或截图。历史被删除的故障 T1/T2 未复验。

- 固定 Playwright 1.62.1 runner 镜像已构建；加入声明式交互步骤后的当前镜像 ID 为 `sha256:118e028382478f1d1c3e58c8af5acae7c5e23fc9b688117fe8ea3d72081a6898`，旧镜像 ID 为 `sha256:b6edba153695b3177872a3130d25fb292770dc6ccdd0ca8cbfb11135f9678b77`；构建探针返回 Node 24.18.1、pnpm 11.2.2、Firefox 153.0、Chromium 151.0.7922.34。部署时须改用当前镜像 ID，环境身份因镜像变化而失效重算。
- 真实 Docker 浏览器访问本地 MoonBox 公开落地页，在 1440×900 和 390×844 视口完成截图及 `body` computed style 采样。Chromium 两张截图的 SHA256 为 `2d99c7047b5dc7ed9c9b296508784a57cb7efc09b492a7921d1c475b43f5910a`、`eef0513f6d4afa2e67c853e45aecf10890e5a1a5c7c169ff7199b314b2d4825f`；Firefox 为 `b210bf73195d01f0180d7d41a19f8815c489bd1009ea7650f08bd65675d6e216`、`d2d96ba26c789ce909fb0acdda5ba7ad797ce344da119ab1be2ac0a31a4be71e`。图片存于忽略的私有运行目录，不入库。
- 同一 runner 访问另一独立静态 Web 样例，双浏览器、双视口截图和 `#sample` computed style 采样通过。四张截图的 SHA256 依次为 Chromium `6651a49f6e522f1f29b758d313a041f99147040b936fcf8c305f891daadd4892`、`94c8d5f883fc21f637356e7ad3edbccd6ca51ce841b437104e11eb925ab89960`，Firefox `f233a43e98edd09f45dd7ffb462e8fb2e2d2a9faa8bf46f94bc43ffb16239bee`、`3734b880b9f8fce955aba337f367c98b3db20b96c1bb07d42b0d0c99352e5a3d`。该样例未经过平台任务 API 与依赖准备链路。
- 浏览器容器只读根文件系统下需要临时 HOME/XDG 缓存；Firefox 页面进程在 128 pids 限额下崩溃，调整为 256 后双视口运行通过。上述修正已纳入运行器配置。
- 2026-10-09 使用当前 runner 对 MoonBox 公开落地页执行「点击开启 MoonBox → 确认登录表单可见 → 刷新 → 再次确认登录表单可见」真实交互，Firefox/Chromium 均在 1440×900、390×844 通过，每视口 6 项断言。Firefox 截图 SHA256 为 `e15196ca6143efea53e885eec52d7d6b804c41d02dea512f0f83ea7391b68609`、`db87834e257520bbfd85663d53504212e970aeb3861f75b180c26424d2cf17d4`；Chromium 为 `8d7d70580dc4a9766be8bb5316b5599fe97c7edaaee8a0a842616b83337e8592`、`55ef14ae9fa84eae3411fcf984c3f8172ad26f2083b6103e0acf99ac18d6fe22`。已目视核对 Firefox 桌面截图为登录表单；此项仍不是 BUG-0030 对话验收。该独立运行器调用未挂项目依赖制品，制品消费路径待端到端验证。
- 定向后端测试通过，包含身份变化、恶意网络输入、项目绑定撤销、磁盘容量不足及 SQLite/MySQL 任务表与索引 DDL 编译；一次性 MySQL 8.4 实机迁移已执行。基础 Compose 与 Chat 平台叠加的 verification profile 配置解析通过；前端 TypeScript 构建通过；OpenSpec strict、当前 Change 中文与标题校验通过。

## 尚未通过的门禁

- 外部 npm 已由用户于 2026-10-09 明确授权并完成真实制品准备。此前自动审批拒绝的那次操作未绕过；本次为新授权后的执行。
- 两空间及独立项目链路已在合成账号与独立数据库中验证，真实 MySQL 迁移已在一次性空库验证；生产部署与长期负载容量仍需单独验证；本地双执行槽重叠已验证。
- BUG-0030 的真实浏览器合成 API 场景和已登录历史会话只读观察已分别记录；原故障 T1/T2 数据已删除，无法做同一实例复验。合成 API 视觉通过不代表真实未知轮次再次发生，也不等于 BUG Change 的全部 AC 已完成。
- 本地已验证旧镜像身份与新镜像身份隔离，切回新镜像后制品校验通过；生产回滚和长期运行仍须部署时演练。交付文档与最终校验结果见下文。

## 交付校验

- 平台验证定向后端测试 22 项通过；真实 Firefox/Chromium 的双空间并发任务和 BUG-0030 合成 API 浏览器用例分别通过。MySQL 8.4 一次性空库迁移、幂等迁移与合成任务往返通过。
- OpenSpec strict、当前 Change 中文和标题、产品数据采集与链路观测、Change 身份、测试框架、环境文件忽略策略及 `git diff --check` 通过。API 全仓标准校验发现既有 `capture_drafts.py:53` 的 `image` 路由缺少 `response_model`；该文件不属于 REQ-0044 改动范围，作为独立存量告警记录，不更改其接口契约。
- 安全校验覆盖跨用户读取 404、绑定撤销、恶意输入、无凭证准备容器、只读制品和无 Docker socket 的运行隔离；生产网络与长期资源压力需在部署验收中复核。
