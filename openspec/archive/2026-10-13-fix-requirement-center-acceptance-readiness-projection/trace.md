---
change_id: fix-requirement-center-acceptance-readiness-projection
title: 需求中心验收投影与文档持续入口修复追溯记录
status: applied
created_at: 2026-10-09 23:00:00
updated_at: 2026-10-13 08:24:00
bug: BUG-0035-requirement-center-acceptance-readiness-projection
requirement: null
sprint: sprint-009
product_data_collection_observability:
  status: applicable
  affected_layers:
    - web
    - governance_context_api
    - document_read_api
    - request_logs
  reason: 验收摘要、文档来源及归档阻断提示涉及上下文接口、授权读取和脱敏请求日志；无 DB schema、对象存储或新保留周期，新增行为事件与 Task Trace 按实际交互评估。
  validation: 计划对照 BUG-0025 归档阻断、聚合来源、项目授权、接口字段和请求日志；不记录文档正文、凭证或本机路径，OpenAPI 与客户端生成按实际字段差异同步。
execution:
  schema_version: 1
  started_at: 2026-10-09 23:05:16
  completed_at: 2026-10-10 03:48:43
  last_event: opsx.apply
---

# 需求中心验收投影与文档持续入口修复追溯记录

## 验收返修批次七：已存在 Change 文档缺失误报

- 用户截图与本地 Firefox 旧 Web 页面均显示 BUG-0035 验收卡片的 Change 文档已存在，但卡片仍报缺少。前端 `missingDocs` 的验收阶段错误读取 Issue 清单；偏差、截图逐项对照和边界见 `acceptance-fixes.md`。
- Web 修正验收阶段来源判断，聚焦测试覆盖“文档齐全无误报”与“真实缺失仍提示”；设计、delta spec、Issue AC-005、Sprint 验收与发布说明已同步。Change 保留 `status: applied` 和首次 `execution.completed_at`。
- 122 项前端聚焦测试、TypeScript、OpenSpec strict、中文与标题校验通过。Chrome 合成 API 预览于 1440×900 和 390×844 确认四份 Change 文档可见且无缺失红字，关键宽度与溢出数据见台账；常驻产品仍是旧包，未将隔离预览写成正式部署验证。API、DB、权限、部署、对象存储及客户端生成无变化；产品数据采集与链路观测无新增字段或事件。
- 本轮增量验收包 `evidence/acceptance/20261013082137855527-0df28337/` 为 11/11 passed，readiness ready 且无 stale；Workflow Sync `opsx.accept` 将 linked Issue 验收状态同步为 passed。2026-10-13 08:24:00 Firefox 刷新后常驻产品 BUG-0035 卡片无 Change 文档缺失误报，`proposal.md` 抽屉正文加载成功，详见台账；Change canonical applied，待本次归档。AI Usage hook 返回 warning/unavailable，未发现可归属 command run。

## 来源与范围

来源：`BUG-0035-requirement-center-acceptance-readiness-projection`，关联 `REQ-0012-frontend-requirement-center`，纳入 `sprint-009`。BUG-0025 是验收与归档提示不一致的复现实例，BUG-0023 是任务分类相关历史缺陷。

## 实施与验证记录

