# 朱春雯第三阶段联调收尾设计

## 背景

仓库已完成第二阶段朱春雯负责的 FastAPI、规则评分、LangChain/OpenAI AI 接口、Prompt、安全边界和演示样例。第三阶段目标是完成前后端联调优化与开发收尾，跑通“事件记录 -> 压力分析 -> AI 沟通模拟 -> 沟通复盘报告”的核心 Demo，并整理联调、技术说明和限制说明。

本设计优先覆盖朱春雯负责的后端、接口、AI、安全边界、技术说明和策划文档。曹乐负责的页面 UI、响应式细节、页面截图、演示视频和宣传海报不作为本次主要修改对象。为了让现有 Vue 页面能在本地稳定调用后端，本次允许修改最小前端运行配置和静态校验脚本，不进入页面 UI 重构。

## 目标

- 确认 `/api/analyze`、`/api/simulate`、`/api/review` 可以被本地前端开发服务器稳定调用。
- 修复后端在第三阶段联调中暴露的字段兼容问题，避免复盘页因展示型 speaker 或旧事件字段被直接 `422` 阻断。
- 给 FastAPI 增加本地 Demo 可用的 CORS 配置，并支持环境变量覆盖。
- 给 Vite 开发服务器增加 `/api` 代理到后端，保证前端相对路径请求可达。
- 整理第三阶段联调记录、后端问题修复记录、技术说明、最终策划文档状态和开发限制说明。

## 非目标

- 不制作第 7 天演示视频、宣传海报或线上提交材料包。
- 不重做曹乐负责的页面 UI、布局、截图和演示路径说明。
- 不实现历史记录持久化、用户账号、数据库或真实隐私数据采集。
- 不在缺少 `OPENAI_API_KEY` 时伪造 AI 成功结果；AI 接口仍返回清晰的 `503`。
- 不提交或发布远程分支，最终发布由用户手动完成。

## 方案选择

推荐采用“后端兼容 + 本地代理 + 文档收尾”的最小联调方案。

- 后端兼容：保留公开契约中的标准字段，同时接收当前前端可能发送的旧字段别名和展示型 speaker 文案，并在 Pydantic 层归一化。
- 本地代理：前端继续使用 `/api/*` 相对路径，Vite 在开发环境转发到 `http://127.0.0.1:8000`。
- 文档收尾：用独立 `docs/phase3-status.md` 记录第三阶段证据，并同步 README、开发计划和策划文档，避免把计划描述成未验证事实。

不推荐直接把前端请求改成硬编码后端绝对地址，因为会让部署环境和本地开发配置混在页面代码里。也不推荐放宽后端到接受任意字段，因为复盘接口的 `original_event` 仍需要保持受控摘要，避免把无限制浏览器状态传给 Prompt。

## 架构与数据流

本地联调时，浏览器访问 Vite 前端：

```text
Vue dev server
  -> /api/analyze | /api/simulate | /api/review
  -> Vite proxy http://127.0.0.1:8000
  -> FastAPI
  -> scoring / LangChain AI service
```

跨源访问后端时，FastAPI CORS 默认允许 `http://localhost:5173` 与 `http://127.0.0.1:5173`。如演示端口变化，可通过 `DORM_HARMONY_CORS_ORIGINS` 使用逗号分隔列表覆盖。

复盘请求兼容规则：

- `DialogueMessage.speaker` 标准值仍为 `user`、`roommate_a`、`roommate_b`、`roommate_c`、`system`。
- 后端兼容 `你`、`用户`、`舍友 A`、`舍友 A（直接型）` 等展示文案，并归一化为标准 speaker。
- `ReviewOriginalEvent.event_type` 标准值仍为 `noise`、`schedule`、`hygiene`、`cost`、`privacy`、`emotion`。
- 后端兼容前端旧值 `noise_conflict`、`schedule_conflict`、`hygiene_conflict`、`expense_conflict`、`privacy_boundary`、`emotional_conflict`。
- 分析页兜底产生的 `risk-high` 这类展示性 event_type 不进入 AI 原始事件摘要，归一化为 `None`。

## 错误处理

- 请求字段非法仍返回 `422`，但当前前端联调中已知的旧字段别名不再被视为非法。
- 缺少 `OPENAI_API_KEY` 时 `/api/simulate` 和 `/api/review` 返回 `503`，前端可展示演示兜底。
- LangChain/OpenAI 调用失败返回 `502`，错误信息不得暴露密钥、堆栈或第三方原始异常。
- CORS 只解决浏览器跨源调用，不改变 AI 服务配置或鉴权边界。

## 测试策略

遵循 TDD：

1. 先写后端失败测试，覆盖本地 CORS preflight、复盘展示型 speaker payload、旧 event_type payload。
2. 先写前端静态失败校验，覆盖 Vite `/api` 代理配置和 phase3 校验脚本入口。
3. 实现最小代码让测试通过。
4. 运行后端 pytest、前端 phase2/phase3 静态校验。
5. 如本地没有 `frontend/node_modules`，记录无法运行完整 Vue build 的事实，不把 build 描述为已通过。

## 文档更新

- 新增 `docs/phase3-status.md`：记录 B3-1 到 B3-5 状态、联调结论、修复记录、技术说明和限制说明。
- 更新 `README.md`：当前状态推进到第三阶段后端联调收尾，补充本地前后端启动方式和 CORS 配置。
- 更新 `docs/backend-api-contract.md`：记录 CORS、Vite 代理和兼容字段。
- 更新 `DEVELOPMENT_PLAN_AND_DELIVERABLES.md`：补充第三阶段朱春雯任务的当前状态证据。
- 更新 `docs/sheyou-xinqing-planning.md`：把最终策划文档中的开发状态与限制对齐到当前实现。

## 验收标准

- 当前分支不是 `main`。
- 后端测试覆盖第三阶段联调修复，并全部通过。
- 前端静态校验确认 Vite 代理与第三阶段联调入口存在。
- `docs/phase3-status.md` 能直接说明 B3-1 到 B3-5 的交付证据和剩余限制。
- README 和后端契约中的启动、配置、接口状态与当前实现一致。
- 不推送、不合并，由用户手动发布分支。
