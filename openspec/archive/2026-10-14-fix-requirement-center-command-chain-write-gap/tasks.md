---
title: 需求中心治理命令链真实写入修复
created_at: '2026-09-29 16:07:39'
updated_at: 2026-10-14 00:24:05
---

# 需求中心治理命令链真实写入修复

## 实施

- [x] AF-045：补齐评审 CHANGELOG 目标行的阶段与下一步校验和后端收尾；隔离 BUG/REQ 产品轮次 applied/verified、文件与看板一致，AC-051 定向通过。详见 [返修台账](acceptance-fixes.md#af-045-ac-051-评审索引阶段与下一步遗漏)。

- [x] AF-044：真实模式未知命令在创建对象会话前给出 Codex 命令提示；补未知命令与 REQ Generate 回归。详见 [返修台账](acceptance-fixes.md#af-044-未接入命令误建产品对象会话)。

- [x] AF-043：修正同会话旧未绑定 prepared 候选在更新且已应用的候选之后重新生效；增加聚焦回归并完成隔离产品 generate→complete 闭环。详见 [返修台账](acceptance-fixes.md#af-043-旧未绑定候选阻断同会话续接)。

- [x] AF-040：移除规划中草稿独立标签，保留内部状态、severity、负责人和动作；见 acceptance-fixes.md。

- [x] AF-033：按当前轮次选择候选，阻止已停止评审的 running 候选拦截原会话后续 Sprint 命令；保留未绑定候选兼容及原成果。见 acceptance-fixes.md。

- [x] AF-030：移除完善中标签，长负责人名称不溢出，保留子文档/提示/动作/门禁；见 acceptance-fixes.md。

- [x] AF-029：区分草稿/完善中卡片、展示已有子文档和补证提示，保留继续完善与评审门禁；验证见 acceptance-fixes.md。

- [x] AF-028：完整校验后零差异返回 unchanged，无 application 与写入；重复 complete 和历史入口回归，见 acceptance-fixes.md。
- [x] AF-027：bug-complete 当前轮候选、权限、草稿/确认门禁与自动回写；同会话 generate→complete 实际验证，见 acceptance-fixes.md。
- [x] AF-026：原工作区成果续接、临时锁预检、req-complete 候选校验自动应用及运行态恢复验证；见 acceptance-fixes.md。

- [x] AF-025：准备失败终态、历史安全恢复、未应用成果保护与轻量阻断提示；证据见 [返修台账](acceptance-fixes.md#AF-025-工作区准备失败终态与成果保留)。

- [x] 扩展治理命令能力矩阵，明确真实候选写入、真实应用写入、demo 模拟和仅展示命令。
- [x] 后端 `governance-preparations` 支持 `BUG-*` 与 `bug-generate`，并保持 `req-generate` 兼容。
- [x] 后端候选校验为 `bug-generate` 建立文件 allowlist：目标 BUG `bug.md`、`trace.md`、BUG registry 和 BUG CHANGELOG。
- [x] 后端应用成功后同步目标 BUG 状态、CHANGELOG 下一步、candidate/application 记录与 Task Trace。
- [x] 前端需求中心真实模式接入 Bug Generate 准备、候选审阅、应用轮询和刷新闭环。
- [x] 前端真实模式对 `complete`、`review`、`sprint-propose`、`opsx` 系列未接入动作展示明确不可执行提示和 Codex 命令，不模拟成功。
- [x] 如 API schema 或客户端类型变化，同步 OpenAPI、Orval、API 文档和错误码说明。

## 验证

- [x] 后端测试覆盖 `req-generate` 不回退、`bug-generate` 成功、不支持 action 拒绝、越界写入拒绝和应用后状态同步。
- [x] 前端测试覆盖 BUG 生成入口、未实现命令提示、非 demo 不模拟成功和看板刷新事实源投影。
- [x] 运行需求中心相关后端、前端、TypeScript 与 OpenSpec 校验。
- [x] 记录真实浏览器或接口观察证据，区分合成回归与真实观察。

## 文档与同步

- [x] 同步 `docs/03-api-index.md`、必要的数据库/API/观测说明和需求中心命令能力说明。
- [x] 更新 BUG-0025 acceptance 与 trace 的实施证据。
- [x] 通过 Workflow Sync 维护 BUG、Sprint 与 Change 状态。

## 验收返修

- [x] AF-032：兼容评审 status/result、明确拒绝原因并补齐原候选重验；回归与真实恢复证据见 acceptance-fixes.md。

- [x] AF-024：取消固定 300 秒默认截止，补充长历史有界恢复及超过 300 秒回归；原轮次恢复与续接证据见 acceptance-fixes.md。

- [x] AF-023：运行中输出独立 assistant 内容区；真实组件落库前后与历史恢复宽度回归，见 acceptance-fixes.md。

- [x] AF-022：独立 Worker 心跳、capabilities 原因分类与自动恢复、草稿保留和恢复发送回归；详情见 acceptance-fixes.md。

- [x] AF-020：统一当前治理文件 manifest/revision 门禁，支持未提交内容与全写入命令隔离工作区同步，保护版本变化和未应用成果。
- [x] AF-031：补齐评审候选、目录迁移校验及自动回写，恢复REQ-0027并验证complete→review；证据见 acceptance-fixes.md。
- [x] AF-020：补充全命令矩阵、generate 应用后同会话 complete 与冲突回归；证据见 acceptance-fixes.md。

- [x] AF-001：修正 Bug Generate 产品准备态输入框，用户可见草稿只展示简洁 `/bug-generate <BUG-full-id>` 命令。
- [x] AF-001/AF-009：将完整内部治理约束从用户消息中移除；最终由后端根据治理 candidate 恢复 execution prompt，前端只发送 display_prompt。
- [x] AF-001：补充前端回归用例和返修台账，详见 `acceptance-fixes.md`。
- [x] AF-002：修正 Bug Generate 发送后的历史消息展示，只显示用户可理解的短命令，不裸露内部治理约束。
- [x] AF-002：隐藏 `prepared` 且 0 文件的治理成果面板，避免空成果面板常驻。
- [x] AF-002：补充历史消息和治理成果面板回归用例，详见 `acceptance-fixes.md`。
- [x] AF-003：将已接入真实治理候选链路的 generate 命令改为校验通过后自动应用，异常时才进入人工“待应用成果”确认。
- [x] AF-003：补充自动应用、人工重试和已存在 operation 不重复申请的前端回归用例，详见 `acceptance-fixes.md`。
- [x] AF-004：移除 Chat 对话区所有治理成果大面板，保留后台自动应用、状态轮询和轻量提示。
- [x] AF-004：补充无面板、自动应用、失败轻量提示和已有 operation 不重复申请的前端回归用例，详见 `acceptance-fixes.md`。
- [x] AF-005：修正 Chat 对话区 assistant 消息宽度，使 assistant 输出占满消息历史可用宽度，用户消息仍保持右侧气泡宽度限制。
- [x] AF-005：补充 assistant 满宽与用户气泡宽度限制的前端布局回归断言，详见 `acceptance-fixes.md`。
- [x] AF-006：修正 Chat assistant 外层历史轨道宽度，pending candidate 自动应用门禁和历史打开无治理成果面板行为。
- [x] AF-006：补充 pending 自动应用 Network 断言、prepared 空候选不申请和治理面板 DOM 不存在断言，详见 `acceptance-fixes.md`。
- [x] AF-007：修正 Chat assistant 正文 bubble/markdown 视觉块运行态铺满，避免仅源码 max-width 断言不足。
- [x] AF-007：补充 DOM + computed style 回归断言，详见 `acceptance-fixes.md`。
- [x] AF-008：重新构建并部署 Web 产物，补充 dist/运行态 bundle 面板文案断言，防止 localhost:18102 继续使用旧前端构建。
- [x] AF-008：generate 候选自动应用改为 controller-ready 门禁，补充 `governance_applications` 自动创建和历史入口 DOM/Network 回归断言。
- [x] AF-009：将 `req-generate`/`bug-generate` 自动应用迁移到后端 collect/controller，前端历史入口只轮询后端 operation。
- [x] AF-009：Chat 历史只保存 display_prompt，执行器内部治理约束由后端根据 candidate 恢复，不落库内部治理约束。
- [x] AF-009：发送前增加 executor sandbox/dry-run preflight，并区分 `executor_unavailable` 与 `governance_validation_failed`。
- [x] AF-009：补充后端 DB/文件事实源回归、前端 DOM/Network 回归、TypeScript、Web 构建和 dist bundle 断言。
- [x] AF-010：增加 Web 启动构建版本校验和旧 bundle 一次性自动刷新，避免历史入口继续运行缓存旧前端实例。
- [x] AF-010：增加 Chat 历史入口旧治理成果面板 DOM 清理，确保旧节点不再恢复到对话主区域。
- [x] AF-010：补充 `runtimeBuild`、历史入口 DOM、运行态 bundle 和浏览器运行态证据，详见 `acceptance-fixes.md`。
- [x] AF-011：将 Chat 推理程度默认值从 High 改为 Low，同步后端 capabilities 默认、前端 Composer fallback 和回归测试。
- [x] AF-012：统一 BUG-0025 运行态部署验收链路，改用项目标准 `scripts/docker-down.sh` / `scripts/docker-up.sh self-storage-sqlite`，并明确裸 compose 只用于基础局部调试。
- [x] AF-013：修正 Chat 对话区所有 AI/assistant 消息满宽规则，覆盖 req-generate、bug-generate、普通 Chat、执行中 TurnActivity 与 status/alert 输出。
- [x] AF-013：补充 Vitest DOM/computed style 与 Playwright 浏览器宽度采样回归证据，并记录 `chat-workbench.test.tsx` 测试池挂起缺口。
- [x] AF-014：修正 Chat assistant 工具调用/完成状态摘要位置，使其作为轻量 meta 左对齐到 assistant 内容列。
- [x] AF-014：补充状态摘要 computed style 和浏览器盒模型断言，确保正文与执行输出继续保持满宽。
- [x] AF-015：统一 Chat、governance 与 events 网络异常归一化，导航/历史恢复 AbortError 静默处理，局部轮询失败不覆盖已生成成功消息。
- [x] AF-015：补充 NetworkError、AbortError、消息区局部错误和历史会话 turns 轮询失败 DOM 回归断言，详见 `acceptance-fixes.md`。
- [x] AF-016：修正 Chat assistant 运行中满宽规则从 generate 样本扩展为 role=assistant 渲染形态规则，隔离非 assistant activity 限宽。
- [x] AF-016：补充 req-complete 截图场景和 complete/review/sprint/opsx/普通 Chat 命令矩阵 DOM/computed style 回归断言，详见 `acceptance-fixes.md`。
- [x] AF-017：将产品写入型对象命令统一接入后端事实源一致性门禁，阻断执行器 `/work` 看不到当前治理事实源的发送。
- [x] AF-017：补充 stale fact source、缺主文档、只读 explore 例外和全命令矩阵后端回归断言，详见 `acceptance-fixes.md`。
- [x] AF-018：优化 `workspace_fact_source_stale` 错误详情，区分本地治理事实源未提交/未同步、Git 快照不可读和旧部署兜底提示。
- [x] AF-018：补充需求中心 Toast、后端错误详情和 API 响应安全字段回归断言，详见 `acceptance-fixes.md`。
- [x] AF-019：修正产品 backend 在 `governance_root` 投影目录执行 Git 快照门禁导致误报的问题，改为优先使用 `source_root` 完整仓库 Git 快照。
- [x] AF-019：补充投影治理目录无 `.git`、source_root clean/dirty 两类后端回归断言，并同步标准 Chat 部署只读挂载 source_root，详见 `acceptance-fixes.md`。
- [x] AF-021：新增显式本地真实仓库工作区执行模式，所有命令可直接读取并写入 `source_root`，取消该模式下的副本同步和候选二次应用。
- [x] AF-021：补充真实仓库模式的工作区绑定、项目级写入协调、候选已应用记录、会话清理和 diff 状态回归断言，详见 `acceptance-fixes.md`。
- [x] AF-034：修正已评审 REQ/BUG 加入迭代命令的类型参数，并覆盖两类卡片点击后 Chat Prompt；证据见 `acceptance-fixes.md`。
- [x] AF-035：补齐执行镜像工具链、构建与启动预检，完成真实沙箱 OpenSpec 命令及标准部署验证；见 `acceptance-fixes.md`。
- [x] AF-036：隔离未完成 Change 的解析失败，保留权限门禁并回归原会话历史、关联与错误分类；见 `acceptance-fixes.md`。
- [x] AF-037：评审迁移后定向同步注册表与索引、失败保留重试，恢复 BUG-0033 并验证卡片及文档读取；见 `acceptance-fixes.md`。
- [x] AF-038：后端补齐已验证评审的遗漏投影，同步隔离评审工具，覆盖原轮次中断恢复、自动回写和 checkpoint；128 项回归通过，详见 `acceptance-fixes.md`。
- [x] AF-039：修正 BUG 生成准备期 2606 错误分类，验证旧成果保留与新候选续接；详见 `acceptance-fixes.md`。
- [x] AF-041：分级字段已正确时保持 capture.md 字节不变，避免 Bug Generate 四文件候选因无语义改写被拒；聚焦回归 6 项通过，详见 `acceptance-fixes.md`。
- [x] AF-041：在独立产品验证环境用 BUG-9101 隔离样本重跑卡片候选，确认同轮 applied/verified application、事实源与看板一致；详见 `acceptance-fixes.md`。

- [x] AF-042：准备后版本变化的 2606 带 `workspace_fact_source_stale` kind；隔离产品 BUG-0038/0039 的旧基准阻断、新 key 续接及部署后错误态已复验，见 acceptance-fixes.md。
