---
title: 独立 Change 创建时自动分级与卡片只读展示业务流程
requirement_id: REQ-0059-standalone-change-auto-classification
created_at: '2026-11-01 00:25:42'
updated_at: '2026-11-01 00:57:00'
---

# 独立 Change 创建时自动分级与卡片只读展示业务流程

## 主流程
创建独立 Change → 解析来源 → 有来源则继承来源分级；无来源则识别类型 → Agent 阅读材料并评估 → 校验枚举及理由 → 原子持久化 → 卡片只读投影。

## 类型与评估契约
本次检查的 change_index.py 卡片 type 表示对象类型 change，并非修复类型，不可复用为 fix 判定。建议新增 trace.change_type，取 fix 或 non_fix；这是待实现契约，不是已有字段。新建时明确写入；历史缺字段仅按完整 fix- 前缀兼容。显式类型与前缀冲突时待核实，禁止直接改级。

建议 trace.classification 保存 state、dimension、rationale、evidence_refs、evaluated_at、evaluated_by；state 为 assessed 或 pending，dimension 为 severity 或 priority。当前等级仍保存顶层 severity/priority，与既有读取契约兼容。独立 fix 的旧 priority 仅作历史，不能映射 severity。后续 OpenSpec 可调整存储形状，但不可改变业务含义。

## 异常与重试
信息不足 → 自主补证 → 仍不足则返回待补充状态及缺口，不宣称创建评估完成。来源不可见、解析错误 → 不视为独立对象。已有合法评估重试 → 返回原结果，不追加审计或更新时间。版本冲突 → 重新读取并重新评估，禁止覆盖。写入失败 → 保留旧事实，不展示成功。

## 旧接口与维护边界
现有 ChangePriorityEditor 调用 PUT /api/v1/requirement-center/changes/{change_id}/priority，服务端经 enqueue_priority 异步提交，并记录 requirement_center.priority_save。卡片移除组件及调用；本期不直接删除服务端接口，以兼容旧客户端，但不能让该接口修改 fix 的当前分级：fix 返回明确类型不匹配且不入队，其他独立活动 Change 保留权限、维护窗口、版本及审计检查。来源转换或归档后拒绝独立修改。后续治理重评支持正确维度，不能借普通 Markdown 编辑绕过保护。实施前复核全部调用者与排队操作，已有操作落盘时再次验证类型和来源。

## 历史策略及父需求差异
父需求允许卡片编辑并仅用 priority；本需求改为创建时评估，fix 增加 severity，卡片只读。非 fix 历史合法 priority 可展示；fix 缺 severity 显示严重性待评估；不批量修改归档。审批、Sprint、开发与归档流程不因本需求自动推进。

## 实施一致性核对

2026-11-01 核对本文件与实现一致：创建Agent评估，完成门禁校验；卡片只读按维度展示；来源和历史保留。证据见 Change `update-standalone-change-auto-classification/evidence/acceptance/implementation-review.md`。无数据库迁移、部署拓扑调整或新增权限。
