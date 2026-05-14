# 第三阶段联调优化与开发收尾状态

本文档记录朱春雯负责的第三阶段后端、接口、AI、技术说明、策划文档和开发限制收尾情况。曹乐负责的前端 UI、响应式优化、页面截图、演示视频和宣传海报不在本文档完成范围内。

## 范围边界

本阶段朱春雯负责：

- `B3-1` 接口联调结果记录
- `B3-2` 后端问题修复记录
- `B3-3` 技术说明
- `B3-4` 最终策划文档一致性整理
- `B3-5` 开发限制说明

完整网页 Demo 是共同任务。当前仓库已完成朱春雯侧的后端联调准备与接口兼容修复；真实浏览器完整演示仍依赖前端页面运行、前端依赖安装、后端服务启动，以及 AI 接口的 `DEEPSEEK_API_KEY`。

## 当前状态

| 任务编号 | 当前状态 | 证据 |
| --- | --- | --- |
| B3-1 完成接口联调 | 已完成朱春雯侧静态联调准备；真实浏览器/API smoke 未验证 | `frontend/vite.config.ts` 已配置 `/api` 代理到 `http://127.0.0.1:8000`；`backend/app/main.py` 已允许本地 Vite origin；`frontend/scripts/verify-phase3.mjs` 校验三个前端相对路径和代理配置 |
| B3-2 修复后端问题 | 已完成本轮后端兼容修复 | `backend/app/schemas.py` 兼容当前前端复盘页展示型 speaker 与旧事件类型；`backend/tests/test_api.py` 覆盖 CORS、复盘 payload 兼容、extra 字段拒绝和风险别名收窄 |
| B3-3 整理技术说明 | 已完成 | 本文档、`README.md`、`docs/backend-api-contract.md`、`docs/scoring-model.md` 和 `docs/phase2-status.md` 已串联 FastAPI、评分模型、LangChain Prompt、AI 服务、安全边界和未实现存储 |
| B3-4 完善最终策划文档 | 已完成当前实现校准 | `docs/sheyou-xinqing-planning.md` 已补充当前实现与后续拓展边界，避免把历史记录存储描述为已落地 |
| B3-5 整理开发限制说明 | 已完成 | 本文档集中记录 Demo 数据范围、AI 输出依赖、未实现功能和验证限制 |

## 接口联调结果

| 接口 | 当前结论 | 说明 |
| --- | --- | --- |
| `GET /health` | 后端可用性接口已实现 | 用于确认 FastAPI 服务启动状态 |
| `POST /api/analyze` | 前端相对路径与后端契约已完成静态联调准备 | 前端通过 `/api/analyze` 提交，Vite 可代理到后端；后端返回结构化压力分析 |
| `POST /api/simulate` | 本地路径与字段契约已准备好 | 有 `DEEPSEEK_API_KEY` 时调用 LangChain/DeepSeek；无 Key 时按契约返回 `503`，前端可展示演示兜底 |
| `POST /api/review` | 本轮已修复已知字段不一致 | 后端兼容当前前端展示型 speaker 和旧事件类型，同时继续拒绝未授权 extra 字段 |

## 后端问题修复记录

| 问题 | 修复方式 | 验证 |
| --- | --- | --- |
| Vite 前端使用 `/api/*` 相对路径，但本地开发时无法直接到 FastAPI | `frontend/vite.config.ts` 增加 `/api` dev proxy；`backend/app/main.py` 增加本地 CORS origin | `node scripts/verify-phase3.mjs`；`backend/tests/test_api.py` CORS preflight 用例 |
| 复盘页可能发送 `你`、`舍友 A（直接型）` 等展示型 speaker | `DialogueMessage` 在校验前归一化为 `user`、`roommate_a`、`roommate_b`、`roommate_c`、`system` | 捕获型 fake service 测试断言 AI service 收到标准 speaker |
| 复盘页可能发送 `noise_conflict`、`privacy_boundary` 等旧事件类型 | `ReviewOriginalEvent.event_type` 在校验前归一化为后端标准事件类型 | 接口测试覆盖 `expense_conflict`、`privacy_boundary`、`emotional_conflict` |
| 分析页派生的 `risk-high` 不应作为真实事件类型传给 AI | 仅允许 `risk-stable`、`risk-pressure`、`risk-high`、`risk-severe` 归一为 `None`；其他 `risk-*` 仍返回 `422` | 接口测试覆盖 `risk-high` 通过配置检查、`risk-critical` 返回 `422` |
| 复盘请求不应吞掉未知浏览器状态 | `ReviewRequest`、`DialogueMessage`、`ReviewOriginalEvent` 均禁止 extra 字段 | 接口测试覆盖顶层 extra 和 dialogue extra 返回 `422` |

## 技术说明

- FastAPI 入口在 `backend/app/main.py`，提供 `GET /health`、`POST /api/analyze`、`POST /api/simulate` 和 `POST /api/review`。
- 压力评分模型在 `backend/app/scoring.py`，按严重程度、发生频率、情绪、沟通状态和冲突升级情况计算 0-100 压力值。
- AI Prompt 在 `backend/app/ai_prompts.py`，限定大学宿舍沟通场景、固定三类舍友角色，并约束非诊断性输出。
- AI 服务在 `backend/app/ai_service.py`，通过 LangChain/DeepSeek 结构化输出；缺少 `DEEPSEEK_API_KEY` 且没有兼容的 `OPENAI_API_KEY` 时返回 `503`，AI 调用失败或结构异常返回 `502`。
- 当前没有实现历史记录持久化；SQLite / JSON 存储仍是后续拓展。
- 本地前端开发服务器通过 Vite `/api` 代理访问 `http://127.0.0.1:8000` 的 FastAPI。

## 开发限制说明

- AI 模拟和复盘依赖 `DEEPSEEK_API_KEY`。`OPENAI_API_KEY` 仅作为旧配置兼容 fallback；无 Key 时接口不会伪造成功结果。
- 当前演示数据只覆盖噪音冲突、卫生分工、隐私边界等典型宿舍场景，不代表真实用户数据采集。
- 项目不采集真实身份信息，不提供账号体系、数据库持久化、历史记录查询或管理后台。
- 本项目仅提供宿舍关系压力趋势提示和沟通训练建议，不进行心理疾病诊断、医学判断或人格评价。
- 页面截图、演示视频、宣传海报、响应式 UI 细节属于曹乐或第 7 天材料任务，不在本次后端收尾中完成。

## 验证记录

当前分支验证命令：

```bash
cd backend
python3 -m pytest
```

结果：`67 passed`。

```bash
cd frontend
node scripts/verify-phase2.mjs
node scripts/verify-phase3.mjs
```

结果：两个静态校验脚本均通过。

当前工作区未安装 `frontend/node_modules`，因此完整 Vue build 或浏览器端真实 smoke 需要先安装前端依赖后再执行。
