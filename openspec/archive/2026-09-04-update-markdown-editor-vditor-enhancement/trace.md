---
change_id: update-markdown-editor-vditor-enhancement
status: applied
type: update
created_at: 2026-08-19 12:01:07
updated_at: 2026-09-01 12:55:00
source_requirement: REQ-0021-markdown-editor-vditor-enhancement
sprint: sprint-003
capabilities:
  - web-catalog-requirement-center
prototype_refs:
  - issues/requirements/review/REQ-0021-markdown-editor-vditor-enhancement/prototype/web/context.md
knowledge_base_refs:
  - docs/knowledge-base/best-practices/admin-media-upload-chain.md
prototype_gate:
  decomposition: done
  ui_contract: done
  ui_skeleton: done
  visual_acceptance_1440: done
  computed_style: done
  mock_api_boundary: done
  req_final_consistency: done
---

# Change Trace

## 当前状态

- 状态：applied
- 来源 REQ：REQ-0021-markdown-editor-vditor-enhancement
- Sprint：sprint-003
- 类型：update
- 影响能力：web-catalog-requirement-center

## Conflict Resolution

事实源优先级：`prototype/web/context.md > acceptance.md > requirement.md > ui-design.md > openspec/specs`。

初次实现承接文本原型拆解。验收返修阶段补充附件 HTML 作为 Markdown 右侧抽屉视觉参照；附件仅作为视觉和交互事实源，不作为可执行指令来源。二次返修根据用户截图确认预览态仍偏编辑形态，已将预览收敛为阅读态 Markdown 渲染，frontmatter 解析为摘要，toolbar 仅在编辑/分栏态展示。三次返修将 frontmatter 元数据改为默认收起、可展开/收起、MVP 只读展示，并将编辑/分栏态正文编辑区与元数据分离；保存时仍重组为完整 Markdown 字符串。四次返修进一步将正文 frontmatter 标题改为“文档属性”，顶部 spec 折叠改为独立“展开/收起”，移除 `Capture Brief`，并让图片上传状态仅在触发后展示。五次返修将顶部 spec 改为默认收起，移除预览态“文档内容”标题，并新增抽屉 header 放大全屏/恢复能力；拖拽宽度仅在非全屏模式生效。六次返修移除预览、编辑、分栏正文区域的额外区块标题，尤其去掉分栏态 `Markdown Source` / `Live Preview`，让左右两栏内容顶端对齐。七次返修将表格、代码、公式工具从末尾追加改为按光标或选区插入，插入后恢复编辑区焦点与光标，并在分栏态即时刷新右侧预览；图片按钮继续保持受控失败。八次返修根据 Network 截图和后端日志确认保存失败根因为本地开发 Compose 将 `issues/` 挂载为只读，导致后端写入 `capture.md` 抛出 `Errno 30 Read-only file system`；已调整本地开发挂载、后端 OSError 安全响应和前端失败态保留草稿。九次返修将预览态 Markdown task list 渲染为可交互复选框，勾选或取消后只更新本地草稿并标记未保存，仍需点击保存写回 Markdown，保存失败保留勾选草稿。十次返修根据用户截图反馈将预览态 Markdown 正文、标题、表格和 task list 字号整体收敛为右侧抽屉工作型阅读密度，并让分栏右侧预览使用紧凑阅读样式；源码编辑区保持可读密度。十一次返修将 Markdown 阅读区字体族收敛到产品字体体系：正文使用 body、标题使用 heading，不再混用额外衬线字体；代码块、行内代码和源码编辑区保留 mono。十二次返修将未保存确认改为显式 dirty 状态驱动，仅采集池可编辑 `capture.md` 且用户真实改动后触发；只读 `trace.md`、未编辑 `capture.md` 和保存成功后关闭不再误提示，保存失败仍保留草稿并提示。十三次返修将抽屉顶部信息层级收敛为 Header + 文档属性 Strip：移除第二个 spec 信息条，Header 副标题改为“优先级 · 负责人负责 · 阶段”，文档属性 Strip 左侧仅显示“文档属性”、右侧控制展开/收起并承载 frontmatter 详情。十四次返修将所有 Markdown 抽屉阅读态统一到同一套工作型阅读密度，重点收敛 `trace.md` 等只读文档的表格字号、行高和单元格 padding。十五次返修为所有 Markdown 抽屉阅读态代码块增加右上角复制按钮，复制代码原文且不含 Markdown 围栏，并用按钮内文案反馈成功或失败；不影响 `capture.md` 源码编辑区、保存、上传或权限边界。十六次返修将复制按钮默认收敛为低视觉权重图标，hover/focus 或复制结果态再展开文案，并收回短代码块顶部留白；不改变复制内容、保存、上传、权限或数据接口。返修后已补齐预览态、编辑态、分栏态、图片上传失败态、`trace.md` 只读态和代码块复制 computed style 证据。

