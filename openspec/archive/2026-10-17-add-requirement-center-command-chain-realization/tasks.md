---
title: 需求中心卡片全命令产品链路真实化任务清单
change_id: add-requirement-center-command-chain-realization
source_requirement: REQ-0027-requirement-center-command-chain-realization
created_at: 2026-09-30 18:06:35
updated_at: 2026-10-04 10:43:55
owner: MoonBox 产品团队
---

# 需求中心卡片全命令产品链路真实化任务清单

## 1. UI Contract 与 Skeleton 先行

- [x] 1.1 复核 `prototype/web/context.md`、`prototype/web/prototype.html`、AC-PROTOTYPE 和现有需求中心组件入口，形成生产 selector 映射。
- [x] 1.2 完成 UI Contract 到实现入口的映射，确认页面、卡片、按钮、浮层、反馈容器、Toast、权限和 Mock/API 边界。
- [x] 1.3 完成 UI Skeleton：卡片动作区、四类浮层容器、反馈容器、状态展示和产物入口占位。
- [x] 1.4 在 1440px 深浅主题下取得 Skeleton 首轮截图或等价 DOM 证据，确认布局、密度、层级和长 ID 不溢出后再进入细节实现。

## 2. 受控动作分发与门禁

- [x] 2.1 梳理八动作现有前端入口和后端 governance/controller/writer/Workflow Sync 能力，明确复用、扩展和不可复用分支。
- [x] 2.2 实现或扩展后端受控动作分发，校验完整 REQ ID、授权项目、对象版本、阶段、材料、动作白名单和权限。
- [x] 2.3 实现只读分析模式，确保分析不写 requirement、trace、registry、CHANGELOG、Sprint 或 OpenSpec，也不推进生命周期。
- [x] 2.4 实现七类写动作的产物写入、校验、Workflow Sync、事实源重读和状态返回顺序。
- [x] 2.5 实现取消、确认、拒绝/延后理由、Sprint 选择、多 active、容量保留和归档门禁的后端裁判。

## 3. 幂等、运行状态与恢复

- [x] 3.1 为写操作建立可查询操作身份和幂等键，同对象冲突写串行执行。
- [x] 3.2 区分受理、运行、阻塞、失败、部分写入、同步失败、版本冲突、权限不足和完成状态。
- [x] 3.3 实现断线、重复点击、请求重试、服务重启、多文件部分写入和 Workflow Sync 失败后的恢复流程。
- [x] 3.4 实现 opsx.start、opsx.apply 和归档投影，确保 REQ canonical 状态在归档前保持 `in_sprint`。

## 4. Web 交互与视觉验收

- [x] 4.1 扩展需求中心卡片动作 UI，传递完整对象身份、动作类型、版本和幂等标识。
- [x] 4.2 实现 `ai-panel`、`action-modal`、`confirm`、`dialog` 四类浮层的加载、取消、提交、错误、成功和恢复提示。
- [x] 4.3 实现或验证外部点击关闭、内部 `stopPropagation` 不误关闭、Esc、Tab 焦点约束和关闭后焦点回到触发器。
- [x] 4.4 完成 1440px、390px、矮视口、深浅主题、权限差异、错误态和长文本溢出视觉验收。
- [x] 4.5 记录关键 computed style：按钮、卡片、浮层、反馈容器、Toast、文档入口和长 ID。

## 5. 数据、API 与观测

- [x] 5.1 如修改 REST API、请求/响应字段、错误码或请求封装，同步 OpenAPI、Orval、`docs/03-api-index.md` 和前后端测试。
- [x] 5.2 如新增或修改数据库结构、索引、迁移、保留周期或恢复记录，同步 SQLite/MySQL schema、迁移、`docs/04-database-design.md` 和数据库测试。
- [x] 5.3 接入 usage_events、request_logs、task_traces 和 task_trace_spans 或声明复用路径，覆盖八动作、写入步骤、同步、恢复和失败分支。
- [x] 5.4 校验 metadata 不保存完整 Prompt、文件正文、请求/响应正文、密钥、Cookie、Authorization header、本机路径或未脱敏治理材料。

## 6. 验证与文档同步

- [x] 6.1 后端测试覆盖八动作阶段门禁、权限、幂等、恢复、Workflow Sync 成功/失败和归档门禁。
- [x] 6.2 前端测试覆盖按钮状态、浮层交互、错误提示、结果查询、权限差异和文本不溢出。
- [x] 6.3 端到端或隔离文件系统测试覆盖 captured → draft → pending_review → approved → in_sprint → opsx.start → applied → archive/done 主链。
- [x] 6.4 补充失败注入测试：部分写入、同步失败、重启恢复、版本冲突和未知外部修改。
- [x] 6.5 运行 OpenSpec、中文标题、产品数据观测、API/DB/UI 相关校验，并把结果回填 Change trace。
- [x] 6.6 根据实现结果同步 linked REQ 的 `requirement.md`、`acceptance.md`、`trace.md`、prototype 口径和 Mock/API 边界。

