---
requirement_id: REQ-0047-governance-command-durable-recovery
title: 治理命令持久化阶段与幂等恢复闭环验收标准
created_at: "2026-10-19 15:52:31"
updated_at: 2026-10-20 08:19:17
acceptance_status: passed
---

# 治理命令持久化阶段与幂等恢复闭环验收标准

## 状态与范围

实现验证已完成，以下勾选依据合成回归、真实隔离产品事实及视觉签认；机器验收结论由下方结果回填记录。首期 req/bug-review，全范围以 requirement.md §10 为准。

- [x] AC-001 启动完整性（FR-001、004）：baseline-only、缺失/非法 operation、身份或绑定不匹配在模型调用前阻断，原基线和成果不变；合法准备通过。
- [x] AC-002 部署兼容（FR-004、010）：backend/worker/controller 能力交集支持才启动；缺心跳、未知或不支持 schema 阻断写入，兼容范围重叠时不同版本号可以协作。
- [x] AC-003 独立状态与阶段（FR-002、003）：逐阶段断点保存指纹及操作版本；执行 completed/failed/stopped 与业务结果分开，原终态不改写，unknown 未确认不接管。
- [x] AC-004 生成后恢复（FR-005、006）：REQ、BUG 各通过真实入口生成完整成果后中断服务，重启只续接校验/应用，不新增模型调用；不完整成果明确需重新生成。
- [x] AC-005 部分提交与同步（FR-003、006、009）：逐文件写入、删除旧目录、Workflow Sync 前后中断，依据原日志安全重放；冲突保留现场；恢复后全部原有子文档完整且 approved/review 与索引一致。
- [x] AC-006 请求幂等（FR-001、005）：相同键/输入返回原操作，同键不同输入冲突；响应丢失和并发恢复仅一份应用/迁移；迟到旧版本不覆盖新结果。
- [x] AC-007 主动停止（FR-007）：应用前停止取消未领取自动恢复并等待用户确认；应用中只允许原事务一致性处理；未知执行器不可接管；无自动模型重生成或隐式回滚。
- [x] AC-008 预算与退避（FR-007）：全操作最多 3 次自动重试，间隔 2/10/30 秒按持久化时间调度，重启不重置；锁竞争不扣次数，超时先回读；手动确认仅一次尝试且不重置自动计数。
- [x] AC-009 权限与冲突（FR-005）：读取可恢复后再撤权、换绑定或修改源，提交重新校验并拒绝；不得覆盖较新成果；半迁移保留保护状态。
- [x] AC-010 过期与旧记录（FR-004、006）：窗口按终结后 7 天和现有配置较早期限计算，重试不续期；配置缺失/成果不可用有明确原因；旧记录无法证明时不补空记录、不改终态。
- [x] AC-011 结果读取（FR-008、009）：业务完成仅在校验、应用、同步、回读齐备后确认；页面错误只影响读取，刷新不产生模型/写入；无凭据不能显示完成。
- [x] AC-012 动作能力与入口（FR-008）：可恢复/冲突/过期/撤权/等待停止确认状态下按钮与能力一致；续接确认绑定原对象和版本，重复提交去重；无能力无假按钮。
- [x] AC-013 观测与脱敏（FR-008）：API 与后台恢复关联同一操作及各次尝试；可信 request_id 由服务端生成，客户端关联字段不用于鉴权；脱敏/截断且无原始 Prompt、凭证和本机路径，观测失败不篡改业务结果。
- [x] AC-014 保护与清理（FR-007）：活跃/应用中引用不被普通清理删除；到期禁止新领取；半迁移清理受阻并可追溯，管理员处置需授权；已完成释放引用，最小诊断90天等周期遵循标准。
- [x] AC-015 兼容与数据库（FR-010）：SQLite/MySQL 的唯一应用、并发领取、预算和过期测试一致；旧记录转换可验证且保留原记录；仅评审支持全恢复，其他动作逐项列明支持与 N/A。
- [x] AC-016 全链路交付（FR-009、010）：独立 REQ 与 BUG 完成正常路径及中断路径，核对实际服务制品、唯一应用、原会话、完整文件、刷新重连后的看板；合成、真实运行和视觉证据分别记载。