## UI Contract / Skeleton 状态

| 项 | 状态 | 说明 |
|---|---|---|
| UI Contract | done | 见 `design.md` |
| UI Skeleton | done | `src/web/src/pages/catalog/RequirementCenterPage.tsx` |
| 1440px 视觉验收 | done | `evidence/20260819-vditor-editor-visual/03-drawer-prototype-preview-1440.png`、`04-drawer-prototype-edit-1440.png`、`05-drawer-prototype-split-1440.png`、`06-drawer-prototype-upload-failed-1440.png` |
| computed style | done | `evidence/20260819-vditor-editor-visual/computed-vditor-editor-1440.json` |
| Mock/API 边界 | done | 当前项目无认可的需求文档图片上传接口，图片入口以受控失败态呈现，不写入本机路径、私有对象地址或凭据 |
| REQ 最终一致性 | done | MVP 范围保持为“仅 capture.md 增强编辑器” |

## 实现记录

| 类型 | 文件 | 说明 |
|---|---|---|
| 前端 | `src/web/src/pages/catalog/RequirementCenterPage.tsx` | 增加 `VditorEditorShell`，仅在采集池 `capture.md` 可编辑态启用，提供图片、表格、代码块、数学公式工具；预览态使用阅读态 Markdown 渲染并解析 frontmatter，task list 渲染为可交互复选框；阅读态代码块提供复制按钮并复制无围栏代码原文；分栏态左正文源码右渲染；移除第二个 spec 信息条；Header 展示对象 ID、当前文档名、标题和“优先级 · 负责人负责 · 阶段”副标题；文档属性默认收起并只读展示，保存时重组完整 Markdown；预览态移除“文档内容”标题；正文区不展示额外区块标题；表格/代码/公式按光标或选区插入并恢复焦点；上传状态按需展示；header 支持放大全屏/恢复；保存失败时保留当前编辑/分栏/预览勾选态和 draft，并以提示反馈失败原因；未保存确认仅在可编辑 `capture.md` 用户真实改动后触发。 |
| 后端 | `src/backend/app/api/v1/requirement_center.py` | 捕获 `capture.md` 写入 `OSError`，返回安全业务错误，避免裸 500 与内部路径泄漏。 |
| 部署 | `docker-compose.yml` | 根目录本地开发 Compose 将 `issues/` 挂载调整为可写，以支持后端对采集池 `capture.md` 的受控保存；其他治理目录保持只读。 |
| 样式 | `src/web/src/styles/globals.css` | 增加 Vditor 工具栏、上传状态、阅读态 Markdown、task list 复选框、代码块复制按钮、frontmatter 折叠面板、双栏编辑/预览、移动端堆叠和抽屉全屏样式；移除正文区块标题样式；收敛阅读态 Markdown 字体密度和字体族。 |
| 测试 | `src/web/src/requirement-center.test.tsx`、`tests/integration/api/test_requirement_center.py` | 扩展 capture.md 编辑与保存测试，覆盖工具栏插入、task list 预览态勾选和保存、阅读态字体密度与字体族、代码块无围栏复制、图片上传受控失败、保存、失败保留草稿、脏关闭、只读保护、只读文档不误触发关闭确认和只读文件系统写入异常。 |
| 视觉证据 | `openspec/changes/update-markdown-editor-vditor-enhancement/evidence/20260819-vditor-editor-visual/` | 1440px 截图、computed style JSON 和可复跑 Playwright 脚本。 |

