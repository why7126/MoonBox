---
change_id: update-markdown-editor-vditor-enhancement
status: applied
type: update
created_at: 2026-08-19 12:01:07
updated_at: 2026-08-19 12:22:00
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

当前无 HTML/PNG 原型，已承接文本原型拆解。实现阶段已补齐 1440px 编辑态、图片上传失败态截图和 computed style 证据。

## UI Contract / Skeleton 状态

| 项 | 状态 | 说明 |
|---|---|---|
| UI Contract | done | 见 `design.md` |
| UI Skeleton | done | `src/web/src/pages/catalog/RequirementCenterPage.tsx` |
| 1440px 视觉验收 | done | `evidence/20260819-vditor-editor-visual/01-capture-vditor-editor-1440.png`、`02-image-upload-controlled-failure-1440.png` |
| computed style | done | `evidence/20260819-vditor-editor-visual/computed-vditor-editor-1440.json` |
| Mock/API 边界 | done | 当前项目无认可的需求文档图片上传接口，图片入口以受控失败态呈现，不写入本机路径、私有对象地址或凭据 |
| REQ 最终一致性 | done | MVP 范围保持为“仅 capture.md 增强编辑器” |

## 实现记录

| 类型 | 文件 | 说明 |
|---|---|---|
| 前端 | `src/web/src/pages/catalog/RequirementCenterPage.tsx` | 增加 `VditorEditorShell`，仅在采集池 `capture.md` 可编辑态启用，提供图片、表格、代码块、数学公式工具和安全源码预览。 |
| 样式 | `src/web/src/styles/globals.css` | 增加 Vditor 工具栏、上传状态、双栏编辑/预览和移动端堆叠样式。 |
| 测试 | `src/web/src/requirement-center.test.tsx` | 扩展 capture.md 编辑测试，覆盖工具栏插入、图片上传受控失败、保存、脏关闭和只读保护。 |
| 视觉证据 | `openspec/changes/update-markdown-editor-vditor-enhancement/evidence/20260819-vditor-editor-visual/` | 1440px 截图、computed style JSON 和可复跑 Playwright 脚本。 |

## API / DB / UI / 部署 / 安全同步

- API：未新增接口；图片上传因缺少项目认可的需求文档上传接口而受控禁用，真实上传接口后续需单独进入 OpenSpec。
- DB：无数据库结构变化。
- UI：需求中心 Markdown 抽屉新增编辑器工具栏和双栏源码/预览布局。
- 部署：无端口、环境变量或 Docker 配置变化。
- 安全：Markdown 预览仍使用文本节点和 `<pre>` 展示，不执行 HTML；图片上传不写入本机路径、临时私有地址或对象存储凭据。

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-19 12:01:07 | req.opsx | 创建 OpenSpec Change，承接 REQ-0021 的 Vditor 增强编辑器需求。 |
| 2026-08-19 12:22:00 | opsx.apply | 完成 capture.md 增强编辑器 MVP，实现工具栏插入、受控上传失败状态、视觉证据和前端测试。 |
