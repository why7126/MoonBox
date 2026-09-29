## MODIFIED Requirements

### Requirement: 独立变更阶段按钮

系统 SHALL 复用REQ/BUG的阶段按钮、弹窗族、权限与执行能力门禁。验收中独立 Change 的完成/归档入口 SHALL 检查 Change 内交付验证来源，但 SHALL NOT 固定要求 `acceptance.md` 或 `verification.md`；当存在非空 `trace.md` 验证类章节或有效 `trace.acceptance_refs` 时，系统 SHALL 接受其作为证据入口。

#### Scenario: 阶段匹配
- **WHEN** 独立Change位于待开发、研发中或验收中
- **THEN** 系统 SHALL 分别提供开始开发、查看进度、受验收门禁控制的完成/归档入口
- **AND** 已完成及未知状态 SHALL 不显示阶段主按钮

#### Scenario: 能力与权限
- **WHEN** 用户触发阶段动作
- **THEN** 写动作 SHALL 校验项目可写、对象权限、Sprint及前置证据，不得因独立Change类型固定禁用，真实能力反馈与同阶段REQ/BUG一致
- **AND** 查看进度 SHALL 仅要求读取权限，缺tasks提示缺失；不得伪造REQ身份或执行结果
- **AND** Demo SHALL 不调用真实写入，成功执行后 SHALL 刷新稳定快照

#### Scenario: 原型验收
- **WHEN** 完成按钮增补
- **THEN** 系统 SHALL 以design、acceptance、新增1440px及关键交互截图、computed style、Mock/API声明和REQ一致性共同验收；原型仅为设计输入

#### Scenario: 无固定禁用提示
- **WHEN** 独立Change满足现有阶段文档及权限门禁
- **THEN** 系统 SHALL 不添加固定验收核对提示，使用REQ/BUG相同的动作处理器与testProgress/manualAcceptanceCount门禁
- **AND** 真实模式尚未支持的动作 SHALL 给出相同能力反馈，不执行虚假流转

#### Scenario: 接受 Change 内非固定验证来源

- **WHEN** 独立 Change 处于验收中且没有 `acceptance.md` 或 `verification.md`
- **THEN** 系统 SHALL 查找 `trace.acceptance_refs` 指向的 Change 内 Markdown
- **AND** 未声明显式引用时，系统 SHALL 查找 `trace.md` 中非空的验证类章节
- **AND** 找到有效来源时 SHALL 不展示“未找到交付验证记录”
- **AND** 未找到任一来源时 SHALL 提示验收来源待核实

#### Scenario: 独立变更从追溯正文读取中文标题

- **WHEN** trace显式标题与proposal/design业务标题均缺失，但trace正文存在有效中文一级业务标题
- **THEN** 卡片必须使用该业务标题，保留完整Change ID身份行
- **AND** 追溯、背景与动机、验证记录等通用章节名不得作为业务标题；无有效标题时回退完整Change ID