## 验收返修记录

| 时间 | 反馈 | 调整 | 验证 |
|---|---|---|---|
| 2026-08-27 08:40:00 | Markdown 右侧抽屉参照附件 HTML 一比一复刻，采用 MoonBox token 适配，补齐预览/编辑/分栏，图片上传继续受控失败 | 默认抽屉宽度调整为 760px；新增附件式 header、spec 信息条、模式栏、独立 toolbar、正文安全预览/源码编辑/分栏和固定 footer；保持 `capture.md` 权限边界 | `vitest` 40 passed；`tsc -b` 通过；`vite build` 通过；Playwright 产出 4 张 1440px 截图和 computed style |
| 2026-08-27 08:53:11 | `capture.md` 预览态仍像编辑形态，需要阅读态 Markdown 渲染，预览态隐藏 toolbar，frontmatter 隐藏或解析，分栏态左源码右渲染 | 新增 frontmatter 解析与 `RenderedMarkdown` 阅读态组件；预览态隐藏 toolbar；分栏右侧复用渲染预览；图片上传受控失败策略不变 | `vitest` 40 passed；`tsc -b` 通过；`vite build` 通过；Playwright computed 显示 `preview.toolbarVisible=false`、`renderedPreviewExists=true`、`rawFrontmatterFenceVisible=false` |
| 2026-08-27 09:05:08 | 元数据默认收起并支持展开/收起；编辑/分栏态将 frontmatter 元数据与正文区分开；MVP 只读展示；保存仍提交完整 Markdown | 新增元数据折叠面板；编辑器 draft 改为 Markdown body；保存前将 frontmatter 与 body 重组；分栏右侧仍渲染正文预览；图片上传受控失败策略不变 | `vitest` 40 passed；`tsc -b` 通过；`vite build` 通过；Playwright computed 显示 `preview.frontmatterSummaryExists=false`、`expandedMetadata.frontmatterSummaryExists=true`、`editorValueIncludesFrontmatterFence=false`、`metadataSummarySeparatedFromEditor=true` |
| 2026-08-27 09:27:51 | 顶部 spec 改为独立“展开/收起”；正文 frontmatter 标题改“文档属性”；移除 `Capture Brief`；图片上传 idle 状态不默认展示 | 新增独立 spec 折叠状态；正文属性文案改为“文档属性”；移除预览 callout；上传状态仅在非 idle 或错误时渲染 | `vitest` 40 passed；`tsc -b` 通过；`vite build` 通过；Playwright computed 显示 `captureBriefVisible=false`、`beforeUpload.uploadStateExists=false`、`collapsedSpec.specGridExists=false`、`expandedMetadata.specGridExists=false` |
| 2026-08-27 09:43:44 | 顶部 spec 默认收起；预览态移除“文档内容”标题；右侧抽屉 header 增加放大全屏/恢复，拖拽宽度仅非全屏生效 | 打开 `capture.md` 时 spec 详情默认收起；移除预览正文标题；新增全屏状态和 header 切换按钮；全屏态隐藏 resizer，恢复后回到右侧抽屉宽度 | `vitest` 40 passed；`tsc -b` 通过；`vite build` 通过；Playwright computed 显示 `preview.specGridExists=false`、`preview.documentContentLabelVisible=false`、`fullscreen.drawerFullscreen=true`、`fullscreen.resizerExists=false`、`restoredDrawer.drawerWidthStyle="width: 760px;"` |
| 2026-08-27 10:32:19 | 分栏态 `Markdown Source` / `Live Preview` 标题高度不一致，用户确认三个 Tab 正文区全部移除额外区块标题 | 删除编辑器 pane label；预览、编辑、分栏正文区直接进入阅读或编辑内容；分栏左右 pane 顶端对齐 | `vitest` 40 passed；`tsc -b` 通过；`vite build` 通过；Playwright computed 显示 `splitLabels.markdownSourceLabelVisible=false`、`splitLabels.livePreviewLabelVisible=false`、`splitLabels.paneTopDelta=0` |
| 2026-08-28 09:15:42 | 编辑/分栏态图片上传、表格、代码、公式功能不可用或反馈不明显 | 图片按钮保持受控失败；表格/代码/公式按光标或选区插入，插入后聚焦编辑区并更新光标；分栏态右侧预览即时刷新 | `vitest` 40 passed；`tsc -b` 通过；`vite build` 通过；Playwright computed 显示 `toolbarInsertion.tableInsertedAtCursor=true`、`codeWrappedSelection=true`、`formulaInserted=true`、`livePreviewUpdated=true` |
| 2026-08-28 09:40:00 | 插入表格/代码/公式后保存显示“文档保存失败”，失败后不应进入空面板 | 本地开发 Compose 允许 `issues/` 受控写入；后端将治理目录写入异常转为 503 安全错误；前端保存失败保留当前编辑/分栏态与 draft，并用 toast/局部错误提示反馈 | `pytest` 12 passed；`vitest` 96 passed；`tsc -b` 通过；`vite build` 通过；OpenSpec strict 通过；`git diff --check` 通过 |
| 2026-08-28 18:30:00 | 预览态 Markdown task list 需要展示成可快速勾选/取消的复选框 | 预览态将 `- [ ]` / `- [x]` 渲染为真实 checkbox；勾选/取消后更新本地 draft 并标记未保存；保存仍通过 footer 按钮写回 Markdown；保存失败保留勾选草稿 | `vitest` 97 passed；`tsc -b` 通过；`vite build` 通过；OpenSpec strict 通过；`git diff --check` 通过 |
| 2026-09-01 00:00:00 | Markdown 文档内容字体感觉偏大，需要更适合右侧抽屉阅读 | 预览态正文从 14px/1.85 收敛到 13px/1.72，一级/二级/三级标题收敛为 20px/16px/14px，表格、列表、task list 和代码块间距同步收紧；分栏右侧预览使用 compact 12.5px/1.68 | `vitest` 104 passed；`tsc -b` 通过；`vite build` 通过；OpenSpec strict 通过；Playwright computed 显示 `preview.renderedPreviewFontSize="13px"`、`splitLabels.renderedPreviewFontSize="12.5px"`；`git diff --check` 通过 |
| 2026-09-01 08:30:00 | 右侧抽屉各部分字体族不一致，Markdown 正文阅读区不应混用衬线字体 | Markdown 阅读区正文显式使用 `var(--rc-font-body)`，标题改用 `var(--rc-font-heading)`，代码块、行内代码和源码编辑区保留 `var(--rc-font-mono)`；顶部 ID、文件名和短标签可继续使用 mono | `vitest` 104 passed；`tsc -b` 通过；`vite build` 通过；OpenSpec strict 通过；Playwright computed 显示 `preview.renderedPreviewFontFamily="Inter, \"Noto Sans SC\", system-ui, sans-serif"`、`preview.renderedHeadingFontFamily="Inter, \"Noto Sans SC\", system-ui, sans-serif"`、`splitLabels.renderedCodeFontFamily="\"JetBrains Mono\", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"`；`git diff --check` 通过 |
| 2026-09-01 10:23:00 | 打开 `trace.md` 或未编辑 `capture.md` 关闭时误出现 `capture.md` 未保存确认 | 新增显式 `dirty` 状态；dirty 仅在可编辑 `capture.md` 的正文编辑、task list 勾选或工具栏插入后置位；初始化、读取、模式切换、只读文档、保存成功和取消草稿保持 clean；保存失败保留 dirty | `vitest` 105 passed，覆盖只读 `trace.md` 关闭不提示、未编辑 `capture.md` 关闭不提示、编辑后关闭提示、保存成功后关闭不提示、保存失败后关闭继续提示 |
| 2026-09-01 10:48:00 | 顶部 Header、spec 信息条和文档属性三层信息重复，用户确认移除第二个 spec 信息条 | 删除第二个 spec 信息条；Header 副标题改为“优先级 · 负责人负责 · 阶段”；文档属性 Strip 左侧仅显示“文档属性”，右侧保留展开/收起，展开后展示 frontmatter 详情 | `vitest` 105 passed、Web build、OpenSpec strict、Playwright computed 视觉证据和 diff check 通过，覆盖 spec strip 不存在、Header 副标题为 `P1 · 产品团队负责 · 采集池`、文档属性展开后展示 frontmatter |
| 2026-09-01 11:12:00 | 不同 Markdown 文档右侧抽屉阅读密度不一致，`trace.md` 表格和标题仍偏大 | 所有 Markdown 抽屉阅读态共用 `rc-rendered-markdown` 工作型密度；正文、标题、列表、代码块收紧，表格单元格收敛为 `12px/1.48` 和 `6px 8px` padding；`capture.md` 源码编辑区保持现状 | `vitest` 105 passed、Web build、OpenSpec strict、Playwright computed 视觉证据和 diff check 通过；`traceReadonly` 证据显示只读表格单元格为 `12px`、`6px 8px` padding |
| 2026-09-01 12:05:00 | Markdown 抽屉预览/只读态代码块需要复制能力 | `RenderedMarkdown` 为代码块增加右上角复制按钮；点击调用 Clipboard API 复制代码块原文，不含 Markdown 围栏；复制成功或失败以按钮内轻量文案反馈，代码块顶部 padding 预留按钮空间 | `vitest` 106 passed；测试覆盖复制内容不含围栏、只读态不展示编辑模式控件；Playwright computed 记录 `preview.codeCopyButtonExists=true` 和 `codeCopy.copiedCode="pnpm test\npnpm build"` |
| 2026-09-01 12:55:00 | 短代码块上的复制按钮视觉权重偏高，顶部留白过大 | 复制按钮默认收敛为 26px 低透明图标；hover/focus 或 copied/failed 状态展开文案；代码块 padding 从 `30px 10px 9px` 收敛为 `10px 44px 9px 10px` | `vitest` 106 passed；CSS 契约覆盖默认图标宽度、低透明度、hover/focus 展开和结果态；Playwright computed 显示 `codeCopyButtonWidth="26px"`、`codeCopyLabelWidth="0px"`、`renderedCodePadding="10px 44px 9px 10px"` |

