---
requirement_id: REQ-0024-markdown-editor-human-edit-permission-matrix
created_at: 2026-09-03 22:02:09
updated_at: 2026-09-03 22:02:09
owner: product
source: requirement.md
---

# 业务流程

## 总体流程

```text
用户打开需求中心
  -> 后端读取 REQ/BUG/Change/Sprint 事实源
  -> 后端按阶段、文档名、路径类别和用户权限计算文档能力
  -> 前端渲染文档入口与 Markdown 抽屉
      -> human_editable=true：完整编辑/分栏/Vditor
      -> task_toggle_only=true：任务 checkbox-only
      -> 其他 readable=true：只读预览
  -> 用户提交保存或勾选
  -> 后端复用能力计算做最终授权
      -> 允许：写入文档并返回最新内容
      -> 拒绝：返回脱敏错误原因
```

## Human Edit Capability

```text
对象阶段 + 对象类型 + 文档名 + 文档路径
  -> Human Edit Capability
      capture: capture.md
      planning: requirement.md / bug.md
      review-ready: 完善类文档
      approved: 完善类文档 + review.md
      sprint-planning: none
      ready-dev: proposal.md / change spec.md / design.md / tasks.md
      development: none
      acceptance: tasks.md checkbox-only
      done: none
```

人工编辑能力只服务页面用户操作，不表达 AI/Workflow 能否写入。

## System Mutation Capability

```text
AI / Workflow / 脚本 / 命令
  -> 命令门禁校验
  -> Issue / Sprint / OpenSpec 状态机校验
  -> Workflow Sync 或对应治理脚本写入
  -> trace / requirement / acceptance / tasks 等事实源同步
```

系统修改能力不由前端只读态决定。`trace.md` 对人工始终只读，但 Workflow Sync 仍可追加变更记录。

## `tasks.md` 验收中勾选流程

```text
验收中对象打开 tasks.md
  -> 后端返回 task_toggle_only=true
  -> 前端渲染 task list checkbox
  -> 用户切换单个或多个 checkbox
  -> 前端提交 task toggle 请求
  -> 后端计算原文与新内容 diff
      -> 仅 checkbox 状态变化：保存
      -> 其他文本变化：拒绝
```

## 与父 REQ 差异

REQ-0021 关注 Markdown 抽屉和 Vditor 增强编辑体验，MVP 只允许采集池 `capture.md` 编辑。本需求不新增编辑器能力本身，而是把“是否可人工编辑、是否可系统修改、是否仅可勾选”抽象成统一权限矩阵，并扩展到 REQ、BUG 和 OpenSpec Change 文档。

## 数据与安全边界

- 前端只负责体验呈现，不能作为最终授权边界。
- 后端必须对每次保存或勾选请求重新计算能力。
- 错误提示只返回脱敏业务原因，不返回本机路径、内部堆栈、密钥或完整治理目录。
- 行为事件、请求日志和 Task Trace 只记录操作摘要、对象 ID、文档名、结果、错误码和脱敏原因。
