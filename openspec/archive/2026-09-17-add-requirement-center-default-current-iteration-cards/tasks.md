# Tasks

## 1. UI Contract And Skeleton

- [x] 1.1 阅读当前需求中心实现，确认默认筛选状态、Sprint 选择器、对象类型选择器、刷新行为、稳定 selector 和测试框架。
- [x] 1.2 先实现或重构筛选骨架，再细化行为：Sprint 多选默认当前迭代、清空/重置语义、空态/错误态容器和响应式工具栏布局；验收返修已移除独立范围触发器/chip 与范围提示模块。
- [x] 1.3 为 Sprint 多选默认选中、单 Sprint 缩小、清空 Sprint、重置动作和空态增加稳定 selector；验收返修确认不新增 `requirement-range-*` selector。
- [x] 1.4 在实现记录中声明 Mock/API 边界：确认当前上下文 API 是否已提供 Sprint 状态、iteration 和独立 Change 成员关系；若不足，先更新 API 范围再继续实现。

## 2. Current Iteration Facts And Filtering

- [x] 2.1 从授权 Sprint 生命周期事实中派生当前 Sprint 候选，将 `iterations/change/` 下 planning 与 in_progress Sprint 视为当前迭代，并默认排除 `iterations/archive/`。
- [x] 2.2 使用同一授权对象集合，将默认当前迭代范围应用到 REQ、BUG 和独立 Change 卡片。
- [x] 2.3 实现多个当前 Sprint 时默认多选并集，并允许用户在 Sprint 下拉中显式缩小到单个 Sprint。
- [x] 2.4 实现无当前迭代、当前迭代为空、自定义 Sprint 选择和错误态，不得在用户未显式清空 Sprint 时回退到全部卡片。
- [x] 2.5 手动刷新保留用户显式 Sprint 选择；空间或项目切换后重新计算默认 Sprint 选择，并忽略上一上下文的 stale 响应。

## 3. Statistics, Permissions And Safety

- [x] 3.1 确保统计、阶段数量、卡片列表和空态均使用当前范围的同一个过滤结果。
- [x] 3.2 确保范围候选、结果数量、搜索提示和诊断信息只包含当前用户有权访问的对象。
- [x] 3.3 确保错误与空态不暴露本机路径、堆栈、原始治理文档、密钥、token、`.env` 内容或未授权对象身份。
- [x] 3.4 保留现有 REQ/BUG/Change 阶段映射、文档入口、动作门禁、独立 Change 去重和归档可见性语义。

## 4. Observability And API Boundary

- [x] 4.1 验证页面加载、Sprint 选择变化、重置、刷新和上下文切换行为事件只记录脱敏范围和结果摘要。
- [x] 4.2 验证需求中心上下文请求日志只记录安全元数据、状态、耗时、结果数量和脱敏错误码。
- [x] 4.3 若 API 响应字段、OpenAPI、Orval/客户端类型或请求封装行为变化，同步更新 `docs/03-api-index.md`、API 治理说明、OpenAPI/客户端产物和聚焦测试。
- [x] 4.4 若无需 API 契约变化，在 Change trace 和验证记录中记录 N/A 原因。

## 5. Prototype-driven UI Validation

- [x] 5.1 先实现 UI Skeleton，并在关闭 UI 细节任务前采集默认当前 Sprint、多当前 Sprint、无当前/当前为空和清空 Sprint 状态的 1440px 证据。
- [x] 5.2 验证深浅主题、窄视口、长 Sprint ID、长卡片标题、Sprint 多选换行、sticky header 和横向看板滚动。
- [x] 5.3 采集 Sprint 多选触发器高度、工具栏 gap、文字颜色、边框、背景、sticky header、空态和 overflow 行为的 computed style 证据。
- [x] 5.4 若实现决策改变范围选项、API 边界、观测状态或原型假设，更新关联 REQ acceptance 或 trace。

## 6. Tests And Documentation

- [x] 6.1 增加默认当前 Sprint 选中、多当前 Sprint 并集、单 Sprint 缩小、清空 Sprint 查看全部/未纳入迭代、选择历史/归档 Sprint 和重置语义的聚焦测试。
- [x] 6.2 增加手动刷新保留显式范围、项目/空间切换重算默认范围和 stale 响应保护测试。
- [x] 6.3 增加无当前 Sprint、当前 Sprint 无卡片、解析失败、权限失败和脱敏错误态测试。
- [x] 6.4 运行相关前端、后端/API、类型、OpenSpec 和 Sprint scope 检查，并在 Change trace 记录命令结果。
- [x] 6.5 归档前确认 requirement.md、acceptance.md、trace.md、Change design.md、spec delta、实现证据和验证结果一致。

## 验收返修记录

- [x] 7.1 根据验收反馈移除独立范围按钮组，不新增 `当前迭代｜全部｜历史｜未纳入迭代｜归档` 筛选。
- [x] 7.2 根据验收反馈移除筛选模块下方提示模块，当前迭代仅通过 Sprint 多选下拉默认选中表达。
- [x] 7.3 根据 Sprint 下拉支持多选的事实，将单当前 Sprint 默认选中 1 项、多当前 Sprint 默认选中全部当前 Sprint，清空 Sprint 后展示全量授权卡片。
- [x] 7.4 根据验收反馈将默认 Sprint 多选调整为当前 Sprint + `未纳入 Sprint`，确保规划前待处理对象默认可见，历史/归档 Sprint 仍需显式选择。
