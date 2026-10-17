---
title: 需求中心验收返修台账
created_at: 2026-10-10 04:00:00
updated_at: 2026-10-13 08:24:00
---

# 需求中心验收返修台账

## 返修批次一：来源分组与验收签认

来源：BUG-0035 验收反馈，用户提供的 BUG-0035 卡片截图。当前 Change 仍为 applied，返修期间仅用户可见阶段投影为研发中；首次 apply 时间不变。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户附件一 | 需求中心、深色主题、BUG-0035 验收中卡片 | 当前卡片与用户文字规则 | Issue、Change、Sprint 三组；Sprint 独立显示三份已生成文档 | Issue / Sprint 混排，Change 行含 sprint.md，Sprint 组缺失 | 来源分组与文档入口 | `.rc-docs`、`.rc-doc-group`，双视口截图与文档读取 | 本次修复 | 用户附件；`data/visual-evidence/BUG-0035-requirement-center-acceptance-readiness-projection/card-1440.png` |
| 用户附件一 | 同上 | Change 文档行 | Change 组中的按钮名为 trace.md | 按钮名为 Change trace.md | 冗余来源前缀 | `.rc-doc-source` 与按钮文本 | 本次修复 | 用户附件；前端源码 `changeDocumentButtonLabel` |
| 用户附件一 | 同上 | Issue acceptance.md 与卡片待办 | 完成的 AC 有证据并勾选；未完成继续阻断 | 10 条 AC 未勾选，卡片显示 10 项待办；当前文档验收阶段只读 | 验收记录与完成事实尚未闭环 | 文档复核、状态投影与归档门禁 | 本次修复归档前签认校验；不代用户勾选或放宽页面权限 | Issue acceptance.md；后端 `_acceptance_readiness` 与 Workflow Sync |

复现条件：授权管理员查看 BUG-0035 验收中卡片；Sprint 为 sprint-009，三份 Sprint 文档已存在。此批次保留原文档抽屉、阶段写权限与项目隔离。文档入口仅暴露关联 Sprint 的实际文件，不引入新的对象授权。

## 实施与验证

- 文档来源：后端按关联 Sprint 的实际文件登记 `sprint.md`、`release-note.md`、`acceptance-report.md`，沿用现有项目和对象授权及只读读取接口；前端把 Issue 自身文档、关联 Change 文档和 Sprint 文档分别放入三组。同名 `trace.md` 由组名区分，Change 按钮仅显示文件名。纯 Change 卡片仅显示实际拥有的 Change 和 Sprint 组。
- 验收门禁：Issue `acceptance.md` 的 AC 勾选与 `acceptance_status` 均是独立验收事实。完成的 AC 由验收人逐项对照证据勾选并回填结论；本轮不代签。后端对未勾选或状态 pending 保持待验收提示及归档阻断。返修任务不会把 AC 计入研发/测试分母。
- 文档同步：BUG `acceptance.md` 的 AC-002、AC-003、AC-005、AC-006、AC-009 已纠正来源分组与验收签认表述；Change `design.md`、两份 delta spec、Sprint `acceptance-report.md` 与 `release-note.md`、`docs/03-api-index.md` 已同步。API 响应结构、OpenAPI schema、Orval 客户端、DB、对象存储、部署和页面写权限没有变化。
- 自动化：后端治理板、相关权限/生命周期与 API 集成共 143 passed；前端需求中心 117 passed，TypeScript `tsc -b` passed。覆盖 Sprint 三文档实际存在、授权只读、Issue/Change 来源分隔，以及“全部勾选但状态 pending”继续阻断。
- 产品观察：Firefox 管理员实际页面 `BUG-0035` 验收中卡片在 1440×900 与 390×844 均显示 Issue、Change、Sprint 三组，Sprint 三份文档入口在独立组内；Change 按钮为 `trace.md`。`.rc-card[data-issue-id="BUG-0035"]` 宽 300px，`.rc-doc-group` 宽 264px；390px 时 `body.scrollWidth=390`。返修后截图见 `data/visual-evidence/BUG-0035-requirement-center-acceptance-readiness-projection/modify-card-1440.png` 与 `modify-card-390.png`。浏览器点开 Sprint `release-note.md`、`acceptance-report.md` 均显示原文和“关联 Sprint 文档只读”。首次读取时本地 Web 代理短时 504，重试后两个 GET 均返回 200；同时期上下文请求也发生 504，未将其认作新增入口的代码故障。
- 当前签认状态：BUG-0035 的 10 项 AC 仍未逐项签认，卡片维持“验收待办 10 项”和归档阻断。本轮交付是返修实施及验证证据，后续需验收人按证据勾选并回填通过结论。

