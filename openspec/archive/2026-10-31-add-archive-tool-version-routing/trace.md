---
title: 变更初始状态记录
change_id: add-archive-tool-version-routing
status: applied
iteration: sprint-017
created_at: 2026-10-31 07:53:40
updated_at: 2026-10-31 11:18:14
execution:
  schema_version: 1
  started_at: 2026-10-31 11:04:00
  completed_at: 2026-10-31 11:18:14
  last_event: opsx.apply
---
# 变更初始状态记录

## 登记说明
本记录时间为状态登记时间，不代表原提案创建或历史执行时间。

## 核实范围
原始创建会话和授权来源未确认。本轮仅登记提案，不代表批准实施。现有任务全未勾选；归档驱动仍从 project.root/scripts 取工具，定向检索未发现独立工具包根、manifest 路由实现，因此未取得该方案已实施的证据。保留原 ID、现有提案与任务，不补造执行时间、不纳入本轮功能开发。

## Sprint 规划登记

本轮用户通过 `/sprint-propose --change add-archive-tool-version-routing` 授权纳入 sprint-017。估算XL、8人天；Sprint合计19/30人天，缓冲11人天。原核实范围为初始登记历史，本次追加规划不改变历史执行事实；status仍为proposed，started_at与completed_at保持空值，尚未执行开发、部署或归档。规划事实见 [Sprint](../../../iterations/change/sprint-017/sprint.md)。


## 入口检查与实施范围

当前用户授权本Change实现、验证与自动验收，不授权部署或正式归档。Sprint-017包含当前Change，opsx.start已成功；前次opsx.apply dry-run要求启动/全勾属于顺序检查，未作为外部阻塞。

| 入口 | 事实源与工作区 | 正向及拒绝验证 | 对应验收 |
|---|---|---|---|
| CLI | 固定配置、manifest；cwd为业务根 | 旧模式及Shell解释器链、包漂移拒绝 | AC-ROUTE、AC-COMPAT |
| 产品归档 | 原operation manifest / input_hash | 原身份及fence保留、版本缺证拒绝 | AC-RECOVERY |
| Worker/子容器 | 服务包与daemon宿主映射 | 实际启动前摘要核验、执行器缺失不领取 | AC-CONTAINER |
| 历史与占用 | 合成历史文件及unknown占用 | 验证前后哈希不变 | AC-CONTAINER |
| UI/公开API | 未改界面或响应schema | 不适用；无需截图、Orval或迁移 | AC-GOVERNANCE |

横切门禁：Tags/Refs、AC-XCUT、knowledge_base_refs、best-practices均不适用；纯后端与治理工具路由，无UI或prototype；准入通过。

## 验证记录

已完成120项定向回归（归档权限、跨入口准入、新包校验、恢复绑定、Shell解释器），另有容器Worker回归3项通过、6项显式环境探针跳过；跳过项不冒称通过。本轮单独运行真实Docker验证覆盖CLI/服务驱动/生产子容器启动，使用合成业务事实，无模型调用和真实对象归档。

真实容器证据：`evidence/container-routing.json`。临时run de1b323c858c443eb283aa07b0bd7d44 已cleanup并check：容器0、网络0、clean。前两次样本启动失败由临时HOME目录缺失导致，修正后复验通过；不更改生产配置。

入口问题及修复：Shell夹具未模拟新增路由，初次114通过/3失败，修正后Shell 7项通过；Sprint校验器实际使用位置参数，按help修正后通过。目录校验仅报告既有legacy SQLite路径warning，未删除数据。其他工作区改动保留。


## 最终验证摘要

自动验收5/5通过：AC-ROUTE、AC-COMPAT、AC-RECOVERY、AC-CONTAINER、AC-GOVERNANCE。最新证据入口为 `evidence/acceptance/20261031111739567955-bd854ead/summary.md`；本轮4项执行、1项有效复用，无失败或待采集。测试组合231项通过；另有Worker测试3通过、6个需额外显式环境的旧探针跳过，本次真实Docker独立验证通过，不把跳过用例计为通过。

最终增量修复：Workflow Sync包导入兼容；受控版本绑定采用rt1前缀防止侧文件丢失后降级；未知嵌套同名目录继续参与历史指纹。真实容器证据按最终代码刷新，校验器重新计算完整包清单验证有效。原authority与fence通过新旧模式参数化测试核对。

已通过Shell语法、diff空白、中文与OpenSpec结构、Sprint scope、目录结构、上下文预算、产品观测声明及本轮observed行为轨迹校验。没有API响应、数据库schema、UI或客户端生成变更；部署配置契约和环境规则已同步，未安装配置、未部署或归档。临时Docker最终cleanup/check为clean（0容器/0网络）。


## 收尾结果

opsx.apply与opsx.accept串行同步成功，tasks为10/10；证据readiness为ready，临时副本归档预演通过，共享archive-readiness返回ready。未执行正式归档或部署。

AI Usage：apply为estimated_fallback（缺token_count），accept Hook为actual且无warning；治理调用计时885秒，但缺整个调用精确Token边界，治理收益不作实测声明。执行链路复盘为warning：仅遗留SQLite目录提示和用量口径不完整；失败已在本次范围自修，未自动创建Issue/Change。前次提前结束归类为已有连续执行契约的执行遗漏，不追加重复规范。
