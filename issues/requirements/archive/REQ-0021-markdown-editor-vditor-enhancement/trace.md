---
requirement_id: REQ-0021-markdown-editor-vditor-enhancement
status: done
priority: P1
created_at: 2026-08-19 11:30:07
updated_at: 2026-09-04 15:29:37
lifecycle:
  captured: 2026-08-19 11:30:07
  generated: 2026-08-19 11:32:02
  completed: 2026-08-19 11:36:10
  reviewed: 2026-08-19 11:41:07
  approved: 2026-08-19 11:41:07
iteration: sprint-003
openspec_changes:
  - change_id: update-markdown-editor-vditor-enhancement
    type: update
    status: archived
related_requirements:
  - REQ-0020-requirement-center-card-document-actions-ai-chat
lifecycle_stage: archive
knowledge_base_refs:
  - docs/knowledge-base/best-practices/admin-media-upload-chain.md
  - docs/knowledge-base/retrospectives/sprint-002-retrospective.md
cross_cutting_tags:
  - media-upload
prototype_refs:
  - path: issues/requirements/review/REQ-0021-markdown-editor-vditor-enhancement/prototype/web/context.md
    role: ui-decomposition
prototype_gate:
  decomposition: done
  ui_skeleton: done
  visual_acceptance_1440: done
  req_final_consistency: done
related_change: update-markdown-editor-vditor-enhancement
---

# REQ-0021-markdown-editor-vditor-enhancement Trace

## 当前状态

- 状态：done
- 优先级：P1
- 阶段：archive
- 关联 Sprint：sprint-003
- 关联 Change：update-markdown-editor-vditor-enhancement
- 父级/关联需求：REQ-0020-requirement-center-card-document-actions-ai-chat
- Knowledge-base 标签：media-upload
- Prototype Gate：decomposition done；UI Skeleton / 1440px 视觉验收 / 最终一致性已由 Change 实现证据完成

## Knowledge-base Cross-cutting Report

| 标签 | 引用文档 | 写入 acceptance 的 AC 条数 |
|---|---|---:|
| media-upload | `docs/knowledge-base/best-practices/admin-media-upload-chain.md` | 7 |

最近复盘参考：`docs/knowledge-base/retrospectives/sprint-002-retrospective.md` 提醒 Docker/media-upload 验收必须使用动态端口、脚本化测试身份和隔离证据，已转化为 AC-XCUT-005 与 AC-XCUT-006。

## Readiness Report

| 项 | 结果 | 说明 |
|---|---|---|
| Readiness | Ready | requirement、user-stories、business-flow、acceptance、trace 与 prototype context 已补齐 |
| Knowledge-base gate | Pass | media-upload best-practice 已读并转化为横切 AC |
| Cross-cutting tags | media-upload | 上传状态机、即时回显、Docker 端口和测试身份已覆盖 |
| Prototype Gate | Ready | 已完成原型拆解、UI Skeleton、1440px 视觉截图和 computed style 证据 |

## Apply Evidence

| 项 | 证据 |
|---|---|
| 实现 Change | `openspec/archive/2026-09-04-update-markdown-editor-vditor-enhancement` |
| 视觉截图 | `openspec/archive/2026-09-04-update-markdown-editor-vditor-enhancement/evidence/20260819-vditor-editor-visual/01-capture-vditor-editor-1440.png`、`02-image-upload-controlled-failure-1440.png` |
| 样式证据 | `openspec/archive/2026-09-04-update-markdown-editor-vditor-enhancement/evidence/20260819-vditor-editor-visual/computed-vditor-editor-1440.json` |
| API 边界 | 当前无认可需求文档图片上传接口，图片入口受控失败，不写入本机路径、私有对象地址或凭据 |

## Modify Evidence