- 后端：保留 Issue 文档与关联 Change 文档各自来源；Sprint 文档保持独立入口。验收态从 Issue `acceptance.md` 的 AC 勾选和 `acceptance_status` 独立投影，研发、测试、人工任务仍按 Change `tasks.md` 分类统计。归档按钮在验收缺证据、任务未完成或服务端阻断时不展示。
- 修复联动回归：待开发卡片的动作门禁单独读取关联 Change 的 proposal、spec、design、tasks，避免文档分源后误报缺失；验收态不借用 Change 的同名文档冒充 Issue 验收来源。
- BUG-0025 事实源：Change 研发 41/41、测试 37/37；Issue `acceptance.md` 标记 `pending` 且 52 条 AC 仍为未勾选。Chat 归档复盘另列 AC-051/052 的真实产品复验与交付证据缺口，服务端归档保持阻断。现有文档未逐项回填通过，因此卡片保守显示 52 条待验证；不能推断其他 50 条已通过。
- 自动化：`src/backend/tests/test_governance_board.py` 79 passed；相邻治理生命周期、缓存、范围测试 20 passed；`src/web/src/requirement-center.test.tsx` 116 passed（Node 25 使用 `NODE_OPTIONS=--no-experimental-webstorage`）；Web TypeScript `tsc -b` 与正式 Web 构建 passed；OpenSpec strict、中文与标题校验 passed。
- API 集成回归：`tests/integration/api/test_requirement_center.py` 22 passed；两个旧断言曾从 Issue 文档清单读取 Change 文档，现改为从关联 Change 的 `document_entries` 读取，保持文档来源契约。
- API 与观测：新增 `acceptance_pending_count`、`acceptance_blocked_reason`，已刷新 OpenAPI、Orval 客户端与 `docs/03-api-index.md`。没有 DB schema、对象存储、部署配置、安全策略、新行为事件或 Task Trace 协议变化；沿用治理上下文和文档读取的现有鉴权与脱敏请求日志。
- UI 边界：复用既有需求中心卡片、文档抽屉和动作入口；不引入 Mock 数据、不新建 modal。桌面与移动视口的真实产品观察另行记录。
- 真实产品观察：本地标准部署 `bash scripts/docker-down.sh self-storage-sqlite --chat-platform` 与 `bash scripts/docker-up.sh self-storage-sqlite --chat-platform` 配对完成且服务健康；Firefox `http://localhost:39002/requirements`，1440×900 和 390×844 响应式视口，管理员角色，BUG-0025 验收中卡片：Issue/Change/Sprint 文档入口持续显示，验收待办 52 项与研发 41/41、测试 37/37 同时可见，无归档入口；BUG-0035 研发中卡片关联 Change 文档存在，`查看进度` 动作可用。截图保存在 `data/visual-evidence/BUG-0035-requirement-center-acceptance-readiness-projection/`，其中 `card-1440.png`、`card-390.png` 为双视口卡片，`acceptance-drawer-1440.png` 为 Issue 验收文档抽屉。
- 视觉与 selector 对照：卡片 `.rc-card[data-issue-id="BUG-0025"]`，来源分组 `.rc-doc-group` / `.rc-doc-source`，验收提示 `[data-testid="acceptance-readiness"]`，卡片动作 `.rc-card-actions`；点击 Issue `acceptance.md` 打开题头 `BUG-0025 · acceptance.md` 的既有 Markdown 抽屉，正文可读且显示当前阶段不可人工编辑。1440px computed style：卡片宽 300px，验收提示和文档组宽 264px，文档按钮 `overflow-wrap: anywhere`；390px：`innerWidth=390`、`body.scrollWidth=390`，卡片宽 300px，验收提示和文档组宽 264px。390px 看板沿用横向滚动列，卡片内容可读。取证时发现 Web 入口缺少 viewport 元标签会将 390px 模拟视口按 980px 布局；已在 `src/web/index.html` 补齐并重新部署，部署后页面自带一个 viewport 元标签且 `innerWidth=390`。
- 权限负向证据：聚焦 API 回归 4 passed。`test_http_permissions_readonly_sprint_and_refresh` 验证 Change 任务文档写入/勾选和无权读取均返回 403，冻结空间动作只读；`test_multiple_source_permission_and_conflict_api` 验证无权 Issue 不泄漏关联 Change、Change 文档 403、归档身份冲突 404；`test_requirement_center_document_endpoints_are_sanitized` 验证非法文档 400 且不泄漏路径；`test_requirement_center_context_requires_login` 验证未登录 401。管理员浏览器观察只用于视觉与内容投影，不替代这些权限负向断言。
- Apply 连续执行观察：`data/visual-evidence/BUG-0035-requirement-center-acceptance-readiness-projection/apply-behavior.json` 记录从 11/12 任务恢复、390px 视口偏差自修、12/12 后执行完成同步；`python scripts/validate-apply-behavior.py --trace ...` 返回 observed 3 records、0 errors。Workflow Sync `opsx.apply` 更新 5 项、错误 0，Change 状态为 `applied`；AI Usage 自动发现无可归属 token_count 事件，hook 返回 warning/unavailable，Sprint 快照跳过。
- 经验沉淀评估：本次偏差已在 BUG root-cause、Change 设计与实施验证中完整追溯；现阶段不新增 incident 文档，归档时按最终验收证据再评估是否提炼通用规则，未自动创建 follow-up Issue/Change。

