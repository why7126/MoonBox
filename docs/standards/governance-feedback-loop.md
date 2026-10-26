---
title: 治理执行量化与分级优化闭环
created_at: 2026-10-20 18:26:00
updated_at: 2026-10-25 22:25:00
---

# 治理执行量化与分级优化闭环

## 适用范围与授权

本项目已获用户于 2026-10-20 明确授权，在治理范围内自动优化规范、技能和脚本。机器策略为 `rules/governance-feedback-policy.json`，仅对本项目有效。`enabled: false` 可撤销后续自动优化；策略文件本身和安全底线不属于自动修改范围。用户后续指令与沙箱权限优先，授权不等于自动提交、归档、发布或修改产品业务代码。

每次命令执行接入轻量采集与复盘；不存在问题时不制造优化。只读 explore 保持只读，可运行 dry-run，不因闭环写台账或修改文件。没有运行结束事件的平台由 Agent 在完成门禁后显式 finish；进程被强制终止时记录保持 running/unknown，恢复后按真实中断事实结束，不能伪造自动唤醒。

## 运行事实与指标

统一入口 `bash scripts/project-python.sh scripts/governance_feedback.py --help`。治理 CLI 实现仅使用标准库，但统一入口仍检查 Python >=3.12 和公共依赖 PyYAML，确保后续 Workflow Sync 与 AI Usage 使用同一环境。任何治理写入前先运行入口 `--check`；环境选择与 CI/容器配置见 `scripts/README.md`。Hook 不可归因只降级，禁止临时修改全局环境。

调用入口执行 start，结束执行 finish（失败、中断也记录），finish 自动 review。保留返回的 run ID；相同 ID 重放 finish 不改结束时间，晚到的精确用量可补齐，冲突数值拒绝覆盖。不得事后补造开始时间。本次机制首次安装只能覆盖启用后的执行区间，应说明覆盖缺口。

| 字段 | 口径 |
|---|---|
| wall_seconds | 明确 start 到 finish 的墙钟时长，包含等待；时钟倒退拒绝结算 |
| tokens | 来源提供的实测总量及可用子项；无来源为 null，不是零 |
| usage_mode | actual / estimated_fallback / unavailable；只有完整归因实测参与收益 |
| tool_error_count | 工具报错计数；不冒充真实重试次数 |
| quality | 独立验证通过、失败或未知，不能由命令退出码自动推定验收通过 |
| assets | 使用的文件版本哈希；不存文件正文 |
| optimization_id / depth | 优化自身运行归属与防递归标记 |

同组比较键为 command、task_class、model、environment、validation_profile、workload_key。workload_key 使用脱敏输入指纹或稳定工作量标识；不得使用客户名称/原文。unknown 不进入收益比较。同组之外不混算。优化前后目标文件版本必须分别一致且不同。缺少阶段观测时不声称有模型耗时、人工等待或工具耗时拆解；并行任务累计时间不等于墙钟时长。

缓存输入与推理输出属于来源口径中的子项，不能再加到 total_tokens。会话 Hook 的 import_usage 只保存数值和身份哈希，标记 provisional；不会把单个 turn 或当前未完成会话冒充完整调用。宿主精确边界用量可通过 finish --tokens 补齐；不能把整个会话累计值直接填入某次调用。未取得精确值时保留 unavailable，照常报告时间和质量。

## 分级与自动实施

1. review 识别失败、工具错误、超时阈值和用量缺失，输出 hypothesis，不直接确认根因。Agent 结合最小会话片段、错误类别、版本和测试补证；证据转存当前 Change 内脱敏摘要。
2. 无行为文档修正为 nonbehavioral，技能/脚本/规则行为修正为 behavioral；权限、安全、验收门禁放宽或范围扩展为 boundary，不能自动实施。对受保护文件按路径硬拒绝；语义边界由 Agent 复核并声明，脚本不声称能自动理解补丁语义。
3. 明确授权下，Agent 自动执行 `/spec-opt` 创建或复用纯治理 Change，纳入 Sprint；先跑身份、Sprint 选择/容量和作用域门禁。非本项目授权或业务需求保持原 REQ/BUG 流程。默认不自动创建业务 Issue。
4. 优化分析前以 start --purpose optimization 计成本，finish 后通过 plan --cost-run 绑定。plan 记录文件基线哈希、证据哈希、风险和总预算估算；重复来源和文件集复用同一个候选。
5. decide 重新核对授权、预算、文件版本、Change 规格、Sprint 范围和 opsx.start dry-run；不通过则 blocked。allowed 后 Agent 按本次候选文件清单实施，保持当前工作区其他改动；脚本从不执行会话内的 shell 或补丁。Change/Sprint事实源写入仍使用专用脚本，不把它们当作任意优化文件。
6. 修复与验证使用 start --optimization-id 计入同一成本；每批前复核预算，运行结束后检查剩余额度。根因未确认、关键验证失败或缺失时不得标记交付成功。预算不提供强制杀进程功能，不中止必要数据保护；到限后不启动下一批自动优化，记录实耗和恢复动作。
7. 修改稳定后集中运行相关测试和治理门禁，更新 Change trace、治理日志和索引；接续 opsx-accept。通过 seal 绑定验证证据和交付文件哈希，修复通过后进入 observing，收集后续可比调用，再 evaluate。不能为获得真实长期收益而制造业务任务。
8. depth 非零的优化运行只记成本，不生成下一层优化；同一来源最多一个已放行候选，防止换标题绕预算。主任务与自动优化的状态分开报告，优化受阻不抹除主任务交付事实。

