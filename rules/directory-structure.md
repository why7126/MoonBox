---
purpose: 目录结构规范
content: 约束 AI 与开发人员遵循当前项目目录边界、文件归属和新增文件规则
update_method: 目录结构调整时由架构负责人确认后更新；AI 只能提出建议，不得擅自放宽规则
created_at: 2026-06-13 00:00:00
updated_at: 2026-08-07 00:00:00
note: AGENTS.md 必须引用本文档；用于防止 AI 随意新增目录或把文件放错位置
---

# 目录结构规范

## 1. 目标

本文档用于约束 AI Agent 和开发人员在 `MoonBox` 中遵循统一目录结构，避免后端、前端、文档、测试、部署和治理文件混放。

新增顶层目录、移动目录边界或改变治理流程时，必须先创建 OpenSpec Change，并同步更新本文件、`rules/document-governance.md`、README、模板资产和相关校验脚本。

## 2. 顶层目录职责

| 目录 | 职责 | 是否允许随意新增同级目录 |
|---|---|---|
| `rules/` | 强制研发规范 | 否 |
| `docs/` | 长期产品与技术文档 | 否 |
| `openspec/` | OpenSpec 需求与规格事实源 | 否 |
| `issues/` | 原始需求和 BUG 池 | 否 |
| `iterations/` | Sprint / 迭代管理 | 否 |
| `releases/` | 产品版本发布对象、公开公告源文件、发布校验材料和公告站点配置 | 否 |
| `mintlify/` | 公开产品手册站点源目录、版本化手册投影、截图资产和 Mintlify 配置 | 否 |
| `compatibility/` | 兼容性矩阵与适配说明 | 否 |
| `.agents/` | Agent 技能与命令唯一入口 | 否 |
| `src/` | 源码 | 否 |
| `tests/` | 测试 | 否 |
| `scripts/` | 自动化脚本 | 否 |
| `data/` | 本地开发、演示、测试样例和运行时数据承载 | 是，仅本地环境 |
| `design-schemes/` | 可复用 UI/UE、导航栏和 HTML Demo 设计资产库 | 否 |
| `models/` | 模型说明和校验信息；不得提交大模型权重 | 否 |
| `deploy/` | 部署编排与发布脚本 | 否 |

## 3. `releases/` 产品发布目录

`releases/` 用于承载产品版本发布对象与公开发布公告源文件，表达一次对外产品版本发布，可汇总一个或多个 Sprint 的 REQ、BUG 与 OpenSpec Change。

推荐结构：

```text
releases/
├── README.md
├── mint.json
├── templates/
│   ├── release.json
│   └── announcement.mdx
└── v0.1.0/
    ├── release.json
    └── announcement.mdx
```

边界：

- `releases/` MUST 只存放产品版本发布对象、公开公告源文件、发布校验记录和静态公告站点配置。
- `releases/` MUST NOT 替代 `iterations/` 四件套、`issues/` 需求/BUG 文档、`openspec/changes/` 变更事实源或 `docs/` 长期技术文档。
- `releases/` MUST NOT 存放运行时生成站点、构建产物、真实客户数据、密钥、数据库连接串、对象存储凭据或不可公开运维信息。
- 若静态站点生成输出目录存在，MUST 在 `.gitignore` 或相邻 README 中声明提交边界。

生命周期：

1. `/release-propose <version>` 创建或更新产品版本发布对象。
2. `/release-prepare <version>` 执行发布前校验并生成或更新公告源文件。
3. `/release-publish <version>` 记录发布确认结果和最终公告位置。

命名：

- 版本目录 SHOULD 使用 SemVer 风格，例如 `v0.1.0/`。
- 公告发布时间字段 MUST 使用 `YYYY-MM-DD HH:mm:ss`。

## 4. `design-schemes/` 设计资产库

`design-schemes/` 用于沉淀可跨项目复用的 UI/UE、导航栏和视觉预览资产，服务于新项目初始化和存量项目重构。

推荐结构：

```text
design-schemes/
├── README.md
├── registry.json
└── schemes/
    └── {scheme-id}/
        ├── meta.json
        ├── design.json
        ├── navigation.json
        ├── demo.html
        └── navigation-demo.html
```

边界：

- `design.json` MUST 作为整体 UI/UE 事实源，记录颜色、字体、间距、组件、布局、响应式和交互规则。
- `navigation.json` MUST 作为导航栏事实源，记录导航类型、菜单分组、状态、权限、折叠和移动端行为。
- `demo.html` 与 `navigation-demo.html` MUST 是可直接打开的静态预览文件，用于让用户快速判断方案效果。
- `design-schemes/` MUST NOT 存放具体业务页面需求、运行时截图缓存、构建产物、真实客户数据、账号、密钥或接口凭据。
- 从来源项目抽取但尚未核对的资产 MUST 标记 `inferred: true`；基于源码、设计稿或截图核实后才可标记为 `inferred: false`。

## 5. `mintlify/` 产品手册目录

`mintlify/` 用于承载可公开部署的产品手册源文件、版本化手册投影、公开发布公告投影和截图资产。

推荐结构：

```text
mintlify/
├── README.md
├── mint.json
├── site-manifest.json
├── docs/
│   └── latest/
│       ├── overview.mdx
│       ├── admin.mdx
│       ├── deployment.mdx
│       └── faq.mdx
├── releases/
└── assets/
    └── screenshots/
```

