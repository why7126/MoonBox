---
change_id: add-space-creation-join-application-flow
type: add
status: modified
source_requirement: REQ-0019-space-creation-join-application-flow
sprint: sprint-003
created_at: 2026-08-15 11:08:25
updated_at: 2026-08-16 10:15:00
prototype_refs:
  - path: issues/requirements/review/REQ-0019-space-creation-join-application-flow/prototype/web/prototype.html
    role: html-structure
  - path: issues/requirements/review/REQ-0019-space-creation-join-application-flow/prototype/web/context.md
    role: prototype-context
ui_contract_status: implemented
ui_skeleton_status: completed
visual_acceptance_1440: completed
computed_style_evidence: completed
mock_api_boundary: real-api
req_final_consistency: completed
---

# Trace

## 来源

- REQ: `REQ-0019-space-creation-join-application-flow`
- Sprint: `sprint-003`
- Knowledge refs:
  - `docs/knowledge-base/best-practices/prototype-driven-ui-gate.md`
  - `docs/knowledge-base/retrospectives/sprint-002-retrospective.md`

## Conflict Resolution

- 附件 v1.0.1 废弃“加入空间”能力；本 Change 返修后只保留前台创建空间申请。
- 2026-08-15 14:31:00 用户反馈重新确认创建空间需平台管理员审批后才可使用；该口径覆盖此前“直接创建并进入空间”的返修口径。
- 2026-08-15 14:52:00 用户反馈要求前台创建空间弹窗输入限制、校验和到期时间控件与后台空间管理一致；该口径覆盖此前原型默认 5 人、1GB、长期有效和日期输入。
- 2026-08-15 15:03:00 用户截图确认创建空间弹窗中到期时间选择器在 1440x900 下向下展开超出可视区域；本次返修以视口碰撞处理为准。
- 2026-08-15 15:12:00 用户反馈时间控件不会消失、面板会出现滚动条、弹窗右上角关闭按钮看不清；本次返修以明确收起动作、无面板滚动条和关闭按钮可见性为准。
- 2026-08-15 15:20:00 用户反馈时间控件“取消 / 确定”偏重；该口径覆盖 15:12 的面板内按钮方案，最终交互为点击 3 个快捷按钮后应用并关闭，点击控件外区域关闭并保留当前值。
- 2026-08-15 16:25:00 用户验收确认点击时间控件外部区域后面板未消失；根因证据来自代码路径：时间控件使用 document 冒泡阶段 `mousedown` 监听，而创建空间弹窗内部 `onMouseDown.stopPropagation()` 会拦截弹窗内非控件区域点击。
- 2026-08-16 10:15:00 用户确认创建空间弹窗审批提示与副标题整合更好；本次只优化文案层级和重复信息，不改变审批流程、接口或结果态。
- 后台空间申请审批是正式空间创建事实源。
- 空间切换真实数据复用 REQ-0018，审批通过后触发上下文刷新。
- Prototype 作为返修事实源；最终验收以 Change design、acceptance、1440px 视觉证据、computed style、Mock/API 边界和 REQ 最终一致性回填共同为准。

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-15 11:08:25 | req.opsx | 创建 OpenSpec Change，状态为 proposed。 |
| 2026-08-15 11:42:00 | opsx.apply | 完成后端 catalog 空间申请 API、申请表扩展、后台 join 审批生效、需求中心申请弹层、API/DB 文档同步与测试。 |
| 2026-08-15 12:27:30 | opsx.modify | 按附件 v1.0.1 返修：删除前台加入空间能力，前台入口只保留创建空间，创建成功直接生成可进入空间。 |
| 2026-08-15 12:52:00 | opsx.modify | 补齐 REQ 目录遗漏子文档：`business-flow.md`、`user-stories.md`、`prototype/web/prototype.html` 均收敛为仅创建空间。 |
| 2026-08-15 13:30:00 | opsx.modify | 按附件原型优化创建空间弹窗 UI：双列布局、单位内嵌、负责人卡、有效期行和底部按钮可见性。 |
| 2026-08-15 14:31:00 | opsx.modify | 创建空间弹窗继续优化：提交待审批申请、审批说明、必填红星、删除负责人卡、到期日期另起一行、单位与后台一致。 |
| 2026-08-15 14:52:00 | opsx.modify | 创建空间弹窗限制和时间控件返修：对齐后台成员/存储/AI Tokens 边界，AI Tokens 不显示单位，到期时间默认本季度末并复用后台日期时间选择器。 |
| 2026-08-15 15:03:00 | opsx.modify | 创建空间弹窗到期时间选择器返修：下方空间不足时向上展开，并保持面板在视口内。 |
| 2026-08-15 15:12:00 | opsx.modify | 创建空间弹窗继续返修：到期时间选择器增加取消/确定并可收起，移除面板自身滚动条，增强右上角关闭按钮可见性。 |
| 2026-08-15 15:20:00 | opsx.modify | 创建空间弹窗时间控件交互轻量化：移除取消/确定，快捷按钮应用后关闭，点击外部关闭并保留当前值。 |
| 2026-08-15 16:25:00 | opsx.modify | 修复到期时间控件外部点击关闭失效：外部点击监听改为 capture 阶段，并修复日历图标二次点击被 input focus 重新打开的问题。 |
| 2026-08-16 10:15:00 | opsx.modify | 创建空间弹窗文案优化：将审批提示整合到副标题，删除表单上方重复提示行。 |

