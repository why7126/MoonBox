---
change_id: add-capture-multimodal-candidate-review
title: Capture 图文候选审阅与确认采集
requirement_id: REQ-0029-capture-multimodal-candidate-review
iteration: sprint-007
status: applied
change_type: add
created_at: '2026-09-15 00:19:14'
updated_at: 2026-09-16 23:48:00
prototype_refs:
- issues/requirements/review/REQ-0029-capture-multimodal-candidate-review/prototype/web/prototype.html
- issues/requirements/review/REQ-0029-capture-multimodal-candidate-review/prototype/web/context.md
- issues/requirements/review/REQ-0029-capture-multimodal-candidate-review/prototype/web/prototype-qa.json
prototype_gate:
  decomposition: done
  conflict_resolution: design.md
  ui_contract: design.md
  ui_skeleton: done
  visual_acceptance_1440: done
  computed_style: done
  mock_api_boundary: design.md
  req_final_consistency: done
product_data_collection_observability:
  status: applicable
  affected_layers:
  - usage_events
  - request_logs
  - task_traces
  - task_trace_spans
  reason: 图文整理、审阅与批次确认涉及Web/API/DB/对象存储及Agent Workflow，四层适用。
  validation: 后端事件、请求与任务关联、脱敏降级及保留检查已完成；真实浏览器四层关联因一次性账号授权审批受阻，仍待补验。
execution:
  schema_version: 1
  started_at: 2026-09-15 00:32:12
  completed_at: 2026-09-15 15:58:00
  last_event: opsx.modify
---
# Capture Change 追溯

来源 REQ-0029，评审 approved 已留痕，当前 in_sprint / sprint-007。Readiness Partially Ready，原型拆解齐全，真实实施证据待任务阶段。

## 设计与证据

- Conflict Resolution、D1 DS策略、UI Contract、UI Skeleton和动作矩阵见design.md。
- 参考PNG：REQ prototype/web/review-1440.png、review-light-1440.png、result-1440.png、review-390.png，仅原型演示。
- 实施证据清单：1440px首轮Skeleton；1440px深浅主题输入/审阅/结果/失败/冲突；1024/390px与矮视口；动作modal/焦点/外部点击；computed-style摘要。全部pending，后续写入evidence/。
- 真实模型、上传、编号恢复与MySQL验证pending；Mock只用于Skeleton及合成回归，不替代真实观察。
- 最终REQ六件套与prototype一致性pending，任务8.2负责回填。

## 验证记录

- OpenSpec CLI 四项 artifacts 均 done；严格校验通过，此状态仅指设计材料齐备，实施任务全部未勾选。
- 当前 Change 中文校验通过，全仓非当前 Change 中文残留为零；Change 身份与 sprint-007 Scope 校验通过。
- Workflow Sync req.opsx 成功，已回填 REQ trace、注册表/看板、Sprint changes 与 scope_estimates.change；execution schema v1 的开始/完成时间均为 null。
- Agent 上下文预算校验通过。全仓目录校验报告根目录存在未登记 .vite/；该目录不属于本次产物，保留并作为仓库级 warning。
- AI Usage hook：usage_mode unavailable，command_run_count 0，Sprint snapshot skipped；未发现可归属会话统计，不影响设计链路。
- 本次仅改文档与追溯，业务代码、API/DB/媒体/浏览器/模型测试未执行，留在 tasks 的实施验收门禁。

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-15 00:19:14 | /req-opsx | 建立提案、设计、两份delta规格和实施验收任务，承接sprint-007。 |

## Apply 中断续接检查点（进行中）