## 返修批次二：人工验收进度与点击入口

来源：用户对 BUG-0035 验收中卡片的截图和明确反馈，仍属于同一 Change 的验收投影与文档入口范围。返修期间用户可见阶段按研发中说明；canonical `applied` 和首次 apply 完成时间保持原值。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户附件二 | 需求中心深色主题，BUG-0035 验收中卡片，移动视口 | 进度行与两段红色验收提示 | 测试后显示紧凑的“人工验收 0/10”，点击打开 Issue `acceptance.md` | 研发 10/10、测试 5/5 后无人工验收数字；上方验收待办和下方阻断文案重复 | 验收 AC 未进入进度行且提示重复 | `.rc-progress`、`[data-testid="acceptance-readiness"]`、`.rc-blocked`、文档抽屉 | 本次修复；AC 分母来自 Issue 文档，不混入 tasks.md 研发/测试 | 用户附件；`data/visual-evidence/BUG-0035-requirement-center-acceptance-readiness-projection/modify-card-390.png` |
| 用户附件二 | 同上，点击人工验收 | Issue 文档抽屉 | 打开 Issue `acceptance.md`，保留只读和归档门禁 | 当前人工验收按钮取自 Change `tasks.md` 且指向任务抽屉，BUG-0035 无人工任务时不出现 | 点击目标与数字来源不符 | 按钮 aria-label、抽屉题头、授权文档读取 | 本次修复；任务进度仍只统计 tasks.md，验收结论 pending 继续阻断 | 前端 `visibleManualAcceptanceProgress`、`openTasksAt`；后端 `_acceptance_readiness` |

实施与验证：

- 后端沿用现有 `manual_acceptance_progress` 字段：识别 Issue `acceptance.md` 的 AC 勾选总数和完成数，返回 `[已勾选数, 总数]`；`acceptance_pending_count`、`acceptance_blocked_reason` 和 Change 人工任务门禁维持独立。没有新增字段、请求路径或写权限。
- 前端在 `.rc-progress` 的测试按钮后显示“人工验收 0/10”，点击通过既有授权读取接口打开 Issue `acceptance.md`，不再定位 Change `tasks.md`。未勾选 AC 时去除重复的卡片红色文案；全部勾选但结论 pending 或来源异常时仍保留单条阻断提示，归档动作仍由服务端复核。
- 聚焦回归：后端治理板与 API 集成 102 passed，前端需求中心 117 passed，Web TypeScript 通过；测试覆盖 0/2、1/2、2/2 的 AC 进度以及 `pending` 结论继续阻断，前端确认点击 Issue 文档而不是 tasks。
- 真实产品：标准本地 `self-storage-sqlite --chat-platform` 配对重建后各服务健康；Firefox 管理员在 1440×900 与 390×844 视口，`BUG-0035` 卡片呈现研发 10/11、测试 5/6、人工验收 0/10，未出现旧两段重复红字。点击人工验收打开题头 `BUG-0035 · acceptance.md`，10 项 AC 可读且复选框禁用，底部显示当前治理阶段不允许人工编辑；当前仍无归档入口。computed style：卡片宽 300px、进度行宽 264px；390px 时 `innerWidth=390`、`body.scrollWidth=390`。截图：`data/visual-evidence/BUG-0035-requirement-center-acceptance-readiness-projection/modify2-card-1440.png`、`modify2-card-390.png`、`modify2-acceptance-drawer-390.png`。
- Mock/API 边界：真实卡片计数由后端读取 Issue 文档返回，抽屉沿用授权单文档 API；demo 验收卡片补齐合成 `acceptance.md` 以匹配动作。未更改真实文档内容编辑能力、DB、对象存储、部署配置或安全策略。BUG-0035 AC 仍待验收人逐项签认。

## 返修批次三：未完成进度数字提示