## 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户附件 Image #1 | 需求中心 1440px 深色主题，创建空间弹窗默认表单 | 附件原型 vs 历史视觉证据 `REQ-0019-create-space-modify-1440.png` | 约 780px 弹窗，字段紧凑双列，成员/存储与 AI Tokens/有效期两行双列，单位在输入框右侧，底部取消/创建按钮完整可见 | 历史实现弹窗较高，字段说明文字撑高，AI Tokens 与有效期不成原型节奏，底部区域下探 | 高度、列编排、单位展示、负责人卡、底部操作 | 截图对照、DOM/CSS 检查、computed style | 本次修复 | `tmp/visual-evidence/REQ-0019-create-space-ui-refine-1440.png`、`tmp/visual-evidence/REQ-0019-create-space-ui-refine-style.json` |
| 用户补充 | 负责人卡 | 用户要求 vs 实现 | 不展示邮箱，右侧保留“创建后不可在此修改” | 返修后负责人卡仅展示头像、姓名和右侧只读说明 | 无 | DOM/CSS 检查 | 已按补充要求修复 | `src/web/src/pages/catalog/RequirementCenterPage.tsx` |
| 用户反馈 14:31 | 创建空间弹窗 | 用户反馈 vs 当前实现 | 说明审批后才可使用；必填红星；删除负责人卡；到期日期在 AI Tokens 下方；单位与后台空间管理一致 | 当前实现已改为待审批申请、红星、无负责人卡、AI Tokens 使用 token 数值 | 行为、文案、布局、单位 | 测试、截图、computed style、API 测试 | 本次修复 | `tmp/visual-evidence/REQ-0019-create-space-approval-ui-1440.png`、`tmp/visual-evidence/REQ-0019-create-space-approval-ui-style.json` |
| 用户反馈 14:52 | 创建空间弹窗 | 用户反馈 vs 后台空间管理表单 | 输入限制和校验与后台一致；AI Tokens 不显示 `Tokens` 单位；到期日期改为到期时间，默认本季度最后一天 23:59:59，控件与后台一致 | 返修前成员/存储仍为 5/1 小范围默认，AI Tokens 有右侧单位，到期字段为日期输入 | 默认值、边界、单位、时间控件 | 代码对照、测试、build、computed style | 本次修复 | `tmp/visual-evidence/REQ-0019-create-space-quota-datetime-1440.png`、`tmp/visual-evidence/REQ-0019-create-space-quota-datetime-style.json` |
| 用户截图 15:03 | 需求中心 1440x900 深色主题，创建空间弹窗，到期时间选择器打开 | 用户截图 vs 当前实现 | 时间选择器完整位于可视区域内，可完成日期、时间和快捷选择 | 返修前面板向下展开，底部超出视口，无法完成选择确认 | 浮层位置、可视区域、交互可达性 | Playwright 视觉采样、computed style、Vitest 近底部定位断言 | 本次修复 | `tmp/visual-evidence/REQ-0019-datetime-collision-1440x900.png`、`tmp/visual-evidence/REQ-0019-datetime-collision-style.json` |
| 用户反馈 15:12 | 创建空间弹窗，到期时间选择器打开，弹窗右上角 | 用户反馈 vs 当前实现 | 时间控件可明确取消或确定并收起；时间面板不出现自身滚动条；右上角关闭按钮清晰可见 | 返修前无确定/取消，面板设置 `overflow:auto`，关闭按钮视觉权重不足 | 收起动作、滚动条、关闭按钮对比度 | Vitest、Playwright 视觉采样、computed style | 本次修复 | `tmp/visual-evidence/REQ-0019-datetime-actions-1440x900.png`、`tmp/visual-evidence/REQ-0019-datetime-actions-style.json` |
| 用户反馈 15:20 | 创建空间弹窗，到期时间选择器打开 | 用户反馈 vs 15:12 实现 | 时间面板不展示取消/确定；点击 3 个快捷按钮后应用并关闭；点击控件外区域关闭并保留当前值；无面板滚动条；右上角关闭按钮清晰 | 返修前面板内有取消/确定 | 交互重量、退出方式 | Vitest、Playwright 视觉采样、computed style | 本次修复 | `tmp/visual-evidence/REQ-0019-datetime-lightweight-1440x900.png`、`tmp/visual-evidence/REQ-0019-datetime-lightweight-style.json` |
| 用户反馈 16:25 | 创建空间弹窗，到期时间选择器打开，点击弹窗内非控件区域 | 用户反馈 vs 当前实现 | 点击时间控件外部区域后面板关闭，并保留当前时间值；日历图标再次点击不应被 focus 重新打开 | 返修前弹窗内 `stopPropagation` 导致 document 冒泡监听收不到外部点击；图标关闭后可能因 input focus 重新打开 | 外部点击事件阶段、图标 toggle 时序 | 代码路径、Vitest 交互测试、build；Playwright 视觉采样因本地 Chromium 权限未完成 | 本次修复 | `src/web/src/requirement-center.test.tsx` |
| 用户反馈 10:15 | 创建空间弹窗默认表单 | 当前实现 vs 用户文案建议 | 副标题一次性说明空间隔离、提交审批、审批通过后创建空间并分配负责人；表单上方不再重复展示审批提示行 | 返修前副标题和 hint 相邻重复说明审批 | 文案重复、信息层级、表单顶部密度 | DOM 文案断言、prototype 对照、REQ/OpenSpec 一致性扫描 | 本次修复 | `src/web/src/requirement-center.test.tsx` |