## 验收返修批次一

- 用户反馈：BUG-0035 卡片文档应按 Issue、Change、Sprint 分组；Sprint 独立显示三份已生成 MD，Change trace 按 `trace.md` 显示；Issue `acceptance.md` 已完成 AC 需由验收人依据证据勾选。截图逐项偏差与完整返修记录见 `acceptance-fixes.md`。
- 返修验证：后端相关回归与集成共 143 passed，前端需求中心 117 passed、TypeScript 通过；Firefox 1440px/390px 截图与 computed style 见 `data/visual-evidence/BUG-0035-requirement-center-acceptance-readiness-projection/modify-card-*.png` 和返修台账。Sprint 两份新增文档均在产品抽屉中成功只读打开。
- 事实与阶段：canonical Change 保持 `applied`，首次 apply 完成时间不变。Workflow Sync `opsx.modify` 更新 2 项、错误 0，用户可见阶段回到“验收中 / 待复验”；Issue AC 尚未人工签认，归档门禁保持阻断。AI Usage hook 返回 warning/unavailable（无可归属 token_count 事件），Sprint 快照跳过。接口 schema、生成客户端、DB、部署和权限边界 N/A；仅增加现有授权文档读取接口允许的 Sprint 文件名，文档索引已同步。

## 验收返修批次二

- 反馈与实施：将重复验收待办文案收敛为测试后方的“人工验收 已勾选 AC 数/AC 总数”，点击 Issue `acceptance.md`；对照、边界和截图详见 `acceptance-fixes.md`。服务端归档仍根据未勾选 AC、结论和任务独立阻断。
- 验证：后端 102 passed、前端 117 passed、TypeScript 通过；Firefox 1440px/390px 实际页面的 `BUG-0035` 显示 `人工验收 0/10` 且无重复红字，点击打开只读 Issue 文档。证据见 `data/visual-evidence/BUG-0035-requirement-center-acceptance-readiness-projection/modify2-*.png`。
- 身份与边界：canonical `applied` 与首次 apply 完成时间不变；复用已有 API 字段和授权读取路径，OpenAPI/客户端生成、DB、对象存储、部署和页面写权限不变；Issue 人工签认仍为 pending，不能归档。

## 验收返修批次三

- 反馈与实施：研发、测试、人工验收进度未完成时仅将数字标红；总数未知不误标红。截图逐项对照、代码规则和 BUG-0026 独立范围判断见 `acceptance-fixes.md`。
- 验证：前端需求中心 117 项及 TypeScript 通过，Docker Web 生产构建通过；Firefox 实际页面 1440×900、390×844 均观察到 BUG-0035 `0/10` 红色，已完成的 `11/11`、`7/7` 灰色；移动端 `body.scrollWidth=390`。OpenSpec strict、中文和标题校验通过。全仓设计系统校验仍报 178 项既有违规，本轮进度样式无新增命中。
- 边界：当前 Change 保持 canonical `applied` 和首次 apply 完成时间；本次没有改变 API、DB、授权、部署配置或服务端归档门禁。BUG-0026 验收文档格式问题未并入本次返修，BUG-0035 Issue AC 仍待人工签认。

## 验收返修批次四