来源：用户提供 BUG-0035 与 BUG-0026 验收中卡片截图，要求研发、测试、人工验收任一进度未满时仅将其数字标红。返修期间用户可见阶段为研发中；Change canonical `applied` 和首次 apply 完成时间保持不变。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户附件三（BUG-0035 卡片） | `/requirements`、深色主题、验收中；附件为卡片裁剪图，当前 Firefox 390px 视口可复现 | `.rc-card[data-issue-id="BUG-0035"] .rc-progress-value` | `人工验收 0/10` 中仅 `0/10` 使用危险色，研发 11/11、测试 6/6 保持常规色 | 三个数字均使用 `--rc-muted` | 未完成验收数字无视觉区分 | 用户截图、Firefox 页面文字、CSS 规则与 computed style；返修后复核 1440px/390px | 本次修复；只变数字颜色，标签及点击抽屉不变 | 用户附件；`src/web/src/styles/globals.css`、`src/web/src/pages/catalog/RequirementCenterPage.tsx` |
| 用户附件四（BUG-0026 卡片） | `/requirements`、深色主题、验收中；附件为卡片裁剪图 | 同一卡片进度行与阻断提示 | 已知分母且未完成的进度数字标红；未知分母仍用待核实提示 | 研发 7/7、测试 17/17；Issue `acceptance.md` 为表格 AC，现有计数规则得不到人工验收分母 | 文档格式与计数规则不匹配 | 用户截图、Issue 文档与 `_acceptance_readiness` 代码路径 | 本 Change 仅修复通用进度色；BUG-0026 验收文档整理由其来源 Change 单独返修 | 用户附件；BUG-0026 `acceptance.md` |

预检：Firefox 当前 `/requirements` 页面可读，BUG-0035 进度为 11/11、6/6、0/10；页面处于旧部署状态。已有截图与代码路径足以确认颜色偏差。与本批次无关的 BUG-0026 验收内容、服务端归档门禁、文档权限和数据接口保持原事实。

实施与验证：

- 在三个进度数字上设置 `data-progress-state`：总数大于 0 且完成数小于总数为 `incomplete`，其余为 `complete`；CSS 仅将 `incomplete` 数字映射到现有 `--rc-danger`，未改变标签样式、点击目标、API 或归档门禁。
- 聚焦前端 117 项测试通过，TypeScript `tsc -b` 与 Docker Web 生产构建通过；OpenSpec strict、当前 Change 中文校验、中文标题校验及本轮文件 `git diff --check` 均通过。全仓 Design System 校验仍有 178 项既有违规，未指向本轮新增的进度样式。
- 实际页面：仅重建并替换本地 Web 容器后，Firefox 管理员在 `/requirements` 观察 BUG-0035；研发 `11/11`、测试 `7/7` 的数字均为 `rgb(152, 160, 179)`，人工验收 `0/10` 的数字为 `rgb(223, 107, 114)`，标签保持常规色。1440×900 时 `innerWidth=1440`、卡片宽 300px；390×844 时 `innerWidth=390`、`body.scrollWidth=390`、卡片宽 300px、进度行宽 264px。Firefox 响应式视口截图与 computed style 已在本轮浏览器取证中核对，未写入独立图片文件；用户原截图是返修前视觉事实源。
- 文档边界：本批次只改变 BUG-0035 已有三项进度的视觉提示；BUG-0026 的表格 AC 与人工验收计数问题仍归属其自身 Change，不在本轮代改验收文档。无 API schema、客户端生成、DB、对象存储、部署配置、安全权限或新行为埋点变化。Issue AC 仍待验收人签认。

## 返修批次四：研发与测试进度抽屉入口