## 7. 验收返修

- [x] 7.1 AF-033：补齐“事实源唯一，工作区是候选沙箱”完成门禁；writer 在标记 applied 前执行 Workflow Sync、重读事实源，sync 失败保持待恢复。
- [x] 7.2 AF-033：补充后端聚焦回归，覆盖 sync 成功才 applied、sync 失败不 applied。
- [x] 7.3 AF-034：本地常驻部署默认 `workspace_mode: source`，copy 保留为显式隔离模式；补充部署/API/REQ/规格文档与聚焦测试。
- [x] 7.4 AF-035：修复 HTML 预览对象 URL 清理在缺少浏览器 API 时抛异常；前端聚焦回归 122 项通过。
- [x] 7.5 AF-036：source 模式拒绝候选时安全回退同轮治理文件；Chat 默认折叠被拒绝轮次的助手原文，显示事实源拒绝结论；新增回归与独立产品轮次复验。
- [x] 7.6 AF-044：拒绝对象会话接口未列入白名单的动作，新增无会话副作用回归；独立产品新构建复验仍列为 AC-009 待办。
- [x] 7.7 AF-047：持久写入器补同步阶段和结果 hash 恢复门禁，前三个候选动作的隔离故障矩阵通过；详见 `acceptance-fixes.md`。
- [x] 7.7a AF-048：worker 对已终态但仍 running 的候选补幂等收尾扫描；重启后只重读既有工作区，不重启外部轮次。
- [x] 7.7b AF-049：真实 source 首文件中断暴露非完成终态跳过基线读取；修复安全恢复入口，三候选动作六窗口隔离矩阵通过。
- [x] 7.8 AC-011：默认 source 模式七动作四窗口真实轮次与重启分类已逐格核对，旧不可验证外部轮次保持 unknown 安全阻断；整项证据见 `evidence/acceptance/samples/AC-011.md`。
- [x] 7.8.1 为 `sprint-propose`、`req-opsx`、`opsx-apply`、`opsx-archive` 建立持久步骤记录、同步前后判定与安全恢复门禁；四动作已有真实产品中断与重启证据。
  - [x] 7.8.1a 四动作新增私有步骤 hash 日志、同步退出码判定和重启终态分类；隔离 4×6 窗口及后续真实产品注入均已取证。
  - [x] 7.8.2 修复版 source 首文件窗口和四个直接命令的写前、部分文件、同步前后及重启矩阵已覆盖。
    - [x] 7.8.2a 修复候选动作因直接命令日志缺席提前停止；`REQ-9204` 真实首文件中断及重启恢复通过，其余矩阵继续待验。
    - [x] 7.8.2b 采集七动作其余真实写入/同步中断样本，修复 Change 控制文件快照遗漏；归档部分迁移现场安全阻断，未当成整项通过。
    - [x] 7.8.2c 从保留的归档现场走跳过再次合并的后置校验，验证规格 hash 与归档目录唯一；修复自动 Sprint 范围解析对合法无缩进 YAML 列表的漏读。
    - [x] 7.8.2d 新 `req-opsx` 写前轮次重启后为 stopped / no_governance_write，旧外部不可读取轮次保持 unknown、不重放；新 `sprint-propose` 在正式 Sync 成功但 YAML 无效时返回 failed / sprint_source_invalid，保留故障文件后仅修正隔离样本。见 `acceptance-fixes.md` AF-057 与产品轮次证据。
  - [x] 7.8.3 七动作 × 四窗口 28 格逐项映射脱敏产品证据，30 个轮次前缀均有入口；Issue AC-011 签认后重跑完整验收。见 `evidence/acceptance/samples/AC-011-matrix-audit-20261017.json`。

- [x] 7.9 AC-012：四个归档中断位置和未知外部修改逐项完成产品对象轮次与安全续做复验，整项通过后签认。
  - [x] 7.9.1 修复规格合并后、Change 迁移前重试会重复合并的脚本反例；真实 CLI 分段与外部编辑阻断隔离验证通过。
  - [x] 7.9.2 在独立副本中断 Workflow Sync 与 Issue 迁移进程，并验证重复续做零核心差异、目录唯一。
  - [x] 7.9.3 补四阶段完整产品对象 Chat 轮次，复核不提前 done 与脱敏证据后运行聚焦验收。

完整返修台账见 `acceptance-fixes.md`。
