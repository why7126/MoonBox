---
title: 纯 Change 阻塞诊断验证记录
created_at: '2026-10-20 19:20:04'
updated_at: '2026-10-20 19:20:04'
---

# 纯 Change 阻塞诊断验证记录

## 实施与验证结果

输入来源明确补齐 AGENTS.md 和 .gitignore；保留既有 src/scripts/tests、目录指纹及治理事实不回退边界。readiness 增加内部安全诊断，归档准入沿用既有 reason 字符串，卡片无需前端结构或接口 schema 修改。未知错误使用中文待核查提示，ready 原因置空。

聚焦验证74项通过；跨入口归档准入94项通过；最终未知错误兜底增量15项通过。计数对应不同执行批次，不作为互不重叠的总用例数。既有 Starlette 弃用提示不影响结果。

## 真实部署观察

原始样本部署绑定可访问。更新后 AC-001/002/004 误缺失解除，与本地结果一致；AC-006 因 Sprint 输入更新真实 stale。浏览器刷新观察到具体 AC-006 中文原因和 disabled=true，截图见 evidence/deployed-blocked.png。

只执行失效 AC-006 的真实验证命令，7项指纹有效证据复用；完整8项清单通过，执行1次、复用7项、检查器耗时168毫秒。再刷新实际页面，卡片无阻塞文案，完成/归档 disabled=false；最终容器 readiness=ready、stale=[]，admission.ready=true。见 evidence/deployed-ready.png 与 deployment-observation.json。未点击归档执行，不宣称已完成归档。

已目视核对两张截图：红色原因可读、未越过卡片边界，ready 后旧原因清除且按钮恢复。视口1633×836，卡片宽360px、overflow=visible、white-space=normal。此为既有卡片语义验证，无原型复刻或样式变更。

## 部署与回退

只将两个模块叠加到当前本地后端镜像；原镜像保留 before-acceptance-fix 标签。无活动轮次；唯一 unknown 为10月12日历史记录，未改写其状态。保持环境、端口、可信绑定、数据库及其他服务不变。首次直接 Compose 命令缺少脚本派生配置且未启动成功，随后复用 docker-common.sh 环境解析完成 backend 限定更新。模块哈希与本地一致。

## 验收边界

根因、命令测试、真实部署/浏览器分别记录。自动验收计划映射来源 BUG AC-001至AC-005；附件存在与哈希校验不替代上述目视签认。耗时仅报告实测值，Token unavailable。不执行实际归档，不修改旧 manifest。

## 动作入口复核

点击完成/归档后成功进入原对象 Chat，预填 `/opsx-archive optimize-governance-feedback-loop`，发送按钮可用；未发送命令。见 evidence/archive-prepared.png。第一次准备发生409并发事实源变化，验收写入稳定后重试成功；只读对比治理投影与源码治理文件差异为0。该观察证明动作准备可用，不表示真实归档已执行。

## 补充回归与预演

前端既有归档入口、验收证据及缺文档门禁3项聚焦测试通过（134项未选，不计作通过）。首次运行受Node原生localStorage冲突影响，使用 NODE_OPTIONS=--no-experimental-webstorage 后通过；无产品代码变更。两个修复 Change 的独立归档临时副本预演均通过，未实际归档。