- 反馈与根因：BUG-0035 卡片研发、测试按钮提示未关联 `tasks.md`，而 Change 组同名文档可正常打开。进度按钮只在 Issue 自身文档中查找，未使用关联 Change 的文档来源；详见 `acceptance-fixes.md` 的页面对照与按钮矩阵。
- 实施与验证：Issue 进度按钮改为读取当前关联 Change `tasks.md` 并分别定位研发与自动化测试章节；多 Change 无当前来源时保守提示。前端需求中心 119 项测试、TypeScript、Docker Web 生产构建、OpenSpec strict 与当前 Change 中文校验通过。Firefox 管理员真实页面重新加载后，在桌面浏览器与 390px 响应式视口点击 BUG-0035 研发及测试均打开右侧抽屉并定位目标章节。
- 边界：canonical `applied` 和首次 apply 完成时间保持不变；沿用授权文档读取，无 API、DB、部署配置、安全或客户端生成变化。Issue 10 项 AC 仍待人工签认，归档门禁保持阻断。
- 同步：Workflow Sync `opsx.modify` 更新 1 项、错误 0，BUG-0035 验收状态仍为 `pending`；AI Usage hook 未发现可归属 `token_count` 事件，返回 warning/unavailable，Sprint 快照跳过。

## 验收返修批次五

- 反馈与范围：用户希望卡片第三个进度名称由“人工验收”改为“验收”，以容纳未来自动验收方向。本轮只调整展示名称与口径说明；当前数字仍是 Issue `acceptance.md` 的 AC 勾选进度，自动验收结果未计入。完整视觉对照与边界记录见 `acceptance-fixes.md`。
- 实施与验证：前端按钮可见标签、无障碍名称、悬浮说明及缺文档提示已同步；119 项需求中心测试、TypeScript、Docker Web 生产构建通过。Firefox 本地真实页面在 390px 和 1440px 视口显示“验收 0/10”，点击仍打开 `BUG-0035 · acceptance.md`；OpenSpec strict 与中文校验通过。
- 边界：Change canonical `applied` 和首次 apply 完成时间不变；无 API、DB、权限、部署、对象存储或客户端生成变化。Issue AC 仍待人工签认，归档门禁保持阻断。

## 验收返修批次六

- 反馈与证据：BUG-0033 的 11 条 AC 仅在表格中，原产品卡片显示“验收结论待核实”。将四份未归档的表格 AC 文档增补未勾选清单后，后端可分别计数为 BUG-0028 0/8、BUG-0029 0/6、BUG-0033 0/11、BUG-0034 0/5；原表格与验收结论保留。真实页面随后暴露 BUG-0033 无自动测试分母时前端仍隐藏验收按钮，完整截图对照和盘点见 `acceptance-fixes.md`。
- 实施：验收进度不再依赖测试进度存在；进度容器可由验收 AC 单独触发。BUG-0035 linked Issue 增补 AC-011，Change 设计及 delta spec 明确无测试分母仍需展示。
- 边界：仅 Issue 文档格式与 Web 展示条件变化；API/DB/权限/部署配置、对象存储和客户端生成不变。Change canonical `applied` 和首次 apply 完成时间保留，所有新增 AC 均未代签。
- 验证与同步：前端需求中心 120 项、后端需求中心 80 项、TypeScript、Web 生产构建、OpenSpec strict、中文与标题校验、Sprint Scope 均通过；Firefox 桌面和 390px 真实页面均显示 BUG-0033 “验收 0/11”，抽屉可读且 AC 未勾选。全仓 Design System 有 178 项既存违规，本次无新增样式/控件。Workflow Sync `opsx.modify` 更新 1、错误 0；AI Usage warning/unavailable。完整证据仍以 `acceptance-fixes.md` 为准。

## 逐项复验批次七

- 2026-10-11：BUG-0035 linked Issue AC-001～008、AC-011 依据实际卡片观察、既有双视口视觉证据及本轮后端 88/前端 120 项聚焦回归完成 Codex 技术签认，验收进度为 9/11。详情见 `acceptance-fixes.md` 与 linked Issue `acceptance.md`。
- AC-009 全阶段双视口视觉矩阵、AC-010 当前 BUG-0025 Chat 归档拒绝响应仍待补证；Change 保持 canonical `applied`，Issue 验收 `pending`，当前不能归档。无实现、API、DB、授权、部署或客户端生成变化。

## 自动验收证据包（2026-10-12）