## 预算与成本

当前初始策略：自动优化每个候选总预算 600 秒、30000 Token，同类问题冷却24小时，最少 3 个基线和 3 个后续样本，性能退化容差 10%，慢调用提示线 300 秒。这些是可调运行护栏，不是已经实现的性能承诺；不得擅自调整策略来让失败通过。首次安装由本次明确 spec-opt 授权覆盖，采集覆盖范围如实报告。

估算用于事前门禁，实测用于预算消耗和收益。分析、实现、验证均计入 optimization_id；按唯一运行 ID 去重。缺失分析成本或实际 Token 时自动实施阻断，保留候选与推荐动作；已有明确单次任务授权可继续原任务，但不得把它伪装为自动优化已满足预算。进行中的子运行阻止启动另一个子运行，避免共享预算并发超发。

## 效果与回退

基线中位数 × 后续样本数 − 后续实耗总和 − 全部优化自身成本 = 净节省。

时间与 Token 分开计算，输出样本量、中位数、优化成本和净节省，不折算虚构价格。只有同组完整样本、版本成立、质量通过、成本完整且两项净节省均不为负、至少一项为正时才为 benefit-confirmed。只有修复验证通过时仍是 observing。样本不足、未知模型、用量缺失或成本未回收，不能宣称收益确认。

后续质量失败优先标记 regressed；达到最小样本量后，时间或Token中位数超过容差也标记 regressed。Agent 对退化按证据分析，必要时仅撤回本次优化差异，并回归验证；禁止 git reset、覆盖用户改动或自动回滚整个仓库。evaluate 不直接改文件，避免与当前活动修改冲突。后续补齐样本可再次评估同一候选。

## 持久化与保留

本地台账位于已被 Git 忽略的 `logs/governance-feedback/`。单文件原子替换、目录级锁和稳定候选身份防止重放覆盖；不持久化 prompt、系统指令、完整会话、工具输出正文、凭证或本机路径。文件名只使用运行/候选随机标识；只保存经过白名单投影的指标、仓库相对路径与哈希。

prune 默认清理超过30天、没有被候选或效果记录引用的已结束运行及暂态用量；活动或被引用记录保留，不能清理证据依赖。需要长期留存的结论以脱敏摘要进入 Change evidence 与治理日志，不提交原始本地台账。自动 Hook 写入失败非阻断并输出 warning，不伪装采集完成。

## 调用示例与执行顺序

使用 CLI --help 获取 start、finish、review、plan、decide、seal、evaluate、show、prune 的完整参数。start 要填写全部比较键；缺失真实模型时可写 unknown，并保持收益待观察。finish --tokens 只接收覆盖该运行的实测总数，缺失时省略。

正常顺序：start → 主任务和验证 → AI Usage Hook → finish/review → 发现问题时记录优化分析成本 → spec-opt规划/证据/Sprint → plan → decide → 实施与验收成本 → 后续样本 evaluate。遵守现有串行写事实源规则。只读探索不执行持久化部分。

## 验证入口

`src/backend/.venv/bin/python -m pytest tests/unit/test_governance_feedback.py tests/unit/test_ai_usage.py -q`

`scripts/validate-agent-context-budget.py` 检查中央入口引用和策略基础字段；完整行为由测试覆盖。合成收益用例只证明计算逻辑，CLI生命周期实测只证明采集路径，不代表真实项目效率已经提升。

采集入口开销可用 `bash scripts/project-python.sh scripts/benchmark-governance-feedback.py --iterations 20` 测量，输出真实本地中位数、P95和样本数，临时台账自动清理；不据此宣称历史任务收益。plan --problem 使用稳定问题分类，同组/文件集/问题去重，未解决候选复用，终态候选在冷却期内不重复生成。

## 归档与桌面会话用量兼容

归档 wrapper 复用 Workflow Sync 的 Change 范围 Sprint 解析，不从 trace 单个字段推断归属。采集器支持用户消息字符串和 input_text/text 内容块数组，忽略图片和旁路 token_usage_record；只从 token_count 的 last_token_usage 取值。warnings 区分会话缺失、用户消息未识别和 Token 缺失。

历史已完成命令可重放用量 Hook，不重复归档。同一次指令涉及多个 Change 时一并传入，按 turn_hash 去重；不能将共享 turn 重复计成本。当前未结束调用的用量保持 provisional，不冒充本次精确成本。