| 项 | 证据 |
|---|---|
| 验收反馈 | Markdown 右侧抽屉参照附件 HTML 一比一复刻，采用 MoonBox token 适配，提供预览/编辑/分栏，图片上传继续受控失败 |
| 返修截图 | `openspec/archive/2026-09-04-update-markdown-editor-vditor-enhancement/evidence/20260819-vditor-editor-visual/03-drawer-prototype-preview-1440.png`、`04-drawer-prototype-edit-1440.png`、`05-drawer-prototype-split-1440.png`、`06-drawer-prototype-upload-failed-1440.png`、`07-drawer-trace-readonly-density-1440.png` |
| 样式证据 | `openspec/archive/2026-09-04-update-markdown-editor-vditor-enhancement/evidence/20260819-vditor-editor-visual/computed-vditor-editor-1440.json` |
| 子文档一致性 | requirement、acceptance、prototype context 和 trace 已同步；business-flow 与 user-stories 无流程语义变化，无需更新 |
| 二次返修 | 预览态改为阅读态 Markdown 渲染，frontmatter 解析为摘要，toolbar 仅编辑/分栏态展示，分栏态左源码右渲染 |
| 二次验证 | `computed-vditor-editor-1440.json` 中 `preview.toolbarVisible=false`、`renderedPreviewExists=true`、`rawFrontmatterFenceVisible=false` |
| 三次返修 | frontmatter 元数据默认收起并支持展开/收起；编辑/分栏态元数据与正文分离；MVP 中元数据只读；保存仍提交完整 Markdown 字符串 |
| 三次验证 | `computed-vditor-editor-1440.json` 中 `preview.frontmatterSummaryExists=false`、`expandedMetadata.frontmatterSummaryExists=true`、`editorValueIncludesFrontmatterFence=false`、`metadataSummarySeparatedFromEditor=true` |
| 四次返修 | 顶部 spec 只显示独立“展开/收起”；正文 frontmatter 标题改为“文档属性”；移除 `Capture Brief`；图片上传 idle 状态不默认展示 |
| 四次验证 | `computed-vditor-editor-1440.json` 中 `preview.captureBriefVisible=false`、`beforeUpload.uploadStateExists=false`、`collapsedSpec.specGridExists=false`、`expandedMetadata.specGridExists=false` |
| 五次返修 | 顶部 spec 默认收起；预览态移除“文档内容”标题；右侧抽屉 header 增加放大全屏/恢复；拖拽宽度仅非全屏生效 |
| 五次验证 | `computed-vditor-editor-1440.json` 中 `preview.specGridExists=false`、`preview.documentContentLabelVisible=false`、`fullscreen.drawerFullscreen=true`、`fullscreen.resizerExists=false`、`restoredDrawer.drawerWidthStyle="width: 760px;"` |
| 六次返修 | 预览、编辑和分栏模式正文区移除额外区块标题；分栏态不再展示 `Markdown Source` / `Live Preview`，左右内容顶端对齐 |
| 六次验证 | `computed-vditor-editor-1440.json` 中 `splitLabels.markdownSourceLabelVisible=false`、`splitLabels.livePreviewLabelVisible=false`、`splitLabels.paneTopDelta=0` |
| 七次返修 | 编辑/分栏态表格、代码、公式工具改为按光标或选区插入；插入后聚焦编辑区并更新光标；分栏态右侧预览即时刷新；图片保持受控失败 |
| 七次验证 | `computed-vditor-editor-1440.json` 中 `toolbarInsertion.tableInsertedAtCursor=true`、`codeWrappedSelection=true`、`formulaInserted=true`、`livePreviewUpdated=true` |
| 八次返修 | 保存失败时前端保留编辑/分栏态和 draft；本地开发 Compose 允许采集池 `capture.md` 受控写入，后端写入异常返回安全业务错误 |
| 九次返修 | 预览态 task list 渲染为真实复选框，勾选后标记未保存，保存失败保留勾选草稿 |
| 十次返修 | 预览态 Markdown 正文、标题、表格和 task list 收敛为右侧抽屉工作型阅读密度；分栏右侧预览使用紧凑阅读样式 |
| 十次验证 | `computed-vditor-editor-1440.json` 中 `preview.renderedPreviewFontSize="13px"`、`preview.renderedHeadingFontSize="20px"`、`splitLabels.renderedPreviewFontSize="12.5px"`；前端聚焦测试 104 passed |
| 十一次返修 | Markdown 阅读区正文使用产品 body 字体，标题使用产品 heading 字体，不再混用衬线字体；代码块、行内代码和源码编辑区保留 mono |
| 十一次验证 | `computed-vditor-editor-1440.json` 中 `preview.renderedPreviewFontFamily="Inter, \"Noto Sans SC\", system-ui, sans-serif"`、`preview.renderedHeadingFontFamily="Inter, \"Noto Sans SC\", system-ui, sans-serif"`、`splitLabels.renderedCodeFontFamily="\"JetBrains Mono\", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"`；前端聚焦测试 104 passed |
| 十二次返修 | 未保存确认仅限可编辑 `capture.md` 用户真实改动后触发；`trace.md` 等只读文档、未编辑 `capture.md` 和保存成功后关闭不提示；保存失败保留草稿且关闭继续提示 |
| 十二次验证 | 前端聚焦测试 105 passed，覆盖只读 `trace.md` 关闭不提示、未编辑 `capture.md` 关闭不提示、编辑后关闭提示、保存成功后关闭不提示、保存失败后关闭继续提示 |
| 十三次返修 | 抽屉顶部信息层级收敛为 Header + 文档属性 Strip：移除第二个 spec 信息条；Header 保留对象 ID、当前文档名、标题和“优先级 · 负责人负责 · 阶段”副标题；文档属性 Strip 左侧仅显示“文档属性”，右侧控制展开/收起，展开后展示 frontmatter 详情 |
| 十三次验证 | 前端聚焦测试 105 passed、Web build、OpenSpec strict、Playwright computed 视觉证据和 diff check 通过；覆盖第二个 spec 信息条不存在、Header 副标题格式和文档属性独立展开详情 |
| 十四次返修 | 所有 Markdown 抽屉阅读态统一为工作型阅读密度；`trace.md` 等只读文档正文、标题、列表、表格和代码块不再明显大于 `capture.md` 预览态；表格单元格单独收敛字号、行高和 padding |
| 十四次验证 | 前端聚焦测试 105 passed、Web build、OpenSpec strict、Playwright computed 视觉证据和 diff check 通过；CSS 契约覆盖阅读态 base、compact、标题、列表和表格单元格密度；`traceReadonly` 证据显示只读表格单元格为 `12px`、`6px 8px` padding |
| 十五次返修 | 所有 Markdown 抽屉阅读态代码块右上角提供复制按钮；复制代码块原文且不包含 Markdown 围栏；成功或失败通过按钮内轻量文案反馈，不影响 `capture.md` 源码编辑区、保存、上传或权限边界 |
| 十五次验证 | 前端聚焦测试 106 passed，覆盖阅读态代码块复制内容为 `pnpm test\npnpm build` 且不含围栏；Playwright computed 证据记录复制按钮存在、复制按钮文案和剪贴板写入原文 |
| 十六次返修 | 复制按钮默认收敛为低视觉权重图标，hover/focus 时显示“复制”提示，点击后短暂显示“已复制/复制失败”；短代码块不再为复制按钮产生过大顶部留白，长代码横向滚动保持可用 |
| 十六次验证 | 前端聚焦测试 106 passed；CSS 契约覆盖默认 26px 图标宽度、低透明度、hover/focus 展开和结果态；Playwright computed 证据记录按钮默认宽度、label 隐藏、复制后文案和紧凑 padding |

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-09-04 15:29:23 | /opsx-archive | Change `update-markdown-editor-vditor-enhancement` 已归档，状态同步完成。 |
| 2026-08-27 08:43:16 | /opsx-modify | Change `update-markdown-editor-vditor-enhancement` 验收返修已同步，待复验或 archive。 |
| 2026-08-27 08:53:11 | /opsx-modify | 按用户截图反馈将 `capture.md` 预览态改为阅读态 Markdown 渲染，预览态隐藏 toolbar，分栏态左源码右渲染，图片上传受控失败策略不变。 |
| 2026-08-27 09:05:08 | /opsx-modify | 按用户反馈将 frontmatter 元数据默认收起并与正文编辑区分离，MVP 只读展示，保存仍提交完整 Markdown。 |
| 2026-08-27 09:27:51 | /opsx-modify | 按最新截图反馈收口抽屉文案与状态噪音：顶部独立展开/收起，正文改“文档属性”，移除 `Capture Brief`，上传状态仅触发后展示。 |
| 2026-08-27 09:43:44 | /opsx-modify | 按最新验收反馈将顶部 spec 默认收起，移除预览态“文档内容”标题，并新增右侧抽屉放大全屏/恢复能力。 |
| 2026-08-27 10:32:19 | /opsx-modify | 按最新截图反馈移除预览、编辑、分栏正文区额外区块标题，分栏态左右内容顶端对齐。 |
| 2026-08-28 09:15:42 | /opsx-modify | 按最新验收反馈增强编辑/分栏态工具栏可用性：表格、代码和公式按光标或选区插入，分栏预览即时刷新，图片保持受控失败。 |
| 2026-09-01 00:00:00 | /opsx-modify | 按最新截图反馈收敛 `capture.md` Markdown 阅读态字体密度，预览态和分栏右侧预览更适合右侧抽屉阅读。 |
| 2026-09-01 08:30:00 | /opsx-modify | 按最新反馈统一 `capture.md` Markdown 阅读区字体族：正文使用产品 body，标题使用产品 heading，代码和源码保留 mono。 |
| 2026-09-01 10:23:00 | /opsx-modify | 按最新截图反馈修正 `capture.md` 抽屉关闭确认边界：仅用户真实改动可编辑 `capture.md` 后提示，`trace.md` 和未编辑内容关闭不提示。 |
| 2026-09-01 10:48:00 | /opsx-modify | 按最新确认收敛 Markdown 抽屉顶部信息层级：移除第二个 spec 信息条，Header 展示摘要，文档属性 Strip 承载 frontmatter 详情。 |
| 2026-09-01 11:12:00 | /opsx-modify | 按最新截图反馈统一所有 Markdown 抽屉阅读态密度，重点收敛 `trace.md` 只读表格字号、行高和单元格 padding。 |
| 2026-09-01 12:05:00 | /opsx-modify | 按最新反馈为所有 Markdown 抽屉阅读态代码块增加复制按钮，复制代码原文且不含 Markdown 围栏，成功/失败轻量提示。 |
| 2026-09-01 12:55:00 | /opsx-modify | 按最新截图反馈收敛代码块复制按钮视觉权重：默认图标化，hover/focus 展开提示，点击后显示复制结果，短代码块减少顶部留白。 |
| 2026-08-19 12:23:54 | /opsx-apply | Change `update-markdown-editor-vditor-enhancement` apply 完成，随后进入归档闭环。 |
| 2026-08-19 11:30:07 | req.capture | 记录需求：为需求中心 `capture.md` 引入 Vditor 增强编辑体验，MVP 限定为采集阶段可编辑文档。 |
| 2026-08-19 11:32:02 | req.generate | 生成 `requirement.md`，需求进入 draft 状态。 |
| 2026-08-19 11:36:10 | req.complete | 补齐 user-stories、business-flow、acceptance 与 prototype context，嵌入 media-upload 横切 AC，需求进入 pending_review。 |
| 2026-08-19 11:41:07 | req.review | 评审通过，需求进入 approved，下一步纳入 Sprint。 |
| 2026-08-19 12:01:07 | req.opsx | 创建 OpenSpec Change `update-markdown-editor-vditor-enhancement`，进入实现准备阶段。 |
| 2026-08-19 12:22:00 | opsx.apply | Change 已实现并验证，等待人工验收或归档。 |
| 2026-08-27 08:40:00 | opsx.modify | 按附件 HTML 验收反馈完成 Markdown 右侧抽屉视觉返修，等待人工验收或归档。 |

- 阶段迁移：plan → review（/req-review --approve）
- 2026-09-04 15:29:23 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive update-markdown-editor-vditor-enhancement
