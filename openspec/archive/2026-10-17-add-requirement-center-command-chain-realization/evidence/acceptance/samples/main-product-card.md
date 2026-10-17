---
title: REQ-0027 主产品卡片核对诊断
created_at: 2026-10-13 18:24:00
status: blocked
---

# REQ-0027 主产品卡片核对诊断

- 主产品入口：本机 `127.0.0.1:39002/requirements`；Firefox 已登录平台管理员，当前空间显示“AI原生软件工厂”。页面刷新后提示“当前空间尚未绑定本地项目”，治理对象为 0，另有“更新失败”提示；[当前页面截图](../visual/main-product-card/main-space-unbound.png)。当前页面不存在 REQ-0027 卡片，因此不能确认其已显示 2/20。
- 容器只读核对：`moonbox-backend` 已运行，`/app/governance/issues`、`openspec`、`iterations`、`rules`、`docs` 分别挂载到当前仓库对应目录。挂载存在不等于当前空间已经关联该项目，不能以容器文件或隔离副本卡片代替主产品 UI 结果。
- 仓库事实：当前 `issues/requirements/review/REQ-0027-requirement-center-command-chain-realization/acceptance.md` 的功能项 AC-018、AC-020 为 `[x]`，共 2/20；其余未勾选。隔离产品 `127.0.0.1:39039` 的 REQ-0027 卡片显示 0/20，是较早复制的隔离项目文件，不代表主产品当前计数。
- 恢复条件：主产品当前空间应绑定当前项目并成功刷新；届时直接核对 REQ-0027 卡片计数、文档入口及项目标识。此诊断不变更主产品空间绑定或数据。

## 2026-10-13 复核

- Firefox 重新读取主产品 `127.0.0.1:39002/requirements`：仍是“当前空间尚未绑定本地项目”与更新失败；空间切换列表只有当前“AI原生软件工厂”，没有已绑定的替代空间。REQ-0027 卡片仍不存在，不能宣称主产品已显示 2/20。
- 仅把当前仓库的 REQ-0027 `acceptance.md` 同步到独立隔离项目的对应文件后刷新隔离产品，真实页面的 [REQ-0027 卡片](../visual/main-product-card/isolated-card-2-of-20.png)显示“验收 2/20”，且 `Help` 说明计数来自 Issue `acceptance.md`，自动验收结果未计入。这证明隔离产品的卡片投影按已勾选事实更新；不等于主产品空间已绑定。
