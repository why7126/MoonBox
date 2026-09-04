## 1. 后端能力模型

- [x] 1.1 定义文档能力对象 schema，包含 `readable`、`human_editable`、`ai_mutable`、`task_toggle_only`、`reason`，并保留 `editable=human_editable` 兼容字段。
- [x] 1.2 实现统一能力计算函数，输入对象类型、阶段、状态、文档名、路径类别、存在性和用户权限。
- [x] 1.3 落地 Human Edit Capability 阶段矩阵，覆盖 REQ、BUG、OpenSpec Change 和已生效 spec 路径边界。
- [x] 1.4 明确 `trace.md` 人工始终只读、系统治理链路可按门禁写入的能力返回。

## 2. API 与保存授权

- [x] 2.1 更新文档列表和文档读取响应，返回能力对象与脱敏 `reason`。
- [x] 2.2 更新完整 Markdown 保存接口，后端复用能力计算并仅允许 `human_editable=true` 的人工保存。
- [x] 2.3 新增或调整 task toggle 保存入口，仅允许 `task_toggle_only=true` 时提交。
- [x] 2.4 实现 `tasks.md` checkbox-only 差异校验，仅允许 `- [ ]` 与 `- [x]` 切换。
- [x] 2.5 为只读、越权保存、非法路径、验收中全文修改 `tasks.md`、编辑已生效规格返回稳定脱敏错误。

## 3. 前端 Markdown 抽屉

- [x] 3.1 将前端编辑入口从硬编码 `capture.md` 改为后端能力对象驱动。
- [x] 3.2 `human_editable=true` 时保留完整编辑、分栏、Vditor、保存和脏状态保护。
- [x] 3.3 `task_toggle_only=true` 时渲染任务 checkbox-only 操作，不展示 Vditor 工具栏、源码编辑器、分栏或全文保存入口。
- [x] 3.4 只读文档展示阅读态和受限原因，关闭只读或未改动文档不触发未保存确认。
- [x] 3.5 待开发 OpenSpec Change 文档展示 Change 范围标识，区分草案 `spec.md` 与已生效规格。

## 4. 产品数据采集与链路观测

- [x] 4.1 为文档打开、完整保存、checkbox-only 保存、越权拒绝定义稳定行为事件名和脱敏属性。
- [x] 4.2 确认请求日志记录对象 ID、文档名、操作类型、结果、错误码和脱敏原因。
- [x] 4.3 判断 task toggle 差异校验是否接入 Task Trace；若不接入，在 Change 验收记录中写明具体原因。
- [x] 4.4 验证观测 metadata 不保存完整 Markdown、完整请求/响应体、完整 Prompt、Authorization、Cookie、本机路径或内部堆栈。

## 5. 测试与文档

- [x] 5.1 补充后端能力矩阵测试，覆盖全部阶段、REQ/Bug 类型、`trace.md`、OpenSpec Change 文档和已生效 `openspec/specs/**/spec.md`。
- [x] 5.2 补充后端保存授权测试，覆盖越权全文保存、`ai_mutable` 不等于人工可保存、checkbox-only diff 拒绝文本变化。
- [x] 5.3 补充前端测试，覆盖完整编辑态、只读态、checkbox-only 态、脏状态确认和保存失败保留草稿。
- [x] 5.4 同步 API 文档、OpenAPI/Orval 相关产物，或在验收记录中写明不适用原因。
- [x] 5.5 运行聚焦后端测试、前端测试、OpenSpec 校验和中文优先校验。

## 6. 验收回填

- [x] 6.1 回填 Change `trace.md` 的实现状态、验证摘要和产品数据采集与链路观测结论。
- [x] 6.2 执行 REQ 子文档一致性检查，确认 `requirement.md`、`acceptance.md`、`trace.md` 与最终实现和 Change 文档一致。

## 验收返修记录

| 时间 | 反馈 | 调整 | 验证 |
|---|---|---|---|
| 2026-09-04 08:51:35 | workflow demo 中规划中 `DEMO-REQ-PLANNING-READY` 的 `requirement.md` 显示“当前阶段只读”，未按矩阵开放编辑。 | 前端 demo/fallback 文档能力改为按 `issue.type + issue.stage + documentName` 生成；阶段流转临时文档同样复用能力矩阵。REQ 子文档一致性扫尾检查：无需更新 `requirement.md`、`business-flow.md`、`user-stories.md`、`acceptance.md`，原因是验收标准未变化，返修只纠正 demo/fallback 实现偏差。 | `corepack pnpm@11.2.2 --dir src/web exec vitest run src/requirement-center.test.tsx --reporter=dot` 通过，59 passed；`corepack pnpm@11.2.2 --dir src/web build` 通过。 |