来源：用户反馈点击卡片“研发”“测试”后右侧抽屉失效；本轮 `/explore` 已在 Firefox 现行部署复现。返修执行中用户可见阶段为研发中，Change canonical `applied` 与首次 apply 完成时间保持不变。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 当前页面取证一（无新增附件） | `/requirements`、Firefox 管理员、深色主题、BUG-0035 验收中，研发 11/11 | `.rc-card[data-issue-id="BUG-0035"] .rc-progress-action` 的研发按钮 | 打开关联 Change `tasks.md` 右侧抽屉，并定位研发任务 | 点击只显示“BUG-0035 未关联 tasks.md，无法打开研发任务。” | 按钮仅查 Issue 文档，未查关联 Change | Firefox 点击、抽屉状态、代码路径、返修后 1440px/390px 复测 | 本次修复 | 用户反馈；Firefox 当前页面；`openTasksAt` 与 `relatedChangeDocumentGroups` |
| 当前页面取证二（无新增附件） | 同上，测试 7/7 | 同一卡片测试按钮 | 打开同一 Change `tasks.md`，定位自动化测试 | 点击只显示“BUG-0035 未关联 tasks.md，无法打开自动化测试。” | 与研发共用失效查找路径 | Firefox 点击、抽屉状态、网络读取摘要、返修后复测 | 本次修复 | Firefox 当前页面；`openTasksAt` |
| 当前页面取证三（对照） | 同一卡片 Change 组 | `tasks.md` 文档按钮 | 原文可通过右侧抽屉读取 | 点击后抽屉成功加载真实 `tasks.md` | 服务端读取与文档本身正常 | Firefox 点击、抽屉题头与正文 | 保持现有读取路径；让进度按钮复用该文档身份 | Firefox 当前页面；Change 组 `tasks.md` 按钮 |

动作按钮族预检：研发 → Markdown drawer → Change `tasks.md` → 研发章节；测试 → 同一 drawer → Change `tasks.md` → 自动化测试章节；人工验收 → Markdown drawer → Issue `acceptance.md` → 无任务章节定位。三者继续使用现有按钮外观、抽屉、关闭方式和权限；不新增 modal。当前代码的测试样本把 `tasks.md` 放在 Issue 自身文档列表，掩盖了真实分组失效，本轮补关联 Change 的回归。

实施与验证：

- `openTasksAt` 对 Issue 优先选择当前关联 Change 的 `tasks.md`；只有未关联 Change 的旧卡片才回退到 Issue 文档。存在多个关联 Change 且没有当前 Change 时给出明确提示，不猜测文档来源；独立 Change 仍打开自身 `tasks.md`。
- 测试把 Issue 文档和 Change 文档分开构造，并覆盖研发与测试章节定位及多 Change 来源不唯一。Node 25 下以 `NODE_OPTIONS=--no-experimental-webstorage` 运行需求中心 119 项测试，全数通过；TypeScript、Docker Web 生产构建与 OpenSpec strict、中文校验通过。首次全量测试受 Node 25 实验性 Web Storage 与 jsdom 冲突影响产生超时，隔离该环境因素后复跑通过。
- Firefox 管理员真实页面重新加载新 Web 构建后，BUG-0035 研发 `11/11` 点击打开题头 `BUG-0035 · tasks.md` 的右侧抽屉，显示“已定位研发任务”；测试 `9/10` 点击打开同一文档，显示“已定位自动化测试：2. 回归验证”。桌面浏览器与 390px 响应式视口均复现上述行为；390px 宽度控件为 390，抽屉可关闭。未保存独立截图文件；浏览器实时 AX 状态、截图与自动化断言作为本次观察证据。
- 本批次复用既有授权文档读取、Markdown 预览和抽屉。API、DB、部署配置、安全权限、客户端生成与数据采集字段均无变化；BUG-0035 Issue 人工验收 `0/10` 保持待签认，归档门禁不变。

## 返修批次五：验收进度标签

来源：用户希望卡片以自动验收为主要演进方向，将“人工验收”标签改为“验收”。本轮仍在 BUG-0035 的验收进度投影范围内；返修期间用户可见阶段为研发中，Change canonical `applied` 与首次 apply 完成时间保持不变。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 历史截图与用户本轮文字反馈 | `/requirements` 深色主题，BUG-0035 验收中卡片 | 测试进度后的第三个 `.rc-progress-action` | 显示“验收 0/10”；悬浮说明当前数字口径，不暗示已接入自动验收 | 当前显示“人工验收 0/10” | 展示名称过窄，易被理解为只能人工执行 | 页面文案、按钮 aria-label/title、双视口视觉与点击抽屉 | 本次修复 | 用户本轮反馈；前轮 Firefox 页面取证；`RequirementCenterPage.tsx` |
| 历史抽屉与实现证据 | 同卡片点击第三个进度按钮 | Issue `acceptance.md` 读取及归档门禁 | 仍打开所属 Issue 验收文档；数字仍为已勾选 AC/总 AC，未完成仍阻断 | 既有抽屉和计数正确 | 改名不能悄然改变分子分母或验收结论 | 代码路径、前端回归、真实点击 | 保持既有行为，只补口径说明 | `_acceptance_readiness`、`openIssueAcceptance`、Issue AC-002/003 |

