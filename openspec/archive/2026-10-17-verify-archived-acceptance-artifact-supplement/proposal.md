## 背景

已归档 BUG-0025 的完整验收清单为 52/52 passed，但归档 `verification.md` 追加最终说明后，AC-003 的附件哈希与原清单不符。Sprint 关闭时的 Workflow Sync 因此把已通过验收投影为 pending。原验收清单必须保持不变，补证需要可核验的独立记录。

## 变更内容

- 对已归档 Change 的单项命令型 AC 提供受控补证：重跑原计划命令，记录当前输入指纹和附件哈希。
- Workflow Sync 仅在补证与原清单、当前文件和原计划完全匹配时接受该附件；其他 AC 仍按原清单验证。
- 为 BUG-0025 的 AC-003 生成补证，并复核 Sprint 关闭投影。

## 能力范围

### 新增能力

- `archived-acceptance-artifact-supplement`：保留原验收清单并验证已归档命令型 AC 的附件补证。

### 修改能力

无。

## 影响范围

治理脚本、Workflow Sync 验收投影和脱敏验收证据；不涉及业务 API、数据库、Web、客户端、部署或产品安全边界。
