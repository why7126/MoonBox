---
created_at: '2026-10-22'
title: 兼容追加证明契约 v1
updated_at: '2026-10-23 21:07:37'
---

# 兼容追加证明契约 v1

## 支持范围

模块与 Requirement 标题组成身份。解析后的原要求正文与所有原 Scenario 文本必须逐字保留，仅新增唯一命名的 WHEN/THEN 场景。重复身份、删除、重命名、原文改写、未知结构及没有新增场景均拒绝。结构通过不等于语义通过：还需绑定同一原文/新文哈希的审查、矛盾检查和回归证明；任何一项缺失不放行。

证明保存于 openspec/archive/.compatible-successors/后继身份/条文摘要.json，schema_version 为 1。绑定 successor、capability、requirement、before_sha256、after_sha256、added_scenarios、delta_sha256、acceptance_sha256 及 review/regression 附件 SHA-256。原归档 journal、manifest、执行时间和历史哈希均不修改。

## 生产与消费

使用 scripts/record-compatible-successor.py 的 predecessor、successor、capability、requirement、review、regression 参数发布证据。前置对象必须唯一且已归档；后继可以是待归档候选或唯一已完成归档。候选必须有当前有效验收证据；候选证明不构成已完成归档事实。文件发布采用原子无覆盖写入；相同内容可重复核验，不同内容拒绝覆盖。

审查文件包含身份绑定、status=passed、reviewer、rationale、contradictions=[]。回归文件包含同样身份绑定及 original_contract、added_scenarios、destructive_changes、broken_chain、concurrent_change 检查记录。生产者需先执行相关回归和逐条审查，不允许从愿望生成通过结论。读取端不执行证据内命令，不以模型意见单独放行。

消费时逐边检查完整归档链、当前有效保护视图、原有验收附件、增量和语义证据；终点核对最新规格效果，再复读全部引用证据。旧版本记录沿用既有独立条文路径，不具有隐式同条文放行权限。关联证据随 Change 归档后仅按唯一已完成身份解析新位置，仍验证原字节哈希。路径越界、符号链接和未知 schema 拒绝。

## 写入前预检与已合并恢复

未合并候选在共享准入及 CLI 写入边界检查受影响历史对象。已完成合并的 move-only 恢复先验证历史 journal、交付和后继链，不将它重新解释为一个拟议改写；不会重放规格合并。预检错误不降低独立人工签署、权限及范围完成门禁。

## 当前规格演进阻断

本 Change 修改「归档连续证明的条文冲突范围」原正文，属于显式规则替代，不能用此兼容追加机制证明。用户已明确选择保留归档阻断，显式替代另行处理。本次按兼容追加范围交付和验收，不加入当前 Change ID 白名单，不自动创建后续 Issue。

## 2026-10-23 验收反馈调整（当前策略）

取消后继写入前兼容证明硬性限制：产品预检、CLI 和归档执行不再要求独立兼容或规则替代证明；已完成后继仍核验正常验收、唯一身份、连续归档哈希链、交付增量、最终规格效果和并发变化。历史 journal、manifest 与证明保留，不自动归档或代替独立签署。

本节取代前文将兼容证明作为硬门禁的描述；证明工具保留为可选审查工具。