## 附件视觉对照摘要

| 对照项 | 期望 | 返修结论 | 证据 |
|---|---|---|---|
| Header / spec 信息条 | 对齐附件的面包屑、标题、副标题、状态/优先级/来源信息条 | 已实现 | `03-drawer-prototype-preview-1440.png` |
| 模式栏 / toolbar | 预览、编辑、分栏三段切换；图片/表格/代码/公式工具栏独立展示 | 已实现 | `04-drawer-prototype-edit-1440.png` |
| 分栏正文 | 源码编辑与安全预览双栏，不横向溢出 | 已实现 | `05-drawer-prototype-split-1440.png`、`computed-vditor-editor-1440.json` |
| 上传失败 / footer | 无真实接口时受控失败，固定 footer 不遮挡正文 | 已实现 | `06-drawer-prototype-upload-failed-1440.png` |
| 预览阅读态 | 预览态渲染 Markdown 正文，frontmatter 不以源码展示，toolbar 不展示 | 已实现 | `03-drawer-prototype-preview-1440.png`、`computed-vditor-editor-1440.json` |
| 分栏右侧渲染 | 分栏态左源码、右阅读态 Markdown 渲染预览 | 已实现 | `05-drawer-prototype-split-1440.png` |
| 元数据折叠 / 正文分离 | 元数据默认收起，可展开/收起，只读展示；编辑器只编辑正文 body，保存仍保留完整 Markdown | 已实现 | `computed-vditor-editor-1440.json` |
| 文案与状态噪音收口 | 顶部仅“展开/收起”；正文为“文档属性”；无 `Capture Brief`；上传 idle 不展示 | 已实现 | `03-drawer-prototype-preview-1440.png`、`06-drawer-prototype-upload-failed-1440.png`、`computed-vditor-editor-1440.json` |
| spec 默认收起 / 去标题 / 全屏 | 顶部 spec 默认收起；预览态无“文档内容”；header 可放大全屏/恢复；全屏隐藏拖拽 | 已实现 | `03-drawer-prototype-preview-1440.png`、`computed-vditor-editor-1440.json` |
| 正文区块标题移除 | 预览、编辑、分栏正文区无额外标题；分栏左右内容顶端对齐 | 已实现 | `05-drawer-prototype-split-1440.png`、`computed-vditor-editor-1440.json` |
| 代码块复制 | 阅读态代码块右上角可复制代码原文，默认低权重图标，hover/focus 或结果态展示文案，不遮挡内容 | 已实现 | `03-drawer-prototype-preview-1440.png`、`computed-vditor-editor-1440.json` |
| 工具栏可用性 | 表格/代码/公式按光标或选区插入，插入后恢复焦点；分栏预览即时刷新；图片保持受控失败 | 已实现 | `05-drawer-prototype-split-1440.png`、`06-drawer-prototype-upload-failed-1440.png`、`computed-vditor-editor-1440.json` |
| task list 交互 | 预览态 task list 可快速勾选/取消，仍需保存按钮写回 Markdown | 已实现 | `src/web/src/requirement-center.test.tsx` |
| 阅读态字体密度 | 所有 Markdown 抽屉阅读态正文、标题、列表、表格、代码块使用右侧抽屉工作型阅读密度；分栏右侧预览更紧凑；只读 `trace.md` 表格单元格单独收敛 | 已实现 | `07-drawer-trace-readonly-density-1440.png`、`computed-vditor-editor-1440.json`、`src/web/src/requirement-center.test.tsx` |
| 阅读态字体族 | 正文阅读区统一产品 body/heading 字体；代码和源码保留 mono；不再混用衬线标题字体 | 已实现 | `computed-vditor-editor-1440.json`、`src/web/src/requirement-center.test.tsx` |
| 关闭确认边界 | 未保存确认仅限可编辑 `capture.md` 用户真实改动后触发；只读文档、未编辑内容和保存成功后关闭不提示 | 已实现 | `src/web/src/requirement-center.test.tsx` |
| 顶部信息层级 | Header + 文档属性 Strip 两层结构；第二个 spec 信息条移除；文档属性展开承载详情 | 已实现 | `src/web/src/requirement-center.test.tsx`、`computed-vditor-editor-1440.json` |

