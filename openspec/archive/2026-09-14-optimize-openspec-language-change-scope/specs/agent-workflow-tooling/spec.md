## ADDED Requirements

### Requirement: OpenSpec 中文优先语言校验

MoonBox MUST 提供 OpenSpec 中文优先语言校验脚本，用于检查 active Change 和按需归档 Change 中的英文脚手架标题与英文任务项。脚本 MUST 支持默认全量 active Change 校验，也 MUST 支持按一个或多个 Change ID 聚焦校验，避免并行 Change 的语言问题互相阻塞当前 Change 的验收结论。

#### Scenario: 默认校验全部 active Change

- **WHEN** 系统运行 `python scripts/validate-openspec-language.py`
- **THEN** 脚本 MUST 校验 `openspec/changes/` 下全部 active Change 的受控 Markdown 文档
- **AND** 发现英文脚手架标题或英文任务项时 MUST 返回失败

#### Scenario: 按 Change 聚焦校验

- **WHEN** 系统运行 `python scripts/validate-openspec-language.py --change <change-id>`
- **THEN** 脚本 MUST 只校验指定 Change 的受控 Markdown 文档
- **AND** 其他并行 active Change 的语言问题 MUST NOT 影响该命令的通过或失败结论
- **AND** 目标 Change 不存在时 MUST 返回失败并说明未找到目标

#### Scenario: 聚焦校验归档 Change

- **WHEN** 系统运行 `python scripts/validate-openspec-language.py --include-archive --change <change-id>`
- **THEN** 脚本 MUST 在 active Change 与归档 Change 范围中查找目标
- **AND** 找到目标归档 Change 后 MUST 校验其受控 Markdown 文档

#### Scenario: 输出非当前 Change 残留报告

- **WHEN** 系统运行 `python scripts/validate-openspec-language.py --change <change-id> --residual-report`
- **AND** 当前 Change 中文优先校验通过
- **THEN** 脚本 MUST 返回成功
- **AND** 脚本 SHOULD 输出非当前 Change 的中文残留摘要
- **AND** 非当前 Change 的残留 MUST NOT 改变当前 Change 的退出码

#### Scenario: req-opsx 生成后自动运行聚焦校验

- **WHEN** `/req-opsx <REQ-full-id>` 成功生成或确认当前 OpenSpec Change
- **THEN** 系统 MUST 运行 `python scripts/validate-openspec-language.py --change <change-id> --residual-report`
- **AND** 当前 Change 的中文优先失败 MUST 阻断本次 `/req-opsx` 完成
- **AND** 其他 active Change 的中文残留 MUST 以全仓残留分离报告呈现
- **AND** 其他 active Change 的残留 MUST NOT 作为当前 REQ 链路的失败结论

### Requirement: OpenSpec 校验总入口聚焦执行

MoonBox MUST 提供 OpenSpec 校验总入口脚本，用于串行运行当前 Change 常用 OpenSpec 文档门禁。总入口 MUST 支持按 Change ID 聚焦执行，并在聚焦模式下运行当前 Change 中文优先校验与 `openspec validate` 结构校验。

#### Scenario: 总入口按 Change 聚焦校验

- **WHEN** 系统运行 `bash scripts/validate-openspec.sh --change <change-id> --residual-report`
- **THEN** 脚本 MUST 只用目标 Change 作为当前中文优先校验范围
- **AND** 脚本 MUST 运行 `openspec validate <change-id>`
- **AND** 非当前 Change 的中文残留 MUST NOT 改变当前 Change 的退出码

#### Scenario: 总入口保持默认全局校验

- **WHEN** 系统运行 `bash scripts/validate-openspec.sh`
- **THEN** 脚本 MUST 运行目录结构校验
- **AND** 脚本 MUST 运行默认全量 active Change 中文优先校验

#### Scenario: 总入口聚焦归档 Change

- **WHEN** 系统运行 `bash scripts/validate-openspec.sh --include-archive --change <change-id> --residual-report`
- **AND** 目标 Change 已位于 `openspec/archive/`
- **THEN** 脚本 MUST 校验目标归档 Change 的中文优先文档
- **AND** 脚本 MUST 校验归档后已合并的正式规格结构

#### Scenario: bug-opsx 生成后自动运行聚焦校验

- **WHEN** `/bug-opsx <BUG-full-id>` 成功生成或确认当前 OpenSpec Change
- **THEN** 系统 MUST 运行 `python scripts/validate-openspec-language.py --change <change-id> --residual-report`
- **AND** 当前 Change 的中文优先失败 MUST 阻断本次 `/bug-opsx` 完成
- **AND** 其他 active Change 的中文残留 MUST 以全仓残留分离报告呈现
- **AND** 其他 active Change 的残留 MUST NOT 作为当前 BUG 链路的失败结论
