## 背景与动机

REQ-0021 已完成 Markdown 抽屉与 Vditor 基础增强，但现有文档能力仍以单一 `editable` 布尔值和“采集池 + `capture.md`”硬编码表达，无法覆盖 REQ、BUG、Sprint 与 OpenSpec 在不同治理阶段的人工编辑边界。REQ-0024 需要把人工编辑权限、系统治理写入权限和验收中任务勾选能力拆开，避免 `trace.md` 审计记录被人工误改，也避免 UI 只读误伤 Workflow Sync、AI 命令和脚本写入。

## 变更内容

- 将需求中心文档能力从单一 `editable` 扩展为结构化能力对象：`readable`、`human_editable`、`ai_mutable`、`task_toggle_only`、`reason`。
- 按治理阶段、对象类型、文档名、文档路径类别和角色权限计算 Human Edit Capability。
- 明确 System Mutation Capability：AI、Workflow、脚本和命令继续按既有治理门禁修改文档，不受前端只读态限制。
- 保持 `trace.md` 对人工始终只读，同时允许受控治理链路追加或修订审计事实。
- 在验收中阶段将 `tasks.md` 限定为 checkbox-only 操作，后端校验 diff 只能切换 `- [ ]` 与 `- [x]`。
- 待开发阶段仅允许编辑当前 OpenSpec Change 下的 `proposal.md`、`spec.md`、`design.md`、`tasks.md`，已生效 `openspec/specs/**/spec.md` 始终人工只读。
- 前端 Markdown 抽屉改为能力驱动渲染：完整编辑、checkbox-only 和阅读态分支由后端能力对象决定。
- 文档列表和保存接口补充后端二次授权、脱敏错误和产品数据采集与链路观测要求。

## 能力影响

### 新增能力

- 无。

### 修改能力

- `web-catalog-requirement-center`: 扩展需求中心阶段动作与文档抽屉能力，新增按阶段、文档和操作类型计算人工编辑权限的规格。
- `web-catalog-requirement-center-real-data`: 扩展真实治理数据接口与保存接口契约，返回文档能力对象并在后端保存时复用能力计算做最终授权。

## 影响范围

- 后端：需求中心文档列表、文档读取、Markdown 保存、task toggle 保存、权限计算和错误码。
- Web：需求中心卡片文档入口、Markdown 抽屉、Vditor 编辑态、只读态、checkbox-only 渲染、脏状态确认和错误提示。
- API：文档列表响应字段新增能力对象，保存接口区分全文保存与 task toggle 保存；如保留 `editable`，其值为 `human_editable` 兼容别名。
- 测试：后端能力矩阵、越权保存、task toggle diff 校验、已生效规格只读；前端完整编辑态、只读态、checkbox-only 态、脏状态与保存失败。
- 产品数据采集与链路观测：记录人工保存、checkbox-only 保存、只读打开、越权拒绝和系统治理写入的脱敏摘要，覆盖行为事件、请求日志和 Task Trace 候选。