- 已执行 opsx.start 与 opsx.progress；未执行 opsx.apply，真实浏览器账号授权和完整 UI 验收门禁未满足。
- 用户已确认正式 UI 方向为“单一 MD 编辑器 + 内嵌图片/文本文件材料块”。生产入口已接入 `CaptureDialog`：输入态只有一个 MD 编辑器；`.txt`/`.md` 文件导入为编辑器来源块；图片通过私有材料上传并在同一材料流展示；候选审阅、编辑/改类型、合并、拆分、删除、来源、确认、结果和重试组件已实现。
- 已修复整理前保存竞态：若自动保存仍在进行，`AI 整理候选` 会等待最新保存完成并使用最新 revision，避免以旧版本启动整理。
- Skeleton证据：`evidence/skeleton-1440-dark.png`、`skeleton-1440-light.png`、`skeleton-390-light.png`、`skeleton-styles.json` 已按单一 MD 编辑器方向重生成并通过脚本校验。
- 后端、模型、存储、确认幂等、恢复和观测的既有局部验证保持有效：SQLite 78项、MySQL 39项、最终后端47项、真实 MinIO/模型读取与 12 组整理质量对照通过。
- 前端验证：TypeScript 通过；`capture-dialog.test.tsx` 3项通过，覆盖单一 MD 编辑器、文本文件导入、候选确认前不编号及保存竞态；`capture-api.test.ts` 3项通过；需求中心统一编辑器入口聚焦测试通过。
- 治理验证：`openspec validate add-capture-multimodal-candidate-review --strict`、当前 Change 中文校验、上下文预算和目录结构校验通过。
- 真实浏览器验收限制：沙箱允许只读查询后发现最新浏览器草稿为空、无材料和整理任务；尝试创建/重置一次性本地管理员验收账号被自动审批拒绝，理由是会修改本地数据库访问控制和临时凭证。因此 7.3、7.5、7.6 和 8.3 保持未完成，等待用户提供已有本地验收配置入口或明确授权一次性账号准备方式。

规范优化建议：将“已有本地验收配置入口”沉淀为部署验收前置项，并把一次性账号准备改成受控 fixture 脚本，避免 apply 收尾依赖手工数据库改权。


## 验收返修记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-16 09:40:00 | /opsx-modify | 按用户附件 `layout-4-console-workbench.html` 复刻 Capture 弹窗布局：居中三阶段工作台、来源材料抽屉、候选单列 board、左侧编号栏、卡片内联编辑和结果卡片；API/DB/编号/幂等契约不变。 |

验证摘要：TypeScript、CaptureDialog/入口单测和 1440/390px 合成骨架验收通过。真实多状态脚本受本地项目只读上下文限制，未作为通过证据；限制已写入 `acceptance-fixes.md`。

| 2026-09-16 10:00:00 | /opsx-modify | 收敛 Capture 字体层级：主标题、审阅标题、候选标题、正文、编号、按钮和 Badge 整体降一级，保留布局和数据契约；证据见 `acceptance-fixes.md`。 |

| 2026-09-16 10:50:00 | /opsx-modify | 按附件比例回调 Capture 字体层级：候选编号、候选标题、正文、Badge、主按钮、副标题和编辑器文本贴近附件 CSS；保留 MoonBox 字体族和 token；证据见 `acceptance-fixes.md`。 |

| 2026-09-16 11:35:00 | /opsx-modify | 输入态附件结构复刻：来源材料改为紧凑 pill chip；材料抽屉、MD 编辑器、草稿状态和删除草稿放回同一 card；`AI 整理候选` 改为 card 外全宽主按钮；关闭按钮改为轻量文字按钮。验证见 `acceptance-fixes.md`。 |

| 2026-09-16 12:12:00 | /opsx-modify | Markdown 抽屉字体密度对齐：MD 输入区改为抽屉同款 monospace 12.5px；材料 chip、草稿状态、按钮、候选正文和 Badge 收敛到抽屉阅读/编辑密度；主标题降至 24px 左右；布局和数据流程不变。验证见 `acceptance-fixes.md`。 |


| 2026-09-16 13:30:00 | /opsx-modify | 按 Markdown 右侧抽屉统一 Capture 弹窗字体 family、主标题 19px、顶部 kicker、审阅态“AI 审阅结果”与候选统计、候选类型/分级双标签、危险色删除，并移除候选说明 notice；布局和数据流程不变。验证见 `acceptance-fixes.md`。 |