## API / DB / UI / 部署 / 安全同步

- API：未新增接口；图片上传因缺少项目认可的需求文档上传接口而受控禁用，真实上传接口后续需单独进入 OpenSpec。
- DB：无数据库结构变化。
- UI：需求中心 Markdown 抽屉新增编辑器工具栏、阅读态 Markdown 预览、预览态 task list 复选框、frontmatter 文档属性折叠面板、双栏源码/渲染布局和 header 全屏/恢复控制；顶部信息层级收敛为 Header + 文档属性 Strip，第二个 spec 信息条不再展示；正文区不展示额外区块标题；所有 Markdown 抽屉阅读态字体密度收敛为右侧抽屉工作型阅读尺度，`trace.md` 等只读文档表格单元格单独收敛字号、行高和 padding，阅读区字体族统一为产品 body/heading，代码和源码保留 mono；工具栏仅在编辑/分栏态展示，表格/代码/公式按光标或选区插入并恢复焦点，上传状态按需展示，拖拽宽度仅非全屏模式生效；关闭确认仅对用户真实改动后的可编辑 `capture.md` 生效。
- 部署：根目录本地开发 Compose 的 `issues/` 挂载由只读调整为可写，以支持受控保存采集池 `capture.md`；端口、环境变量、生产部署和对象存储配置不变。
- 安全：Markdown 预览使用受控 React 节点渲染，不执行 HTML；图片上传不写入本机路径、临时私有地址或对象存储凭据。

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-19 12:01:07 | req.opsx | 创建 OpenSpec Change，承接 REQ-0021 的 Vditor 增强编辑器需求。 |
| 2026-08-19 12:22:00 | opsx.apply | 完成 capture.md 增强编辑器 MVP，实现工具栏插入、受控上传失败状态、视觉证据和前端测试。 |
| 2026-08-27 08:40:00 | opsx.modify | 按附件 HTML 验收反馈复刻 Markdown 右侧抽屉结构，补齐预览/编辑/分栏与新视觉证据。 |
| 2026-08-27 08:53:11 | opsx.modify | 按用户截图反馈将 `capture.md` 预览态改为阅读态 Markdown 渲染，预览态隐藏 toolbar，分栏态左源码右渲染。 |
| 2026-08-27 09:05:08 | opsx.modify | 按用户反馈将 frontmatter 元数据默认收起并与正文编辑区分离，MVP 只读展示，保存仍提交完整 Markdown。 |
| 2026-08-27 09:27:51 | opsx.modify | 按最新截图反馈收口抽屉文案与状态噪音：顶部独立展开/收起，正文改“文档属性”，移除 `Capture Brief`，上传状态仅触发后展示。 |
| 2026-08-27 09:43:44 | opsx.modify | 按最新验收反馈将顶部 spec 默认收起，移除预览态“文档内容”标题，并新增右侧抽屉放大全屏/恢复能力。 |
| 2026-08-27 10:32:19 | opsx.modify | 按最新截图反馈移除预览、编辑、分栏正文区额外区块标题，分栏态左右内容顶端对齐。 |
| 2026-08-28 09:15:42 | opsx.modify | 按最新验收反馈增强编辑/分栏态工具栏可用性：表格、代码和公式按光标或选区插入，分栏预览即时刷新，图片保持受控失败。 |
| 2026-08-28 09:40:00 | opsx.modify | 按保存失败证据完成本地开发 Compose 写入挂载、后端写入异常安全响应和前端失败态保留草稿返修。 |
| 2026-08-28 18:30:00 | opsx.modify | 按最新验收反馈将预览态 task list 渲染为可交互复选框，勾选后标记未保存并通过保存按钮写回 Markdown。 |
| 2026-09-01 00:00:00 | opsx.modify | 按最新截图反馈收敛 `capture.md` 阅读态字体密度，预览态和分栏右侧预览更适合右侧抽屉阅读。 |
| 2026-09-01 08:30:00 | opsx.modify | 按最新反馈统一 `capture.md` 抽屉 Markdown 阅读区字体族，标题改用产品 heading，正文使用 body，代码和源码保留 mono。 |
| 2026-09-01 10:23:00 | opsx.modify | 按最新截图反馈修正 `capture.md` 抽屉关闭确认边界：仅用户真实改动可编辑 `capture.md` 后提示，`trace.md` 和未编辑内容关闭不提示。 |
| 2026-09-01 10:48:00 | opsx.modify | 按最新确认移除 Markdown 抽屉第二个 spec 信息条，Header 展示优先级/负责人/阶段，文档属性 Strip 承载展开详情。 |
| 2026-09-01 11:12:00 | opsx.modify | 按最新截图反馈统一所有 Markdown 抽屉阅读态密度，重点收敛 `trace.md` 只读表格字号、行高和单元格 padding。 |
