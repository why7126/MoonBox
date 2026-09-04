## MODIFIED Requirements

### Requirement: 设计系统校验

MoonBox SHALL 提供 `scripts/validate-design-system.py`，用于发现硬编码颜色、CSS `content` 原始非 ASCII 符号和绕过组件体系的原生控件使用。

#### Scenario: 校验通过

- **GIVEN** 源码遵守 Token、CSS 生成内容与组件使用规则
- **WHEN** 校验脚本运行
- **THEN** 脚本成功退出

#### Scenario: CSS content 非 ASCII 符号必须使用 escape 写法

- **WHEN** CSS 文件通过 `content` 属性生成分隔点、箭头、勾号或其他非 ASCII 符号
- **THEN** 非 ASCII 符号必须使用 CSS escape 写法，例如 `\00B7` 或 `\2713`
- **AND** 不得在 `content` 字符串中直接写入原始非 ASCII 符号
- **AND** ASCII 字符、空字符串、`attr()` 和 `counter()` 用法不得被误判为违规
