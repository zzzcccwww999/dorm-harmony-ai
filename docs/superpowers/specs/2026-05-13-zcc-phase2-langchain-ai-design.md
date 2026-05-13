# 朱春雯第二阶段 LangChain AI 后端设计

## 背景

本仓库第一阶段已完成 FastAPI 后端基础能力、`GET /health`、`POST /api/analyze`、规则评分模型和基础安全提示。第二阶段朱春雯负责后端、AI、评分模型、接口设计、安全边界和演示样例数据；曹乐负责前端页面、交互、UI、截图和演示材料。

本设计只覆盖朱春雯第二阶段后端 / AI 范围，不修改曹乐负责的 Vue 页面和第 7 天线上提交成品。

## 已确认决策

采用“真实 LangChain + OpenAI 结构化输出 + 缺少 API Key 明确失败”的方案。

- 后端必须真实接入 LangChain，而不是默认返回模板数据。
- `OPENAI_API_KEY` 只从环境变量读取，不写入仓库。
- 可选 `DORM_HARMONY_LLM_MODEL` 控制模型名。
- 缺少 `OPENAI_API_KEY` 时，AI 接口返回 `503 Service Unavailable`，提示需要配置 API Key。
- 测试使用可注入 fake LLM，不依赖真实外网和真实 API Key。

## 目标

完成朱春雯第二阶段 B2-1 到 B2-6 中属于后端 / AI 的可验收能力：

- 保持 `/api/analyze` 不同输入返回不同压力值和风险等级，并补充第二阶段状态说明。
- 设计多角色 Prompt，固定舍友 A 直接型、舍友 B 回避型、舍友 C 调和型。
- 实现 `POST /api/simulate`，真实调用 LangChain / OpenAI，返回结构化多角色回复。
- 实现 `POST /api/review`，真实调用 LangChain / OpenAI，返回结构化复盘报告。
- 输出安全边界提示，不生成心理诊断、人格评价或攻击性建议。
- 准备至少 3 个演示场景数据，覆盖噪音冲突、卫生分工、隐私边界。

## 非目标

- 不实现曹乐负责的前端页面、聊天气泡、报告页面、接口对接和截图素材。
- 不提前制作第 7 天演示视频、宣传海报或线上提交包。
- 不实现历史记录存储。
- 不把 API Key 或真实用户隐私写入代码、测试或文档。
- 不在缺少 API Key 时伪装成真实 AI 成功返回。

## 架构

后端保持当前 FastAPI 结构，并新增 AI 相关模块：

- `backend/app/schemas.py`：新增 simulate / review 请求响应模型。
- `backend/app/ai_prompts.py`：集中存放多角色模拟和沟通复盘 Prompt。
- `backend/app/ai_service.py`：封装 LangChain 调用、配置读取、结构化输出解析和错误映射。
- `backend/app/demo_data.py`：提供第二阶段演示样例数据。
- `backend/app/main.py`：新增 `/api/simulate` 和 `/api/review` 路由。
- `backend/tests/`：新增接口、AI 服务、演示数据和安全边界测试。

接口层不直接构造 LLM。它调用 AI 服务层，AI 服务层通过可注入的 runner 执行 LangChain 调用。生产环境 runner 使用 `langchain_openai.ChatOpenAI`；测试环境用 fake runner 返回固定 Pydantic 对象或抛出异常。

## 配置

运行时使用以下环境变量：

| 变量 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | 是 | 无 | OpenAI API Key，由 `langchain_openai.ChatOpenAI` 读取 |
| `DORM_HARMONY_LLM_MODEL` | 否 | `gpt-4o-mini` | OpenAI 模型名，需支持结构化输出 |
| `DORM_HARMONY_LLM_TIMEOUT` | 否 | `20` | LLM 请求超时时间，单位秒 |

README 和后端契约需要说明这些变量，但不得包含真实 Key。

## 接口设计

### POST /api/simulate

请求字段：

- `scenario`: 宿舍沟通场景，trim 后不能为空，最长 300 字符。
- `user_message`: 用户准备表达的话术，trim 后不能为空，最长 500 字符。
- `risk_level`: 可选，来自 `/api/analyze` 的风险等级。
- `context`: 可选补充背景，trim 后为空时按 `None` 处理，最长 500 字符。

响应字段：

- `replies`: 固定 3 条，分别为舍友 A、舍友 B、舍友 C。
- `safety_note`: 非诊断性安全提示。

每条回复包含：

- `roommate`: `舍友 A`、`舍友 B`、`舍友 C`。
- `personality`: `直接型`、`回避型`、`调和型`。
- `message`: 适合宿舍沟通演练的中文回复。

### POST /api/review

请求字段：

- `scenario`: 沟通场景，trim 后不能为空，最长 300 字符。
- `dialogue`: 至少 1 条对话记录。
- `original_event`: 可选原始事件摘要。

对话记录包含：

- `speaker`: `user`、`roommate_a`、`roommate_b`、`roommate_c`、`system`。
- `message`: 对话内容，trim 后不能为空，最长 500 字符。

响应字段：

- `summary`: 表达总结。
- `strengths`: 表达优点，至少 1 条。
- `risks`: 潜在问题，至少 1 条。
- `rewritten_message`: 优化后的沟通话术。
- `next_steps`: 后续行动建议，至少 1 条。
- `safety_note`: 非诊断性安全提示。

