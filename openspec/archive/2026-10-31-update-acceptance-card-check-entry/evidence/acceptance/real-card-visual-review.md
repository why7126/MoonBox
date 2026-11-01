---
title: 验收卡片真实界面验证
created_at: '2026-11-01 00:23:47'
updated_at: '2026-11-01 00:23:47'
---

# 验收卡片真实界面验证

## 环境与样本边界
用户于本次apply明确选择隔离测试样本。使用当前源码生产构建、真实FastAPI路由与SQLite测试库、真实登录与项目授权；服务别名req58-isolated-local，端口39029，仅本机。样本为合成事项，不是正式交付；未修改正式REQ/BUG/Change状态造样本。未使用浏览器fetch拦截、DOM注入或静态截图模拟页面。
原本地服务39002可访问，刷新后验收列0项；此前短暂显示的是归档前缓存，不纳入通过证据。隔离验证不冒称原部署当前存在验收中样本。

## 逐项视觉签认
| 组合 | 证据 | 结果 |
|---|---|---|
| 验收中·1440×1100·独立/来源卡 | isolated-1440.png、isolated-1440-style.json | 通过，完整两卡；无检查整行、无占位，文档进度和红框外阻塞提示保留 |
| 验收中·390×1100·独立卡 | isolated-390-standalone.png、isolated-390-style.json | 通过，卡宽266px，横向看板滚至目标后完整展示 |
| 验收中·390×1100·来源卡 | isolated-390-source.png、isolated-390-style.json | 通过，纵向滚动后完整卡片；原横向看板和侧栏行为保留 |

两个视口目标selector acceptance-check、acceptance-readiness数量均0，dialog数量0。桌面两卡高度248.96/263.71px，窄屏270.15/280.21px；padding 15px 16px 18px、font-size 13px、gap 0、overflow visible。DOM子节点从文档直接进入原阻塞提示/进度，没有替代空行。标题/标签/文档按既有布局换行。原型是删除范围契约，不要求合成示例的文字、人力和数据值与截图完全相同。

## 原有操作流程
isolated-existing-rework.png：点击返修进入原Chat并预填精确opsx-modify命令，无归档准备弹窗、未发送消息或调用模型。
isolated-existing-check.png和txt：点击检查迭代归档条件后返回真实未完成对象原因，归档保持禁用，目标检查行依然0。旧自动验收按钮保持禁用。失败重试由单元测试独立覆盖，不冒充真实网络故障观察。

## 分层证据
5项前端回归覆盖摘要刷新、轮询、迭代检查失败重试、既有来源交付确认和卡片行为；生产build/TypeScript通过。旧撤回弹窗骨架完全不参与本轮验收。AC-PROTOTYPE-001采用用户明确的局部删除决定，无新骨架确认项。
