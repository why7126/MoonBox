---
bug_id: BUG-0067-chat-stream-preview-premature-truncation
title: Chat 流式正文预览过早截断修复验收标准
created_at: '2026-10-26 20:19:21'
updated_at: 2026-10-30 09:12:20
acceptance_status: passed
---

# Chat 流式正文预览过早截断修复验收标准

## 验收状态

修复已实现；AC-001 至 AC-007 的命令/隔离集成回归通过。AC-008 两种视口五阶段隔离截图及真实 Agent 完成轮次已签认；整体证据校验 9/9 通过。

## 回归标准

| 编号 | 场景与操作 | 通过条件 | 证据方式 |
|---|---|---|---|
| AC-001 | 无 final 的运行中 output，分别保存 20、21、22、294 个小片段，总正文低于展示预算 | 正文顺序完整，恰好 21 不误判，多片段不提前停在第 21 段；无缺失提示 | 后端真实存储读取测试，断言正文与 truncated |
| AC-002 | 相同短正文按不同粒度切分，包含中文和换行 | 展示及复制文本一致，无丢字、乱码、重复 | 后端字符完整性与前端复制测试 |
| AC-003 | 正文在展示预算以下、恰好预算、超过预算 | 前两者完整；超限有准确范围提示及可用完整内容入口，不误报执行失败 | 后端边界测试、浏览器入口与分页验证 |
| AC-004 | 历史事件读取存在序号缺口、读取失败；对照正常流式未结束 | 保留真实缺口/读取失败反馈，不将所有警告隐藏；正常生成不作为内容丢失 | 旧格式兼容测试、前端状态测试 |
| AC-005 | 从 output 切换选定 final；覆盖合法多片段、重复通知与不同最终版本 | 正确选择最终答案，保持合法正文，不重复拼接；不得改变执行终态事实 | 最终答案回归测试及刷新检查 |
| AC-006 | 运行中、完成、失败、停止状态下读取与刷新历史 | 状态和正文完整性独立表达；已保留过程正文可读；不产生重复助手消息 | 状态矩阵、真实浏览器观察 |
| AC-007 | 大量微片段和超大正文，含无权限跨会话读取 | 查询/内存受明确预算约束，分页可终止，权限隔离保持，不因读取执行写入或重放命令 | 查询次数/读取字节统计、鉴权测试、写入次数断言 |
| AC-008 | 本地 Chat 真实运行，正常结束；1440px 与窄屏视口 | 连续输出超过 21 小片段后正文仍按预算展示；提示可理解，完整内容入口可操作 | 阶段×视口截图、关键 selector、页面实际值；命令与视觉证据分别记录 |

AC-003/007 的具体预算和查询上界在 Change 设计中明确后执行，不能以无界全量查询满足完整性。AC-008 使用经授权的无副作用测试命令，不重放原 bug-opsx 业务命令。

## 数据采集与链路观测

- product_data_collection_observability: applicable
- affected_layers: Web、API、DB 读取、Agent Workflow 输出链路。
- validation：核对片段数、正文大小、读取范围、截断原因和同轮状态；证据仅存脱敏摘要，禁止记录原始 Prompt、凭证或客户正文。
- N/A：本次文档完善不新增日志、埋点、数据结构或客户端；部署与安全无实现变化。后续若 API/DB/UI 边界变化，须同步文档、规则、测试及必要客户端生成。

## 完成门禁

逐 AC 记录结果与证据。单元测试、合成回归和真实页面观察分开报告；全部适用标准通过才可声明修复验收完成。AC-008 真实轮次 completed，293 段 output，命令退出 0，文件差异为空；真实与合成证据分别记录。

## 实施验证摘要

后端 SQLite 最终 47 项通过，MySQL 35 项及边界/状态 22 项、最终粒度/保护增量 6 项通过；前端 33 项与 TypeScript 通过。交付依据见 `openspec/archive/2026-10-27-fix-chat-stream-preview-premature-truncation/verification.md`，截图见同 Change `evidence/acceptance/visual/`。读取不改业务状态、不重放命令；本地完整 Chat 已按授权更新；已于2026-10-27归档；原验证数量与证据说明保持不变。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-30 08:33:54
accepted_by: workflow-sync
source_change: fix-chat-stream-preview-premature-truncation
source_sprint: sprint-014
evidence: [openspec/archive/2026-10-27-fix-chat-stream-preview-premature-truncation/evidence/acceptance/20261026225142511044-12b2315e/summary.md]
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