## 验证证据

- Backend: `uv run pytest tests/integration/api/test_admin_spaces.py`，7 passed。
- Frontend: `pnpm --dir src/web test -- --runInBand`，89 passed。
- Build: `pnpm --dir src/web build`，通过 TypeScript 与 Vite 构建。
- Visual 1440px: `tmp/visual-evidence/REQ-0019-space-application-1440.png`。
- Computed style: modal width `760px`、border radius `14px`、background `rgb(18, 20, 43)`；input height `40px`、radius `7px`；primary action height `34px`、background `rgb(203, 163, 92)`。
- Modify Backend: `uv run pytest tests/integration/api/test_admin_spaces.py`，7 passed。
- Modify Frontend: `pnpm --dir src/web test -- --runInBand`，89 passed。
- Modify Build: `pnpm --dir src/web build`，通过 TypeScript 与 Vite 构建。
- Modify Visual 1440px: `tmp/visual-evidence/REQ-0019-create-space-modify-1440.png`。
- Modify Computed style: modal width `760px`、border radius `14px`、background `rgb(18, 20, 43)`；input height `40px`、radius `7px`；owner card height `68px`、radius `8px`；period option height `45px`、radius `7px`；primary action height `34px`、background `rgb(203, 163, 92)`。
- Modify Docs Consistency: REQ 子文档残留扫描确认 `business-flow.md`、`user-stories.md`、`prototype/web/prototype.html` 已不再将加入空间、精准搜索、撤回或重新提交作为正向功能流程；相关词仅保留在非目标边界说明中。
- UI Refine Frontend: `pnpm --dir src/web test -- --runInBand`，89 passed。
- UI Refine Build: `pnpm --dir src/web build`，通过 TypeScript 与 Vite 构建。
- UI Refine Visual 1440px: `tmp/visual-evidence/REQ-0019-create-space-ui-refine-1440.png`。
- UI Refine Computed style: modal `780px × 761px`、bottom `831px`；grid columns `349px 349px`；owner card `714px × 68px`；input `349px × 40px` 且 padding-right `42px`；radio `12px × 12px`；period options `349px × 40px`；actions `714px × 92px`；primary action `93px × 34px`；`modalVisibleBottom=true`、`actionVisibleBottom=true`、`hasLegacyTabs=false`。
- Approval UI Backend: `uv run pytest tests/integration/api/test_admin_spaces.py tests/integration/api/test_requirement_center.py`，15 passed。
- Approval UI Frontend: `pnpm --dir src/web test -- --runInBand`，89 passed。
- Approval UI Build: `pnpm --dir src/web build`，通过 TypeScript 与 Vite 构建。
- Approval UI Visual 1440px: `tmp/visual-evidence/REQ-0019-create-space-approval-ui-1440.png`。
- Approval UI Computed style: modal `780px × 757px`、bottom `829px`；grid columns `349px 349px`；AI Tokens input `349px × 40px`；date row `349px × 64px`；required star color `rgb(248, 113, 113)`；actions `714px × 92px`；primary action `93px × 34px`；`modalVisibleBottom=true`、`actionVisibleBottom=true`、`hasOwnerCard=false`。
- Quota/Datetime Backend: `uv run pytest tests/integration/api/test_admin_spaces.py tests/integration/api/test_requirement_center.py`，15 passed。
- Quota/Datetime Frontend: `pnpm --dir src/web test -- --runInBand src/requirement-center.test.tsx`，89 passed。
- Quota/Datetime Build: `pnpm --dir src/web build`，通过 TypeScript 与 Vite 构建。
- Quota/Datetime Visual 1440px: `tmp/visual-evidence/REQ-0019-create-space-quota-datetime-1440.png`。
- Quota/Datetime Computed style: modal `780px × 744.3125px`、bottom `822.15625px`；AI Tokens `aiHasUnitField=false`；到期时间控件 `349px × 40px`；actions bottom `791.15625px`；`modalVisibleBottom=true`、`actionVisibleBottom=true`。
- Datetime Collision Frontend: `pnpm --dir src/web test -- --runInBand src/requirement-center.test.tsx`，89 passed；覆盖 1440x900 近底部打开时 `data-placement=top` 且面板 top 小于输入框 top。
- Datetime Collision Build: `pnpm --dir src/web build`，通过 TypeScript 与 Vite 构建。
- Datetime Collision Visual 1440x900: `tmp/visual-evidence/REQ-0019-datetime-collision-1440x900.png`。
- Datetime Collision Computed style: viewport `1440 × 900`；placement `top`；panel top `280px`、bottom `635.78125px`、height `355.78125px`；input top `645.15625px`；`panelWithinViewport=true`、`panelOpensAboveInput=true`。
- Datetime Actions Frontend: `pnpm --dir src/web test -- --runInBand src/requirement-center.test.tsx`，89 passed；覆盖时间面板内“取消 / 确定”存在，点击确定后收起。
- Datetime Actions Build: `pnpm --dir src/web build`，通过 TypeScript 与 Vite 构建。
- Datetime Actions Visual 1440x900: `tmp/visual-evidence/REQ-0019-datetime-actions-1440x900.png`。
- Datetime Actions Computed style: panel top `236px`、bottom `628px`、height `392px`、overflow `visible`、`hasPanelScrollbar=false`、`hasCancel=true`、`hasConfirm=true`；close button `42px × 42px`，color `rgb(233, 238, 251)`，border `rgb(233, 238, 251)`。
- Datetime Lightweight Frontend: `pnpm --dir src/web test -- --runInBand src/requirement-center.test.tsx`，89 passed；覆盖时间面板不展示“取消 / 确定”，点击“本季度末”后应用并关闭。
- Datetime Lightweight Build: `pnpm --dir src/web build`，通过 TypeScript 与 Vite 构建。
- Datetime Lightweight Visual 1440x900: `tmp/visual-evidence/REQ-0019-datetime-lightweight-1440x900.png`。
- Datetime Lightweight Computed style: panel top `260px`、bottom `615.78125px`、height `355.78125px`、overflow `visible`、`hasPanelScrollbar=false`、`hasActionsBar=false`、`hasCancel=false`、`hasConfirm=false`；快捷按钮 3 个；close button `42px × 42px`，color `rgb(233, 238, 251)`，background `color(srgb 0.117909 0.125229 0.194771 / 0.9)`，border `rgb(233, 238, 251)`。
- Datetime Outside Close Frontend: `pnpm --dir src/web exec vitest run src/requirement-center.test.tsx`，34 passed；覆盖点击弹窗内非控件区域关闭并保留当前值、日历图标二次点击关闭、快捷按钮应用后关闭。
- Datetime Outside Close Build: `pnpm --dir src/web build`，通过 TypeScript 与 Vite 构建。
- Datetime Outside Close Visual: Playwright 1440x900 采样尝试启动 Chromium 时被本地沙箱权限拦截，两次提升权限请求未在审核时限内完成；本轮以 Vitest 交互测试和 build 作为自动化证据。
- Copy Merge Frontend: `pnpm --dir src/web exec vitest run src/requirement-center.test.tsx`，34 passed；覆盖整合副标题展示、旧审批 hint 不再展示、创建空间提交流程仍可用。
- Copy Merge Build: `pnpm --dir src/web build`，通过 TypeScript 与 Vite 构建。

## Mock/API 边界

- 自动化视觉验收可使用 Playwright route mock 需求中心 context 和创建空间响应，仅用于 UI 状态采样。
- 实现代码调用真实 API：`/api/v1/catalog/workspace-applications/create`。
- 前台不再调用加入空间、精准搜索空间、我的申请、撤回或重新提交接口。