- `/opsx-accept` 对 BUG-0035 逐项建计划并生成 `openspec/changes/fix-requirement-center-acceptance-readiness-projection/evidence/acceptance/20261012154349001165-323fcebd/`；结果 9 passed、AC-009 视觉矩阵证据缺失、AC-010 当前 Chat 归档轮次未授权且未取得，整体未 ready。linked Issue 仍 pending，Change 仍 applied。
- Firefox 当前卡片投影与历史 Chat 阻断回复已分层记录；未将 2026-10-09 的旧回复视为当前服务端拒绝。未修改业务实现、API、DB、权限或部署配置。

## 授权补证与复验（2026-10-12）

- 临时治理源副本构造 BUG-9101/9102/9103，Firefox 分别观察迭代规划、待开发、研发中卡片及来源文档分组；截图导出未得到完整目标卡片与 computed style，AC-009 未签认。临时服务已停止，未写正式治理对象。
- 正式 BUG-0025 对象 Chat 归档 turn `f3d624c6-2422-4eee-9a49-3181af97d5fd` 的脚本退出 1；任务 80/81 与规格合并校验先行阻断，未触达验收门禁，亦未发生归档。AC-010 未签认。
- 新证据包 `evidence/acceptance/20261012162428424904-79c14fde/` 为 9 passed、2 failed；脱敏观察在 `evidence/acceptance/isolation-stage-and-archive-observation.md`。Change 保持 applied，linked Issue 验收 pending。

## 阶段视觉矩阵补证（2026-10-12）

- Firefox 1440×900、390×900 的七个 Issue 阶段和独立 Change 共 16 张完整截图已纳入 `evidence/acceptance/stage-visual/`；逐项对照、关键点击及样式证据索引见 `evidence/acceptance/phase-matrix-1440-390.md`。隔离对象未进入正式治理源。
- linked Issue AC-009 已由 Codex 技术复验勾选。最新证据包 `evidence/acceptance/20261012164826724067-559511d7/` 为 10 passed、AC-010 failed。正式 BUG-0025 归档仍被其未完成任务与规格合并校验先行阻断，未证明验收门禁；Change applied、Issue acceptance pending，未归档。

## AC-010 续验预检（2026-10-12）

- `python scripts/opsx_acceptance.py --change fix-requirement-center-acceptance-readiness-projection --readiness` 返回 `blocked`，仅 AC-010 stale；未重复发送有副作用的正式归档命令。
- BUG-0025 `tasks.md` 的第二条 AF-041 仍未完成；该 Change 的 `评审成果受控自动回写` delta requirement 在当前有效规格中无对应可合并目标，故先前归档轮次未进入验收门禁。
- 当前 `acceptance-plan.json` 的 AC-010 使用 `product_turn`，执行器要求目标归档命令 `exit_code=0`；但本 AC 的目标是观察缺证据时归档被拒。该成功条件与负向验收目标不一致，即使前置阻塞解除，也不能仅凭该自动判定签认。后续需在本 Change 范围内校正负向产品轮次的判定和证据约束，再取得同轮真实门禁响应。

## AC-010 门禁同轮复验与验收完成（2026-10-12）

- BUG-0025 的 AF-041 已在独立真实产品副本取得同轮 candidate `applied`、application `applied/verified`，可信 `bug.md`、trace、注册表、索引均为 draft；其 delta spec 严格校验和临时副本合并通过。正式 BUG-0025 仍有 28 条待验 AC，保持 active。
- `scripts/archive-change.sh` 在规格合并与目录迁移前执行 Issue 验收门禁。正式关联 Chat turn `9bffe2e8-bb23-4559-b132-b4feb6856ef6` 已完成，同轮命令事件序号 38 的归档脚本退出 1 并返回 `ACCEPTANCE_GATE_BLOCKED issue_acceptance_pending checked=24 total=52`；Change 与 Issue 原位。AC-010 负向判定要求同轮命令、预期退出码、门禁标记和文件效果，其他失败不得冒充通过。
- 完整增量验收证据包 `evidence/acceptance/20261012174521381442-836220d3/` 为 11/11 passed；`--readiness` 返回 ready、stale 为空。Workflow Sync `opsx.accept` 无错误，将 linked Issue `acceptance_status` 同步为 passed。Change canonical applied，未自动归档。
