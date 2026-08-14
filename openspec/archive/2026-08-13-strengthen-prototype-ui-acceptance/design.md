# Design: 强化原型驱动 UI 验收规范

## Approach

将 Prototype-driven UI Gate 从流程性要求升级为“UI Contract + Skeleton 首轮确认 + 视觉证据 + computed style + Mock/API 边界 + 一致性 checklist”的组合门禁。

## Governance Contract

### UI Contract

带 `prototype/` 的 UI Change 必须在 Change `design.md` 中写入 UI Contract。Contract 至少声明：

- 事实源优先级和冲突处理。
- 页面入口、路由、权限显示和默认落点。
- 信息架构、组件层级、关键状态和交互触发。
- 字体、字号、行高、颜色、边框、间距、层级、滚动和 responsive 关注点。
- 图标与文案一致性规则。
- Mock/API 数据边界和生产风险。
- 前后台或既有页面一致性 checklist。

### Skeleton First

Skeleton 是首轮实现确认点，不再只是内部任务。带 prototype 的 UI Change 在详细实现前必须有 1440px Skeleton 证据或等价视觉确认，避免后续才发现布局方向不一致。

### Evidence Gate

实现和返修完成前必须记录：

- 1440px 默认首屏截图或等价证据。
- 关键交互截图，例如侧边栏展开/收起、用户菜单、二级浮层、弹窗、筛选、空态和权限差异。
- 高风险视觉点的 computed style 证据。
- Mock/API 边界声明。

返修后相关旧截图和样式证据视为 stale，必须重新取证。

## Affected Assets

- `rules/ui-design.md`：将详细门禁写入 UI 规则。
- `docs/standards/prototype-ui-acceptance.md`：新增可执行标准与模板。
- `AGENTS.md`：更新 UI 读取路由和流程红线。
- `docs/README.md`：补充专项标准索引。
- `.agents/skills/req-opsx/SKILL.md`：生成 Change 时要求 UI Contract、computed style 和 Mock/API 边界。
- `.agents/skills/opsx-apply/SKILL.md`：实现阶段要求 Contract、Skeleton、截图、computed style 和 Mock/API 证据。
- `.agents/skills/opsx-modify/SKILL.md`：返修阶段要求对照 Contract 并刷新证据。

## Risk

- 风险：增加 UI Change 前置工作量。
- 缓解：仅对带 prototype、AC-PROTOTYPE、UI Skeleton 或明确引用既有页面视觉的 Change 强制执行，普通后端或非 UI Change 不受影响。

