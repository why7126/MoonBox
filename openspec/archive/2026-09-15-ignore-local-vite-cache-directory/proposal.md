## 背景

根目录 `.vite/` 是 Vite 或前端测试工具可能生成的本地缓存目录，不属于 MoonBox 正式项目结构。当前目录结构校验把它识别为未登记根目录，导致治理门禁在存在本地缓存时失败。

## 变更内容

- 将根目录 `.vite/` 明确纳入 `.gitignore` 的本地缓存边界。
- 更新目录结构校验脚本，允许忽略根目录 `.vite/`。
- 更新目录结构规则和 OpenSpec delta spec，说明 `.vite/` 不是正式项目目录。
- 写入治理日志并同步 Sprint scope。

## 能力影响

### 新增能力

- 无。

### 修改能力

- `harness-runtime`: 目录结构校验允许被 Git 忽略的根目录 `.vite/` 本地缓存存在，不将其视为正式顶层目录。

## 影响范围

- 规则：`rules/directory-structure.md`。
- 脚本：`scripts/validate-directory-structure.py`。
- Git 边界：`.gitignore`。
- 文档：本 Change 与治理日志。
- API/DB/Web/管理端/客户端/Orval/Docker Compose：不适用，本变更仅调整本地目录治理和校验脚本。
