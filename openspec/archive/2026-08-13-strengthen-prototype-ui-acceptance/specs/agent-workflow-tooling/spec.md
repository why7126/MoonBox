## MODIFIED Requirements

### Requirement: 原型驱动 UI 开发门禁
系统 SHALL 对带 `prototype/` 的 UI 页面建立从需求完善、OpenSpec 转换、实现、返修到归档的连续门禁，确保原型拆解、UI Contract、UI Skeleton 首轮确认、1440px 与关键交互视觉验收、computed style 验收、Mock/API 边界声明、图标文案一致性检查和 REQ 文档最终一致性检查均被记录并通过。

#### Scenario: 需求完善拆解 prototype
- **GIVEN** 一个 UI REQ 存在 `prototype/web/` 或等价页面原型目录
- **WHEN** 执行 `/req-complete <REQ-full-id>`
- **THEN** 系统 SHALL 在需求文档中记录原型页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点
- **AND** 系统 SHALL 将可测试验收项写入 `acceptance.md` 并在 `trace.md` 记录 `prototype_refs`

#### Scenario: OpenSpec 承接 UI Contract 和 UI Skeleton
- **GIVEN** 一个带 prototype 的 REQ 已进入 `/req-opsx`
- **WHEN** 系统生成 active Change
- **THEN** Change `design.md` SHALL 包含 UI Contract，声明事实源优先级、页面入口、信息架构、视觉 token、交互状态、图标文案、Mock/API 边界、权限规则和一致性参照
- **AND** Change `design.md` SHALL 包含 UI Skeleton 章节
- **AND** Change `tasks.md` SHALL 包含先完成 UI Contract 与 UI Skeleton 再实现细节的独立任务
- **AND** Change SHALL 记录 prototype 与 acceptance 的冲突处理结论

#### Scenario: 实现阶段执行视觉和样式验收
- **GIVEN** 一个带 prototype 的 UI Change 正在 `/opsx-apply` 或 `/opsx-modify`
- **WHEN** 相关 UI 任务准备标记完成
- **THEN** 系统 SHALL 先在 1440px 桌面视口完成视觉验收
- **AND** 系统 SHALL 对关键交互记录截图或等价证据
- **AND** 系统 SHALL 对原型敏感或曾返修的视觉点记录 computed style 或等价检查
- **AND** 系统 SHALL 记录 Mock/API 边界、验收命令和结果摘要

#### Scenario: 前后台一致性检查
- **GIVEN** 一个带 prototype 的 UI Change 需要对齐前台、后台或既有页面
- **WHEN** 系统执行 `/req-opsx`、`/opsx-apply` 或 `/opsx-modify`
- **THEN** 系统 SHALL 对品牌区、菜单分组、导航密度、active 态、折叠按钮、用户菜单、浮层层级、字体 token、图标尺寸、hover/click outside、危险色、图标和文案进行 checklist 验收

#### Scenario: 归档前检查 REQ 最终一致性
- **GIVEN** 一个带 prototype 的 UI Change 准备 `/opsx-archive`
- **WHEN** 系统执行归档前文档同步门禁
- **THEN** 系统 SHALL 复核 linked REQ 的 `requirement.md`、`acceptance.md`、`trace.md` 与 Change 设计、实现证据、验收结果一致
- **AND** 若发现验收口径、非目标、UI 行为、Mock/API 边界、computed style、视觉证据或实现差异，系统 SHALL 阻断归档并要求先回填或返修
