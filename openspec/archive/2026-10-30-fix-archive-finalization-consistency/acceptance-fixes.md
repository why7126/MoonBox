---
title: 归档收尾验收返修台账
created_at: 2026-10-30 09:12:20
updated_at: 2026-10-30 09:12:20
---

# 归档收尾验收返修台账

## 批次一：路径误报与当前文案

根因 confirmed：裸路径正则未排除中文冒号，误吞说明；10处当前说明未随已完成归档同步。用户授权在原Change内修复，不改变部分交付策略。

实现：仅裸路径以中文冒号分隔，显式Markdown链接保留含冒号的合法文件名；正例、缺失目标反例与显式链接均回归。

文档：定向更新10块当前摘要，原文快照如下；不改历史事件、Change归档目录、证据包和恢复日志。不改API/DB/UI/部署、安全或客户端生成。纯治理Change无来源REQ；三个REQ仅当前交付说明变化，业务流程、用户故事、验收标准和prototype无需更新，原因是产品能力与验收标准不变。

## 验证

88项聚焦回归通过。sprint-014扫描53份文件、sprint-015扫描25份文件均零命中；8个相关归档Change的1548个文件摘要不变，清单见evidence/repair/protected-files.json。严格OpenSpec校验通过。Docker reap服务不可达，本次无新容器。自动验收新增AC-REPAIR-DOCS保存扫描与保护检查；不宣称真实产品归档已验证。

## 返修前文案快照

以下仅为本轮修复前快照，不作为当前状态。原文没有明确时间的不补造发生日期。

### issues/bugs/archive/BUG-0056-requirement-center-context-load-latency/trace.md

原章节：## 当前摘要

```text
已补齐 [缺陷文档](bug.md)、[根因分析](root-cause.md)、[临时规避](workaround.md) 与 [验收标准](acceptance.md)，确认全量快照扫描、归档目录重复查找及逐卡注册表重复解析三个性能机制；两项只读对照结果一致。原始约27秒的完整分段归因、冷暖统计与修复回归仍待补证。[评审已通过](review.md)，保留 high；已纳入 sprint-014，状态为 in_sprint；已创建 fix-requirement-center-context-load-latency，状态为 proposed；实施与验收未开始。
```

### issues/bugs/archive/BUG-0056-requirement-center-context-load-latency/bug.md

原章节：## 当前交付状态

```text
已补齐 [根因分析](root-cause.md)、[临时规避](workaround.md) 和 [验收标准](acceptance.md)，根因证据与中文标题门禁已通过，已评审通过并纳入 sprint-014，当前状态为 in_sprint。三个瓶颈机制已确认，剩余证据边界保留；已创建 [修复Change](../../../../openspec/archive/2026-10-30-fix-requirement-center-context-load-latency/proposal.md)，尚未实施修复或完成验收。
```

### issues/bugs/archive/BUG-0065-chat-final-answer-duplicate-concatenation/trace.md

原章节：## 当前摘要

```text
缺陷包已补齐，机制根因 confirmed，见 [根因分析](root-cause.md)。评审已通过，已纳入 sprint-014，状态为 in_sprint；已创建 fix-chat-final-answer-duplicate-concatenation，状态 applied；已完成实现，验收以最新证据包为准。
```

### issues/bugs/archive/BUG-0066-chat-auto-verification-status-stale/trace.md

原章节：## 当前摘要

```text
缺陷包已补齐，机制根因 confirmed，见 [根因分析](root-cause.md)。评审已通过，已纳入 sprint-014，状态为 in_sprint；已创建 fix-chat-auto-verification-status-stale，状态 applied；已完成实现，验收以最新证据包为准。
```

### issues/bugs/archive/BUG-0067-chat-stream-preview-premature-truncation/trace.md

原章节：## 当前摘要

