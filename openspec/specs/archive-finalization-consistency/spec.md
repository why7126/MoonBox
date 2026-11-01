# archive-finalization-consistency Specification

## Purpose
TBD - created by archiving change fix-archive-finalization-consistency. Update Purpose after archive.
## Requirements
### Requirement: 归档完成必须验证当前文档

系统 SHALL 在 CLI 完整归档与产品归档返回完成前验证关联普通引用及明确当前正文；目录移动和历史任务完成不能单独证明本次收尾成功。

#### Scenario: 旧路径或当前正文残留

- **WHEN** 目录已移动但相关文档存在失效导航或明确当前状态矛盾
- **THEN** 返回收尾阻断并保留现场，不返回完整归档成功

#### Scenario: 恢复和重放

- **WHEN** 从已移动、已同步或已完成操作恢复
- **THEN** 重新执行只读收尾验证，每次请求只验证一次，不重复合并

#### Scenario: 历史与部分交付

- **WHEN** 文档记录历史失败、示例路径或父需求部分交付
- **THEN** 保留原文，不据子 Change 归档自动将父需求判为 done；真实导航仍接受检查

#### Scenario: 非完整收尾

- **WHEN** CLI 未指定 finalize
- **THEN** 仅报告目录移动完成，不报告完整归档成功

### Requirement: 不改写历史的收尾恢复

系统 SHALL 仅在唯一归档、完整验收和原恢复证明有效时，通过排他追加的绑定记录恢复明确的初始proposal状态和已关闭来源Issue指向自身Change的旧导航；原文、规格和恢复日志保持不变。

#### Scenario: 有效恢复与重放
- **WHEN** 原文为proposal初始proposed状态或闭合来源Issue中自身Change旧路径，且所有证明有效
- **THEN** 预检只读，显式apply追加绑定记录，共享收尾检查采用验证后的投影；重复apply不覆盖记录

#### Scenario: 拒绝不受支持或变化的输入
- **WHEN** 验收失败、身份歧义、来源不闭合、路径逃逸、符号链接、内容或记录变化、非初始状态
- **THEN** 不豁免对应冲突，不修改历史或覆盖记录，不允许重新合并以伪造完成

### Requirement: 归档前声明的证明绑定恢复
系统 SHALL 仅在唯一完整归档及原验收恢复证明有效时，允许追加记录将trace验收结论中精确的“无正式归档授权，本次未归档”声明识别为历史；不修改原文。

#### Scenario: 受限恢复
- **WHEN** 来源已关闭、兄弟完成，且用户授权恢复
- **THEN** 记录绑定全文、原证明与完整验收，收尾仅消除此句冲突

#### Scenario: 保留真实阻塞
- **WHEN** 同段还有失败状态、证据变化或原文变化
- **THEN** 校验继续阻断，不把整个段落豁免

### Requirement: 提案历史问题引用恢复
系统 SHALL 在原完整归档证明有效时，允许追加记录识别proposal背景中固定语法的归档前声明引用，保留原文并绑定全文哈希及段落行号。

#### Scenario: 明确的旧问题引用
- **WHEN** 背景句以REQ或BUG编号说明归档同步后的验收声明被检查器误判，引用为受支持的归档前声明，且用户授权恢复
- **THEN** 只将该完整句子识别为历史，恢复记录无变化时重复执行保持幂等

#### Scenario: 真实冲突及变化
- **WHEN** 引用句含额外状态断言、相邻句存在冲突、章节不符或绑定发生变化
- **THEN** 保留相应阻断，不豁免整个段落或未知句式

### Requirement: 已关闭缺陷索引追加证明
系统 SHALL 保留原恢复证明与当前来源追溯，通过独立补证验证仅追加已关闭缺陷索引和更新时间的变化。

#### Scenario: 合法追加
- **WHEN** 原文哈希匹配原证明且新增缺陷均已归档并反向关联来源
- **THEN** 完整复核其他绑定后允许收尾

#### Scenario: 非法漂移
- **WHEN** 正文、证明、验收、归属或补证存在未知变化
- **THEN** 阻断收尾且保留全部原件