边界：

- `mintlify/` MUST 只存放公开产品手册源文件、Mintlify 配置、可公开截图资产和发布公告投影。
- `mintlify/` MUST NOT 替代 `docs/` 长期技术文档、`releases/` 发布事实源、`iterations/`、`issues/` 或 `openspec/`。
- `mintlify/` MUST NOT 存放构建产物、真实客户数据、密钥、数据库连接串、真实 `.env`、Authorization header、Cookie、运行时数据库或不可公开运维信息。
- 产品手册生成后 MUST 运行 `python scripts/validate-mintlify-docs.py`。
- 本地和生产 Docker Compose 可通过 `docs-site` profile 挂载 `mintlify/` 作为产品手册预览或承载源。

## 6. 源码归属规则

后端代码推荐放在：

```text
src/backend/app/
├── api/
├── core/
├── db/
├── models/
├── repositories/
├── schemas/
├── services/
└── main.py
```

Web 前端代码推荐放在：

```text
src/web/src/
├── app/
├── pages/
├── features/
├── components/
├── services/
├── generated/      # 客户端生成代码，不允许手工修改
└── styles/
```

其他端按需使用：

```text
src/wechat-miniapp/
src/android/
src/ios/
src/desktop/
src/algorithm/
src/shared/
src/sdk/
src/infrastructure/
```

禁止把后端、前端或业务代码放到 `scripts/`、`docs/`、`tests/` 或项目根目录。共享类型、常量、错误码、SDK 应放在 `src/shared/` 或 `src/sdk/`，不得复制到多个端。

## 7. 文档归属规则

- 主文档与总索引放入 `docs/`。
- 可复用设计资产说明放入 `design-schemes/README.md` 和各方案目录 README；单个需求页面原型仍放入 `issues/requirements/{plan|review|archive}/REQ-*/prototype/`。
- API、测试等治理细则放入 `docs/standards/`。
- 规范工程日志统一放入 `docs/spec-logs/`：`/spec-study` 学习报告使用 `YYYYMMDDhhmmss-study-xxx.md`，`/spec-opt` 本项目规范、技能、脚本、目录边界或校验规则迭代日志使用 `YYYYMMDDhhmmss-governance-xxx.md`；该目录不替代 `docs/standards/`、`docs/knowledge-base/`、`openspec/changes/`、`iterations/`、`releases/` 或 `deploy/`，且不得包含用户隐私数据、真实客户数据、密钥、访问令牌、未脱敏日志、学习对象源码、截图中的个人信息、本机绝对路径、系统用户名或用户主目录。
- 产品需求放入 `issues/requirements/{plan|review|archive}/REQ-*`；禁止 `docs/prd/`。
- BUG 分析放入 `issues/bugs/{plan|review|archive}/BUG-*`；禁止 `docs/bugs/`。
- 故障、复盘、最佳实践放入 `docs/knowledge-base/`。
- 迭代文档放入 `iterations/{change|archive}/sprint-xxx/`。
- 产品版本发布对象、公告源文件和发布校验记录放入 `releases/`。
- 公开产品手册源文件、版本化手册投影和站点配置放入 `mintlify/`。
- 正式系统能力放入 `openspec/specs/`。
- 开发中的变更放入 `openspec/changes/`；已完成变更放入 `openspec/archive/`。
- 禁止新增 `openspec/changes/archive/`。该路径是旧技能模板残留，目录结构校验会阻断。

## 8. Docker 与部署文件

- 根目录只保留项目级编排文件，例如 `docker-compose.yml` 与按需启用的 `docker-compose.prod*.yml`。
- 后端镜像构建文件放入 `src/backend/Dockerfile`。
- Web 镜像构建文件放入 `src/web/Dockerfile`。
- Web Nginx 配置放入 `src/web/nginx.conf`。
- 部署脚本放入 `scripts/` 或 `deploy/`，并在 README / 部署文档中说明。
- `deploy/local/` 维护本地六模式矩阵；`deploy/prod/` 维护生产 Compose 入口；`deploy/scripts/` 维护环境校验、启动/停止和产品手册静态预览脚本。
- Sprint / OpenSpec 归档证据、readiness、stale scan、Fact Sheet 等治理脚本放入 `scripts/`，并由 `.agents/skills/opsx-archive`、`.agents/skills/sprint-archive`、`.agents/skills/sprint-exps` 引用。

## 9. AI 新增文件前检查清单

```text
□ 是否已有 OpenSpec Change？
□ 新文件是否属于已有目录职责？
□ 是否需要更新 rules/directory-structure.md？
□ 是否需要更新 AGENTS.md 的目录说明？
□ 是否需要更新 README.md？
□ 是否需要补充测试？
□ 是否需要同步客户端生成代码？
```

## 10. 禁止事项

- 禁止在根目录新增业务代码文件。
- 禁止将测试代码放入源码目录外的临时目录。
- 禁止手工修改客户端生成代码。
- 禁止在未更新 OpenSpec 的情况下新增业务能力。
- 禁止把 Docker 环境变量硬编码到代码中。
- 禁止用临时目录替代正式目录结构。
- 禁止新增或恢复 `.claude/`、`.codex/`、`.cursor/`、`.kiro/`、`.opencode/` 等兼容 Agent 工具目录。
