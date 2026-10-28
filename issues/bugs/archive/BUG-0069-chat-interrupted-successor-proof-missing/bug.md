---
bug_id: BUG-0069-chat-interrupted-successor-proof-missing
created_at: '2026-10-27 16:38:20'
updated_at: 2026-10-27 18:44:32
title: Chat 中断缺少旧同步证明导致外部接续完成后仍受限
status: done
severity: high
owner: 产品团队
lifecycle_stage: archive
related_bug: BUG-0061-cross-entry-continuation-guard-convergence
related_requirement: null
---

# Chat 中断缺少旧同步证明导致外部接续完成后仍受限

复用来源：[BUG-0061的2026-10-27复发材料](../../archive/BUG-0061-cross-entry-continuation-guard-convergence/trace.md)。用户明确授权承接，不继承原历史验收passed或原已归档Change。

## 现象与影响

BUG-0056原Chat轮次已停止，缺少正式同步成功证明；外部接续完成后验收8/8但卡片仍结果待核对，阻断后续动作。严重度high，无已知数据丢失，存在重复执行风险。

## 复现与根因

Chat apply在成功同步证明形成前停止→外部完成同对象交付及有效验收→查看卡片与核验入口。status要求has_sync，recover提前拒绝缺旧清单或direct_sync_missing，verify_successor本身仍要求旧成功清单。详见root-cause.md六条复发证据。已核对两份部署后端核心文件哈希一致。

## 范围及修复方向

仅承接无旧同步证明的已终止apply/modify；保留旧事件和停止状态，验证可信原操作身份/启动基线、后继正式完成收据、对象/版本/绑定/权限、当前验收指纹及并发状态，独立留存后继核验记录后原子解除限制。缺证及冲突继续拒绝。不把旧操作伪装成功，不复用旧BUG通过结果，不包含性能修复，不绕过review/archive专用协议。

## 数据采集与观测

product_data_collection_observability: affected。affected_layers: governance workflow、completion proof、API admission、Web UI、recovery audit。validation: AC-002至AC-007验证脱敏关联、拒绝原因、权限与结果；参照docs/standards/product-data-collection-observability.md。后台核验不伪造用户行为。DB迁移/API结构/客户端生成按新Change设计确定；对象存储和未启用客户端无已确认改动。
