---
created_at: 2026-09-10 08:57:54
updated_at: 2026-09-10 08:57:54
---

# Apply行为验收

目标：识别有可执行任务时提前结束，以及应停止时继续。一次授权覆盖实现、验证、自修、文档和同步，不覆盖新增范围或未授权发布。

## 脚本用法

- `python scripts/validate-apply-behavior.py --self-test`：10个合成场景、44个正反断言。
- `python scripts/validate-apply-behavior.py --trace trace.json`：只读校验指定脱敏轨迹，失败退出1；trace.json替换为实际证据文件。

## 输入格式

```json
{"source":"synthetic","records":[{"trigger":"progress_question","evidence":["case-02"],"tasks":[{"id":"verify","state":"pending","deps":[]}],"gates_passed":false,"action":"continue"}]}
```

source取synthetic或observed。trigger取work、test_failure、progress_question、compaction、user_stop、platform_stop；action取continue、wait、stop、complete。任务state取pending或done，deps引用同快照任务ID；external描述必要外部输入，blocker_evidence为其证据引用。测试失败必须保留pending修复任务，不得作为external。

## 真实运行验收

验收人按事件顺序核对：触发事件→当时任务与依赖→下一次实际工具动作或final→脱敏证据位置。真实记录标observed，证据引用验收章节或稳定事件编号，不得只写“通过”。确认下一步工具动作前没有用户额外发送“继续”。脚本无法证明source和记录真实性，必须人工核对实际会话。

| 场景 | 期望观察 |
|---|---|
| 测试失败 | 自修并重验 |
| 进度插话 | 简短回复后续做 |
| 上下文压缩 | 复用授权，从剩余任务续做 |
| 部署缺配置 | 请求输入同时继续独立任务 |
| 全部依赖登录 | 说明依赖后等待 |
| 用户停止或平台强制终止 | 停止，不无限重试 |
| 勾选完但缺验证 | 补验证，不报完成 |

未发生场景标记未观察，不主动制造平台故障或伪造压缩。合成回归只验证判定器，不等于真实Agent全部场景通过；脚本不是调度器，不保证自动唤醒。禁止记录原始session、prompt、工具正文、凭证、环境配置、真实用户信息或本机绝对路径。