按钮族检查：研发 → Change `tasks.md` 研发章节；测试 → Change `tasks.md` 自动化测试章节；验收 → Issue `acceptance.md`。三个按钮的数字来源、颜色规则和点击目标保持不变；仅第三个按钮的可见标签、无障碍名称与缺文档提示同步改名。当前 `0/10` 只代表 Issue AC 勾选进度，自动验收结果尚未汇总进此分数。

实施与验证：

- 卡片第三个进度按钮的可见文字和无障碍名称改为“验收”；`title` 说明分子、分母依据 Issue `acceptance.md` 的 AC 勾选，自动验收结果尚未计入。缺文档提示同步改名。后端 `manual_acceptance_progress` 字段、计数逻辑、归档门禁和按钮目标均不变。
- 前端需求中心 119 项测试通过，TypeScript 与 Docker Web 生产构建通过；OpenSpec strict 和当前 Change 中文校验通过。测试同时断言按钮名称、口径说明与打开 Issue 文档。
- Firefox 管理员在本地 `/requirements` 新 Web 构建中，390px 和 1440px 响应式视口均观察到 BUG-0035 “验收 0/10”，无障碍名称和说明与可见标签一致；点击打开 `BUG-0035 · acceptance.md` 右侧抽屉，AC 保持未勾选。浏览器实时 AX 状态和截图已核对，未另存独立图片文件。一次会话过期后使用浏览器已填凭据重新登录并刷新页面，区分旧脚本与新构建；未修改验收数据。
- 视觉与数据边界：只缩短进度标签，既有 `.rc-progress-action`、`.rc-progress-label`、`.rc-progress-value` 样式和危险色规则不变。Mock/API 边界、OpenAPI、DB、权限、部署配置、对象存储和数据采集字段均无变化；自动验收结果接入仍属后续能力，不由本轮改名假定已实现。

## 返修批次六：存量表格 AC 迁移

用户已选择统一将存量 Issue `acceptance.md` 的表格 AC 迁为可计数复选框。当前后端统一解析器只识别 `- [ ] AC-001` 形式；BUG-0033 的 AC-001～011 均在表格中且 `acceptance_status: pending`，实际投影为 `(0, 0, 验收结论待核实)`。BUG-0026 先前只迁移了自身文档，未改产品解析器。本次属于既有 BUG-0035 验收投影格式偏差，保持后端单一计数规则。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户 2026-10-11 BUG-0033 卡片截图 | `/requirements`，深色主题，BUG-0033 验收中卡片 | 测试后的验收区域 | 待复验 AC 可计数并显示“验收 0/11”，点击打开 Issue `acceptance.md` | 显示红色“验收结论待核实”，无验收分数 | 表格 AC 不匹配复选框解析器 | 对照截图、Issue 文档、`_acceptance_readiness` 返回值与迁移后双视口页面 | 迁移文档，不从表格“通过”推断签认 | 用户截图；`requirement_center.py`；BUG-0033 `acceptance.md` |
| 同一截图与当前实现 | 文档分组及任务进度 | Issue/Change/Sprint 入口、研发测试数字、归档门禁 | 迁移只改变验收计数来源；保留待签认阻断 | 文档入口和任务进度已显示 | 无布局或组件行为偏差 | 现有卡片与后端投影核对 | 保留现有 UI、API 和门禁 | 用户截图；Change 设计与测试 |

存量盘点：未归档 Issue 中，BUG-0028 有 8 条、BUG-0029 有 6 条、BUG-0033 有 11 条、BUG-0034 有 5 条表格 AC，四份均没有复选框；BUG-0025、0026、0035 与 REQ-0027 已有复选框。归档 Issue 为历史事实，本轮不迁移。迁移只增加独立 AC 清单，原场景表和证据原文保留；所有新增 AC 均未勾选，原 `acceptance_status` 不变。BUG-0028/0034 尚未进入验收阶段，先规范未来投影入口。

