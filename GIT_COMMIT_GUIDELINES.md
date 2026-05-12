# Git Commit 提交信息规范

规范的 Git Commit 提交信息可以让团队更快理解每次代码变更的目的、范围和影响，方便代码审查、问题追溯和版本管理。

## 1. 提交格式

统一使用 Conventional Commits 风格：

```text
<type>(<scope>): <subject>
```

如果本次提交没有明确模块，可以省略 `scope`：

```text
<type>: <subject>
```

示例：

```text
feat(frontend): 新增事件记录页面
fix(api): 修复压力分析接口返回字段错误
docs: 更新项目策划文档
chore: 更新依赖配置
```

## 2. type 类型规范

| type | 含义 | 示例 |
| --- | --- | --- |
| `feat` | 新增功能 | `feat(ai): 新增多角色沟通模拟功能` |
| `fix` | 修复 Bug | `fix(frontend): 修复压力等级显示错误` |
| `docs` | 文档修改 | `docs: 更新 README 使用说明` |
| `style` | 代码格式或样式调整，不影响逻辑 | `style(ui): 调整聊天气泡间距` |
| `refactor` | 代码重构，不新增功能、不修 Bug | `refactor(backend): 拆分压力评分逻辑` |
| `perf` | 性能优化 | `perf(api): 优化历史记录查询速度` |
| `test` | 测试相关 | `test(api): 添加压力分析接口测试` |
| `chore` | 构建、依赖、配置等辅助修改 | `chore: 更新 package.json 依赖版本` |
| `build` | 构建或打包相关 | `build: 修改前端打包配置` |
| `revert` | 回滚提交 | `revert: 回滚 feat(ai): 新增微信登录` |

## 3. scope 范围建议

结合“舍友心晴”项目，推荐使用以下范围：

| scope | 对应范围 |
| --- | --- |
| `frontend` | Vue 前端整体功能 |
| `ui` | 页面样式、组件展示 |
| `backend` | FastAPI 后端逻辑 |
| `api` | 接口请求与响应 |
| `scoring` | 压力评分模型 |
| `ai` | LangChain、大模型、Prompt |
| `db` | SQLite / JSON 存储 |
| `safety` | 心理安全边界、免责声明 |
| `docs` | 文档、PPT、策划材料 |
| `demo` | 演示数据、演示脚本 |

## 4. subject 描述要求

- 简洁说明本次提交做了什么。
- 建议不超过 50 个字符。
- 使用清晰的动宾结构，例如“新增”“修复”“优化”“更新”“调整”。
- 不要写模糊、随意、无法追溯的提交信息。

不推荐：

```text
fix bug
update
test
再改改
了定搞
```

推荐：

```text
fix(api): 修复压力分析接口空数据报错
feat(frontend): 新增沟通复盘报告页面
docs(demo): 补充答辩演示流程
```

## 5. 本项目推荐提交示例

```text
feat(frontend): 新增首页和事件记录页
feat(scoring): 实现宿舍压力评分模型
feat(api): 新增 /api/analyze 分析接口
feat(ai): 新增多角色舍友回复生成逻辑
feat(frontend): 新增 AI 沟通模拟页面
fix(ui): 修复移动端按钮文字换行问题
docs: 更新作品策划文档
chore: 初始化前后端项目结构
```

## 6. 提交原则

- 一次提交只做一类事情。
- 前端、后端、AI、文档尽量分开提交。
- 提交信息要能说明变更目的，不要让审查者通过代码猜意图。
- 不要提交 `.env`、API Key、`node_modules`、`__pycache__`、`dist`、`build` 等无关或敏感文件。
- 回滚提交必须说明被回滚的提交信息和哈希值。