```text
用户已明确批准修复，评审通过，severity 保持 medium；根因证据门禁通过。已纳入 sprint-014；修复 Change 已 applied，9/9 验收通过，本地服务已更新，下一步可执行归档。
```

### issues/bugs/archive/BUG-0067-chat-stream-preview-premature-truncation/acceptance.md

原章节：## 实施验证摘要

```text
后端 SQLite 最终 47 项通过，MySQL 35 项及边界/状态 22 项、最终粒度/保护增量 6 项通过；前端 33 项与 TypeScript 通过。交付依据见 `openspec/archive/2026-10-27-fix-chat-stream-preview-premature-truncation/verification.md`，截图见同 Change `evidence/acceptance/visual/`。读取不改业务状态、不重放命令；本地完整 Chat 已按授权更新；未正式归档。
```

### issues/bugs/archive/BUG-0068-chat-database-lock-execution-interruption/trace.md

原章节：## 当前摘要

```text
根因 confirmed（现场机制），严重等级 high；已评审通过，状态 approved。缺陷主文档见 [缺陷说明](bug.md)，最新补证见 [根因分析](root-cause.md)，初始判重见 [缺陷记录](capture.md)。已评审并纳入sprint-014；已创建fix-chat-database-lock-execution-interruption，尚未实施修复。

关联 BUG-0056-requirement-center-context-load-latency；原执行不重跑、不解除保护。历史失败事务与当前采样持锁来源分别记录。
```

### issues/requirements/archive/REQ-0042-agent-runtime-version-space-isolation/requirement.md

原章节：## 11. 当前状态

```text
- 状态：in_sprint（已纳入 sprint-015）；P1。
- 已完成：PRD、用户故事、业务流程、验收标准、追溯与交互原型拆解、需求评审。
- 已创建 Change：`update-unified-workspace-runtime`；尚未实现与产品验收。
- 下一步：`/opsx-apply REQ-0042-agent-runtime-version-space-isolation`。
```

### issues/requirements/archive/REQ-0054-workspace-recovery-points/requirement.md

原章节：## 11. 当前状态

```text
- 状态：in_sprint（已纳入 sprint-015）；P1。
- 已完成：PRD、用户故事、业务流程、验收标准、追溯与交互原型拆解、需求评审。
- 已创建 Change：`add-workspace-recovery-points`；尚未实现与产品验收。
- 下一步：`/opsx-apply REQ-0054-workspace-recovery-points`。
```

### issues/requirements/archive/REQ-0055-sprint-authorized-worktree-merge/requirement.md

原章节：## 11. 当前状态

```text
- 状态：in_sprint（已纳入 sprint-015）；P1。
- 已完成：PRD、用户故事、业务流程、验收标准、追溯与交互原型拆解、需求评审。
- 已创建 Change：`add-sprint-authorized-worktree-merge`；尚未实现与产品验收。
- 下一步：`/opsx-apply REQ-0055-sprint-authorized-worktree-merge`。
```


## 批次二：文档标题一致性

偏差与根因 confirmed：标题校验要求有效中文 title 与唯一且一致的 H1；proposal、design、tasks、spec 缺少二者，trace 缺少 title，返修台账 H1 与 title 不一致。证据为上一轮 validate-document-titles.py 的明确失败结果与对应文件结构。

修复仅补齐五份文档元数据及缺少的一级标题，将台账原批次一标题降为二级并增加总标题。正文、历史快照、增量 Requirement/Scenario 和部分交付策略不变。既有 applied、首次执行时间不变。新增 AC-DOC-TITLES 固化六份文档的标题检查，其他 AC 按指纹复用或复验；结果见最新 evidence/acceptance 完整清单。

文档同步判定：直接治理 Change，无来源 REQ/BUG，无需更新 Issue 子文档；仅同步本 Change 与 Sprint 验收摘要。API、数据库、UI、部署、安全、客户端及发布行为无变化，无需同步其他产品文档。历史证据文件不改写，不正式归档。