迁移后真实页面刷新：BUG-0029 显示“验收 0/6”，BUG-0034 显示“验收 0/5”；BUG-0033 后端已返回 11 项待验证，但页面仍只出现红色阻断文案。代码定位到 `visibleManualAcceptanceProgress` 需要 `testProgress` 才返回数据，进度容器也只由研发或测试进度触发。BUG-0033 的 Change 只有研发任务分母，没有自动测试任务分母；此为与表格格式并列的已确认展示条件缺陷。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户截图及迁移后 Firefox 页面 | BUG-0033 验收中、无测试进度 | 测试后的验收按钮和红色提示 | 独立显示可点击“验收 0/11”，未勾选 AC 不重复红字 | 迁移后仅显示“验收未完成：11 项待验证”红字 | 前端将验收按钮依赖测试分母 | 对照后端 `(11, 11)`、浏览器 AX、组件条件与聚焦回归 | 移除测试依赖，进度容器接受验收进度单独触发 | `RequirementCenterPage.tsx`、`requirement-center.test.tsx` |

实施：四份 Issue 文档新增同编号、全部未勾选的 AC 清单，保留原表格与 frontmatter 状态；`RequirementCenterPage.tsx` 仅调整两个展示条件，不改变数字来源、归档门禁或抽屉目标。前端新增 BUG-0033 型“有 AC、无测试分母”回归，断言验收 0/11、无重复红字、归档入口仍隐藏及点击打开 Issue 文档。后端现有解析器对四份文档分别返回 `(8,8)`、`(6,6)`、`(11,11)`、`(5,5)`；没有启用表格解析或把隔离回归自动映射为完成。BUG 子文档扫尾：四份 acceptance 文档与 BUG-0035 acceptance 已更新；各 BUG 主文档、根因与 workaround 未改变故障事实，无需同步；Issue trace 的状态投影由 Workflow Sync 维护。API/DB/权限/部署配置/客户端生成、请求日志与 Task Trace 字段无变化，产品数据采集声明仍适用，新增采集为 N/A。

验证：前端需求中心 120 项、Web TypeScript、Docker Web 生产构建、后端需求中心 80 项、OpenSpec strict、当前 Change 中文与标题校验均通过；四份文档的表格 AC 编号与复选框编号逐一相等且计数与预期一致。Web 镜像重建后仅重建本地 web 容器，未停止 backend、Chat worker 或治理控制器；浏览器刷新后 BUG-0033 在桌面及 390px 响应式视口均显示“验收 0/11”，无测试进度按钮、不再显示重复红字、无归档动作。点击验收打开 `BUG-0033 · acceptance.md`，正文包含未勾选 AC-001～011 和保留的原表格；BUG-0029、0034 同页分别显示 0/6、0/5。BUG-0028 当前仍在已评审阶段，因此不提前展示验收进度。没有独立保存用户会话截图；证据为浏览器实时页面与抽屉无障碍树、产品构建和聚焦测试。人工签认与 Change 归档仍待后续复验。

验证限制与同步：全仓 `validate-design-system.py` 报 178 项既存违规，跨多个未改文件；本次两处前端改动没有新增控件或样式。Sprint Scope 与 Agent 上下文预算校验通过。Workflow Sync `opsx.modify` 解析 `sprint-009`，更新 1、错误 0、阻断 0，BUG-0035 验收保持 pending；AI Usage hook 为 warning/unavailable，未发现可归属 command run。当前返修投影回到验收中；Change canonical `applied` 与首次完成时间未回退。

## 复验批次七：BUG-0035 逐项技术签认

2026-10-11 07:27，按用户指令复核 linked Issue AC-001～011。平台超级管理员在本地 Web v0.1.0 的 Firefox `/requirements` 实际看到 BUG-0035 研发 14/14、测试 13/13、验收 0/11，Issue/Change/Sprint 三组入口；BUG-0033 0/11 且无测试分母，BUG-0029 0/6、BUG-0034 0/5，BUG-0025 18/52。点击 BUG-0035 研发按钮出现 `BUG-0035 · tasks.md` 抽屉题头；后续浏览器切回另一 Chat 页面，不能把短暂“Markdown 加载中”当作文档正文读取成功，完整点击证据沿用返修批次四的双视口记录。

