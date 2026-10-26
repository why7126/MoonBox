---
title: 规格末尾空行导致归档历史断链的补证经验
created_at: 2026-10-26 11:28:36
updated_at: 2026-10-26 11:28:36
status: active
source: sprint-013
---

# 规格末尾空行导致归档历史断链的补证经验

## 现象与根因

sprint-013关闭时，3个已归档Change的完整基线证明失败，任务均已完成。根因confirmed：原归档重放结果与历史Git提交仅相差规格文件末尾一个LF，但目录全文哈希不同。独立临时重放精确匹配源记录expected，另一端匹配已完成后继的baseline，排除业务条文变化。

## 证据链

| 证据 | 来源 | 结论 |
|---|---|---|
| 严格关闭预检 | Sprint最终验收报告及修复Change trace | 原有3项基线阻断，不能凭全勾任务关闭 |
| 精确重放与两端目录清单 | `openspec/archive/.spec-normalizations/req-0050-eof-newline.json` | 文件集合不变，正文逐字相同，唯一差异为末尾LF |
| 拒绝路径回归 | repair-archive-newline-proof最终结构化验收 | 正文篡改、缺文件、错误锚点、符号链接及并发变化仍拒绝 |
| 最终闭环 | sprint-013最终验收报告 | 8项Change全部归档，105任务完成，25文件陈旧扫描零阻断 |

## 处理与适用边界

使用独立补证，不覆盖原journal、manifest或正式条文。完整目录清单重算两端哈希，源归档expected与已完成后继baseline双向锚定，再继续原归档链、条文效果和并发复核。只适用于已证明的规格末尾LF差异，不允许忽略全局空白、不把语义相似当作逐字一致，不自动接受格式化或文件增删。

同时修复4处当前验收引用；历史证据中的旧路径原样保留。修复Change的189项联合测试不是全Sprint测试数，也不等于生产部署验证。

## 复用指引

先定位断链两端，再在临时目录重放原操作；无法取得精确结果则继续阻断，不通过手改哈希补链。区分业务验收、恢复准入、当前路径和历史材料，复用[证据分层实践](../best-practices/governance-recovery-archive-evidence.md)。当前算法及保护边界以[验收标准](../../standards/opsx-acceptance.md)为准。

来源：[修复Change](../../../openspec/archive/2026-10-26-repair-archive-newline-proof/trace.md)、[Sprint复盘](../retrospectives/sprint-013-retrospective.md)。本记录不新增运行行为或跟进Issue。