## 故障与证据矩阵

| 组合 | 样本及检查 | 证据类型 |
|---|---|---|
| 准备/生成/校验/应用/同步/回读提交前后中断 | 对两类评审做隔离断点注入；记录停止点和未完成步骤 | 合成回归 |
| 正常及生成后重启 | REQ、BUG 各自独立真实对象；预先验证样本 registry/index/元数据 | 真实产品轮次 |
| 部分应用/响应丢失/并发 | 核对副作用次数、指纹、围栏及唯一应用 | 合成回归，受控产品恢复补证 |
| 原轮次 stopped/failed | 原终态与业务已应用可以共存；不能伪造 completed | 真实观察及合成覆盖 |
| 版本/权限/绑定/过期/预算 | 时间可控测试，不等待7天，不修改真实用户权限或清理数据 | 合成回归 |
| 操作详情与确认 | 1440×900、390×844，按下方矩阵采样 | 浏览器截图与 computed style |

真实样本每类最多一个正常样本和一个恢复样本；失败先定位夹具或环境原因，不无限创建样本。测试隔离配置、凭证私存、清理边界及原部署未更新须记录。通过条件是成果保留、副作用唯一、原终态真实；模型完成文字和命令测试不能替代页面或应用证据。

## 横切 AC（knowledge-base）

无 admin-list/admin-form/admin-modal/media-upload 标签，本需求是前台 Chat 局部恢复交互，不复制管理端或上传门禁。无这些标签的 AC-XCUT；以下为领域知识库检查：

- [x] AC-KB-001 来源 docs/knowledge-base/incidents/20261019-review-operation-record-contract.md：验证记录生产与消费契约、两次写入间中断和实际部署版本，不能只检查工作区名单。
- [x] AC-KB-002 同上：保留被拒绝/中断样本，夹具先通过初始索引及预期合法迁移预检，不把预检或历史样本当作当前产品通过。
- [x] AC-KB-003 来源 docs/knowledge-base/retrospectives/sprint-009-retrospective.md：成果保留/过期/删除保护作为同一生命周期验收，合成故障与真实运行分开报告。

## 原型驱动 UI AC

- [x] AC-PROTOTYPE-001 实施前核对 prototype/web/context.md 的区域、状态、数据和动作矩阵，更新 Change UI Contract；文档阶段已拆解不等于产品通过。
- [x] AC-PROTOTYPE-002 先完成 UI Skeleton 的插槽、状态容器及选择器，并保留首轮1440px确认后再完成细节。
- [x] AC-PROTOTYPE-003 1440×900覆盖可恢复、确认、提交中、恢复完成、阻断/过期；390×844覆盖确认滚动与长原因。采集按钮、对话框宽度、字体、颜色、焦点及错误状态样式，验证键盘退出和不溢出。
- [x] AC-PROTOTYPE-004 归档前核对 PRD、流程、故事、trace、原型与最终实现一致，真实 API/Mock 边界明确；返修后重采受影响证据。

## 数据采集与链路观测

product_data_collection_observability: applicable；affected_layers: API、DB、request_logs、usage_events、task_traces、task_trace_spans、Web。validation: AC-013/014/015；直接后台入口不伪造行为事件；不新增计费事件。本轮API、增量数据库schema与生成客户端已同步文档和测试；未执行生产迁移、配置或权限变更。实际证据与验证范围见关联Change的verification.md。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-20 08:19:17
accepted_by: workflow-sync
source_change: add-governance-command-durable-recovery
source_sprint: sprint-010
evidence: [openspec/archive/2026-10-19-add-governance-command-durable-recovery/evidence/acceptance/20261019181959291154-9d93348f/summary.md]
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