本轮聚焦回归：后端 `test_governance_board.py` 与 `test_governance_scope.py` 共 88 项通过；前端 `requirement-center.test.tsx` 120 项通过。前端首跑因 Node 25 实验性 Web Storage 使 `localStorage.clear` 初始化失败，使用 `NODE_OPTIONS=--no-experimental-webstorage` 复跑全部通过。四份存量文档复选框分别为 BUG-0028 8、BUG-0029 6、BUG-0033 11、BUG-0034 5 项，均未勾选；根因证据校验通过。

逐项预期、实际、权限/响应摘要、证据入口及签认人见 linked Issue `acceptance.md` 的“2026-10-11 逐项复验与签认”。Codex 技术签认 AC-001～008、AC-011，共 9/11。AC-009 缺全阶段双视口真实视觉矩阵及独立 Change 当前观察；AC-010 缺本轮 BUG-0025 Chat 归档命令的真实阻断响应。这两项保持未勾选，整体 `acceptance_status: pending`，不执行归档或代填产品团队最终结论。本轮仅更新验收记录；实现、规格、OpenAPI、DB、权限、部署、客户端生成、数据采集字段均未变。

签认落盘后，直接由当前治理服务读取仓库投影：BUG-0035 stage=acceptance，研发 14/14、测试 14/14、验收 9/11，待验证 2 项；归档动作的 `disabled_reason` 为“验收未完成：2 项待验证，请查看 acceptance.md”。这属于服务端当前读模型结果，不等同于 Chat 归档命令的真实拒绝响应；后者仍归 AC-010 待验。

## 返修批次六：AC-010 归档负向门禁与同轮判定

旧正式 Chat 轮次仅因任务和规格合并失败而退出，不能证明验收门禁。BUG-0025 的 AF-041 已在独立真实产品副本以新卡片候选取得同轮 `applied/verified`；修正九条 delta Requirement 分类后，临时副本 OpenSpec 归档合并通过。此批次在归档脚本执行 OpenSpec 合并前，独立检查关联 Issue 的 `acceptance_status` 与 AC 勾选；缺失、未签认或仍有待验项返回 `ACCEPTANCE_GATE_BLOCKED` 并保持原目录。独立 Change 不受 Issue 门禁影响。

自动验收 `product_turn` 增加预期退出码和门禁标记条件，AC-010 要求同轮目标命令返回退出码 1、结果含 `ACCEPTANCE_GATE_BLOCKED`，且 Change 仍在 active。只记录布尔标记、退出码与事件序号，不入仓保存工具原始输出。正式 BUG-0025 关联 Chat 轮次 `9bffe2e8-bb23-4559-b132-b4feb6856ef6` 完成，序号 38 的归档脚本返回 `ACCEPTANCE_GATE_BLOCKED issue_acceptance_pending checked=24 total=52`、退出 1；BUG-0025 保持待验，Change 未归档。完整验收包 `evidence/acceptance/20261012174521381442-836220d3/` 为 11/11 passed，readiness ready，Workflow Sync `opsx.accept` 将 BUG-0035 验收状态同步为 passed。

聚焦验证：`tests/unit/test_opsx_acceptance.py` 8 passed；正式 BUG-0025 门禁脚本阻断、BUG-0035 已签认门禁脚本放行；两项 Change OpenSpec strict、中文与标题校验、`git diff --check` 通过。自动验收摘要生成器补齐中文业务标题，避免新证据包阻断后续预检。API/DB schema、Web 请求、对象存储、部署、客户端生成均未变化；affected_layers 为 Agent Workflow、归档脚本与既有 Chat execution.tool，`product_data_collection_observability: applicable`，校验仅使用脱敏状态与同轮事件。AI Usage hook 执行但无可归因会话记录，记为 warning，不把缺失统计写成成功用量。

## 返修批次七：验收卡片已存在 Change 文档误报缺少