## Prompt 设计

系统 Prompt 统一包含安全边界：

- 只处理大学宿舍关系沟通场景。
- 不进行心理疾病诊断、医学判断或人格评价。
- 不输出攻击、威胁、羞辱、操控或报复性建议。
- 当用户内容包含高压力、暴力风险、严重失眠或现实安全风险时，提示寻求辅导员、心理老师、家人或可信任同学等现实支持。
- 输出必须符合接口结构，语言温和、具体、可执行。

`/api/simulate` Prompt 固定三位舍友角色：

- 舍友 A：直接型，容易反驳，但不得攻击或羞辱用户。
- 舍友 B：回避型，不愿正面沟通，但不得完全无意义。
- 舍友 C：调和型，愿意缓和关系并提出可执行规则。

`/api/review` Prompt 从对话中分析用户表达方式，输出优点、风险、优化话术和后续行动建议。

## LangChain 调用

生产实现使用 `langchain_openai.ChatOpenAI`：

- `model` 来自 `DORM_HARMONY_LLM_MODEL`，默认 `gpt-4o-mini`。
- `temperature=0.3`，降低演示输出波动。
- `timeout` 来自 `DORM_HARMONY_LLM_TIMEOUT`。
- `max_retries=1`，避免演示请求长时间卡住。
- 使用 `with_structured_output(...)` 解析为 Pydantic 响应模型。

如果结构化解析失败、OpenAI 返回错误、LangChain 抛出异常或 key 缺失，接口不返回伪造成功结果，而是返回可解释错误。

## 错误处理

| 场景 | HTTP 状态 | 响应语义 |
| --- | --- | --- |
| 请求字段非法 | `422` | FastAPI / Pydantic 默认校验错误 |
| 缺少 `OPENAI_API_KEY` | `503` | AI 服务未配置，需要设置环境变量 |
| LLM 调用失败 | `502` | AI 服务暂时不可用，请稍后重试 |
| LLM 输出不符合结构 | `502` | AI 输出结构异常，请稍后重试 |

错误信息不得回显 API Key、原始异常堆栈或敏感配置。

## 安全边界

新增 AI 接口必须复用统一安全提示，并在 Prompt 和响应中都体现非诊断边界。

安全提示必须包含：

- 仅用于宿舍沟通演练或沟通训练建议。
- 不代表真实舍友想法。
- 不进行心理诊断、医学判断或人格评价。
- 高压力、暴力风险、严重失眠等情况建议寻求现实支持。

测试要断言接口返回中包含非诊断性提示和现实支持建议。

## 演示样例数据

后端准备至少 3 个样例：

- 噪音冲突：舍友晚上打游戏声音较大，影响睡眠。
- 卫生分工：公共区域长期无人打扫，用户承担过多。
- 隐私边界：舍友未经允许使用个人物品。

样例数据应包含可直接用于 `/api/analyze`、`/api/simulate`、`/api/review` 的字段，便于后续前端或演示流程复用。

## 测试策略

必须遵循 TDD：

1. 先写失败测试，再实现运行时代码。
2. 新增接口测试覆盖成功结构、缺少 key 的 `503`、非法输入的 `422`。
3. AI 服务测试使用 fake runner，覆盖 LangChain 成功、缺 key、调用失败和结构异常。
4. Prompt / 安全边界测试用字符串断言，确认禁止诊断、人格评价和攻击性建议。
5. 演示数据测试确认至少 3 个场景、字段可用于接口请求。
6. 保留现有 `/api/analyze` 和评分测试，补充第二阶段回归测试确认不同输入得到不同风险等级。

基础验证命令：

```bash
cd backend
python3 -m pytest -p no:cacheprovider
```

如本地完整 API 测试因沙箱 `TestClient` 超时，至少要记录纯服务层测试结果和失败原因；不能把未运行的测试描述为通过。

## 文档更新

实现完成后需要更新：

- `README.md`：当前状态从第一阶段改为第二阶段后端 AI 能力，补充环境变量和运行说明。
- `docs/backend-api-contract.md`：把 `/api/simulate`、`/api/review` 从字段草案更新为已实现运行时接口。
- 新增 `docs/phase2-status.md`：记录第二阶段完成项和未覆盖项，避免把第一阶段状态文档改成混合状态。
- `DEVELOPMENT_PLAN_AND_DELIVERABLES.md`：标注朱春雯 B2-1 到 B2-6 的完成证据。

## 验收标准

- 当前分支不是 `main`，所有修改在 `feature/zcc-phase2-backend-ai` 上完成。
- `/api/analyze` 保持现有行为，并证明不同输入会产生不同压力值和风险等级。
- `/api/simulate` 和 `/api/review` 已注册 FastAPI 路由。
- 有 `OPENAI_API_KEY` 时，生产服务通过 LangChain 调用真实 OpenAI 模型。
- 无 `OPENAI_API_KEY` 时，AI 接口返回 `503`，不返回模板伪结果。
- 接口响应结构与后端契约一致，测试覆盖主要成功和失败路径。
- 文档清楚区分当前第二阶段已实现能力、仍未实现的前端对接 / 第三阶段联调 / 第 7 天材料。
