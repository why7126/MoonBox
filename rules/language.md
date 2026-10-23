---
purpose: 全局规则
content: 团队研发规范和AI约束
source: AI自动生成初稿，项目团队确认
update_method: 项目初始化后由人工确认；后续由AI辅助更新并经人工Review
created_at: 2026-06-13 00:00:00
updated_at: 2026-10-23 08:30:47
note: 适用于MoonBox项目模板
---

# 语言规范

产品、需求、设计、测试、OpenSpec 规范正文和长期治理文档 MUST 使用中文优先编写；代码标识符使用英文；API 字段使用英文 snake_case 或 camelCase，按接口约定统一。

## OpenSpec 语言规则

- `openspec/specs/**/spec.md` 与 `openspec/changes/**/specs/**/spec.md` 中的业务能力标题、需求说明、场景名称和验收描述 MUST 使用中文。
- OpenSpec 解析关键字 MAY 保留英文，例如 `Requirement`、`Scenario`、`MUST`、`SHALL`、`WHEN`、`THEN`、`AND`，以保证 CLI 校验稳定。
- API 路径、HTTP 方法、数据库表名、字段名、枚举值、代码类名、文件路径、命令、产品英文专名（如 客户端生成、Mintlify、Docker、Swagger）MAY 保留英文。
- 归档后生成的 `Purpose` 不得保留 `TBD - created by archiving...` 等脚手架占位文案；应改为中文能力说明。
- `/req-opsx` 与 `/bug-opsx` 使用 OpenSpec CLI `instructions` 或 template 时，proposal、design、tasks 的章节标题 MUST 按项目中文语义落盘；`Why`、`What Changes`、`Capabilities`、`Impact`、`Context`、`Goals`、`Implementation`、`Testing`、`Documentation` 等英文脚手架标题只可作为生成参考，不得保留在最终 Change 文档标题中。

## 生成文档中文业务标题

所有生成Markdown（含capture、trace、user-stories、review、requirement、bug、business-flow、acceptance、root-cause、workaround、proposal、design、tasks、spec及其他产物）必须有非空中文Frontmatter title与一致的唯一一级标题。业务主文档表达业务目标，辅助文档结合业务主题和用途，不能只有ID或文档类别。注册表每条必须有中文业务title，随Issue主文档业务标题同步。保留OpenSpec解析关键字。

生成完成前运行 `python scripts/validate-document-titles.py` 并传入本次产物路径或 `--bug`、`--req`、`--change`；失败先修正，不声明生成完成、不推进状态。历史无关文件不批量重写，读取端按阶段回退；产品Agent产物在应用前执行同一校验。

## 产品经理视角沟通

适用于所有 Agent 面向用户的进度汇报、问题说明、方案比较、交互卡片、验收结果和最终交付说明。

- 先讲业务结果和用户影响，再补充支撑判断所必需的技术细节。简短状态无需机械扩展成完整报告。
- 优先日常语言，不堆砌缩写、英文或中文技术术语；能直接表达含义时不额外引入术语。
- 必要技术术语随文解释：首次出现时用一句通俗说明解释含义，以及它与当前问题的关系；同一回复不重复解释，换话题或脱离原上下文时补充必要说明。
- 决策说明体验、成本、时间和风险，给出推荐理由。没有依据的成本或工期明确未知，不编造数字；不相关维度可以简短说明不适用。
- 保留真实完成状态、验证范围、失败、阻塞及不确定性，不用易懂措辞掩盖未验证结论。命令、路径、标识符、机器字段保持原样，解释放在旁边，不改写可执行内容。
- 面向开发者的代码、协议和机器输出保留准确表达；用户明确要求深入技术细节时可增加细节，仍解释首次出现的必要术语。

表达示例：将“缓存失效”解释为“保存后页面仍显示旧内容，需要及时更新”；将“幂等”解释为“重复提交也只产生一次实际结果”；将“回归通过”解释为“已检查受影响的原有功能仍正常”，并列明实际验证范围。

发送前检查：用户能否知道结果、影响、是否需要决策；术语是否必要且已解释；是否保留证据和限制。静态脚本仅检查规则和引用存在，不代表每次实际回复都已符合可理解性要求。