用户 2026-10-12 提供 BUG-0035 验收中卡片截图。截图与当前源码构成以下逐项视觉对照；截图只作为本次对话证据，不复制含会话信息的原图。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户截图 #1 | `/requirements`，验收中，BUG-0035，深色主题；截图未标明视口 | Change 文档组 | `proposal.md`、`spec.md`、`design.md`、`tasks.md` 可见且可按原权限打开 | 四个入口均已显示 | 无入口缺失；文档来源为关联 Change | 截图文字与 Change 目录、后端文档投影核对 | 保留现有文档组 | 用户本次对话截图；`requirement_center.py` `_change_document_names` |
| 用户截图 #1 | 同上 | 卡片红色阻断提示 | 已显示的 Change 文档不应提示缺少；真实验收阻断仍按服务端结论显示 | “缺少 proposal.md、spec.md、design.md、tasks.md” | 验收阶段从 Issue 自身清单判断 Change 文档，形成自相矛盾的文案 | 前端 `missingDocs`/`blockedTip`、Change 文件存在性、组件回归；运行态复核视口和 DOM | 本次修复验收阶段文档来源判断 | 用户本次对话截图；`RequirementCenterPage.tsx`；本批次测试输出 |

复现条件：BUG-0035 的 Issue 文档清单不含这四个 Change 文档，而关联 Change 的 `document_entries` 含四个入口；卡片阶段为 `acceptance`，服务端没有其他 `blocked` 原因时，前端生成上述红字。根因为 `missingDocs` 只在待开发和研发中阶段使用 Change 清单，验收中回退到 Issue 清单。影响验收卡片提示可信度，不改变实际文档可读性或归档门禁。

实施：`missingDocs` 将验收阶段纳入关联 Change 文档检查，继续让 `trace.md` 归 Issue 自身判断；保留 `blockedTip` 对服务端真实阻断原因的优先级。组件回归覆盖四份 Change 文档齐全时无缺失红字，以及确实缺少 `tasks.md` 时仍提示缺少。没有调整 CSS、布局、权限或归档操作。

验证：前端需求中心 122 项聚焦测试和 TypeScript 通过；OpenSpec strict、当前 Change 中文及标题校验通过。隔离 Vite 预览使用合成 API，Chrome 在 1440×900 与 390×844 检查同一 BUG-0035 验收卡片：四份 Change 文档均可见，`.rc-blocked` 为 0 项；卡片 computed width 为 300px，文档区 `scrollWidth=clientWidth=264px`，页面 `body.scrollWidth` 分别为 1440px 与 390px。合成预览不是正式服务部署；正式 Firefox `/requirements` 仍运行旧 Web 包，返修前可观察到四份文档已显示但红字仍报缺少。当前未重建常驻 Chat 平台容器，真实产品修复后观察保留为后续验收事项。

增量验收：本次输入指纹变更后先执行完整检查，10 项通过、AC-010 因未指定只读产品数据库暂时 blocked；随后指定本地 SQLite 并仅复验 AC-010，复用其余有效结果。最新证据包 `evidence/acceptance/20261012182141076273-a4e250f8/` 为 11/11 passed，`--readiness` 返回 ready、stale 为空。Workflow Sync `opsx.accept` 错误 0，将 BUG-0035 `acceptance_status` 同步为 passed。这里的 ready 是当前计划的自动化归档就绪结论；常驻 Web 仍需部署新构建后复核本次卡片显示，不将合成预览冒充产品上线证据。Change 保持 applied，未归档。

归档前运行态复核（2026-10-13 08:24:00，Firefox，常驻 `localhost:39002/requirements`）：页面刷新后成功同步看板，BUG-0035 验收中卡片仍显示 Issue、Change、Sprint 三组，Change 组的 `proposal.md`、`spec.md`、`design.md`、`tasks.md` 均在；卡片显示研发 16/16、测试 15/15、验收 11/11、“完成 / 归档”可用，未出现“缺少 proposal.md、spec.md、design.md、tasks.md”误报。点击 Change 组 `proposal.md` 后，右侧抽屉题头为 `BUG-0035 · proposal.md`，安全预览加载正文成功。此为当前刷新页面的实际观察，补齐本批次常驻产品复核；隔离双视口阶段矩阵仍以 `evidence/acceptance/phase-matrix-1440-390.md` 为依据，不将本次桌面视口观察称为移动视口复验。