| 2026-09-16 14:20:00 | /opsx-modify | 删除 Capture 弹窗顶部主标题和副标题，仅保留 `新建 CAPTURE` crumb、关闭按钮和三点式步骤条；输入说明迁移到 MD 编辑器 placeholder；布局和数据流程不变。验证见 `acceptance-fixes.md`。 |

| 2026-09-16 14:55:00 | /opsx-modify | 按最新截图返修候选卡标题行、来源材料文案、输入外框和二次弹窗可读性；复选框与标题同行，modal 独立高层级展示，数据流程不变。验证见 `acceptance-fixes.md`。 |

| 2026-09-16 17:45:00 | /opsx-modify | 按 `layout-5-split-delete.html` 和用户反馈返修第 2 步：删除 `AI 审阅结果` 标题；来源依据改为候选卡内 label + 具体依据文本；拆分/删除改为卡内展开面板；确认创建直接提交，不再二次确认。验证见 `acceptance-fixes.md`。 |
| 2026-09-16 19:05:00 | /opsx-modify | 拆分/删除面板改为在候选卡操作按钮行之后向下展开；拆分面板改为左右两个完整子条目，每项包含类目、标题和描述，且可分别选择需求或 BUG。验证见 `acceptance-fixes.md`。 |
| 2026-09-16 19:52:00 | /opsx-modify | 第 1 步上传文本文件新增独立 chip 与删除入口；删除文本文件 chip 时同步移除 MD 编辑器中的对应来源文件块，图片删除和服务端数据流程不变。验证见 `acceptance-fixes.md`。 |
| 2026-09-16 19:58:00 | /opsx-modify | 第 2 步候选卡操作区将 `编辑 / 改类型` 改为带编辑图标的 `编辑`；删除按钮添加删除图标；编辑面板移动到操作按钮行之后向下展开，行为不变。验证见 `acceptance-fixes.md`。 |
| 2026-09-16 22:24:00 | /opsx-modify | 第 3 步创建结果按附件收敛：结果态改为左对齐结果内容流，每条采集记录以 REQ/BUG 编号 badge、标题、目录、capture.md / trace.md 和来源摘要展示；幂等保护与产物边界合并为实底说明块；确认幂等、编号分配、来源追溯和服务端数据流程不变。验证见 `acceptance-fixes.md`。 |
| 2026-09-16 23:05:00 | /opsx-modify | 项目内相似 REQ/BUG 提示返修：候选卡展示可能相关项，支持继续创建、合并、补充材料或删除；合并/补充候选不进入确认创建批次，不分配新编号；服务端确认幂等与编号流程不变。验证见 `acceptance-fixes.md`。 |
| 2026-09-16 23:12:00 | /opsx-modify | MD 文本材料块可删除返修：`MD 文本` chip 仅在存在手写/粘贴正文时显示，删除时清空手写正文并保留上传来源文件块和图片材料；来源材料计数动态更新，服务端数据流程不变。验证见 `acceptance-fixes.md`。 |
| 2026-09-16 23:30:00 | /opsx-modify | 默认 Markdown 编辑器不显示来源 chip 返修：第 1 步来源材料区移除 `MD 文本` / `编辑器正文` chip 与计数，来源材料只统计额外上传图片和文本文件；上传文本文件和图片删除逻辑、草稿保存、AI 整理和确认编号流程不变。验证见 `acceptance-fixes.md`。 |
| 2026-09-16 23:38:00 | /opsx-modify | 相似项提示空态隐藏返修：候选卡仅在存在相似匹配时展示 `可能相关` 模块；无匹配时不显示空态，默认创建状态不显示 `继续创建新记录`，已标记已有项后恢复入口改为 `恢复创建`；相似匹配、确认幂等和编号流程不变。验证见 `acceptance-fixes.md`。 |
| 2026-09-16 23:48:00 | /opsx-modify | 创建结果态图标移除返修：成功、失败或中断结果态不再显示圆形勾选图标；confirming 状态保留 loading；创建结果、确认幂等、编号分配、来源追溯和服务端数据流程不变。验证见 `acceptance-fixes.md`。 |
