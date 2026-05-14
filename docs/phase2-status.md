# 第二阶段后端 AI 状态

本文档记录第二阶段朱春雯负责的后端 AI 交付状态。

## 范围边界

本阶段覆盖朱春雯负责的后端/FastAPI/LangChain/Prompt/安全边界/演示样例/技术文档：

- FastAPI 后端接口：`GET /health`、`POST /api/analyze`、`POST /api/simulate`、`POST /api/review`
- LangChain/DeepSeek AI 服务层与结构化输出
- 多角色沟通模拟 Prompt、沟通复盘 Prompt 和安全边界
- 后端演示样例数据与技术文档状态记录

本阶段不覆盖曹乐负责的前端页面、UI、截图、演示视频、宣传海报，也不覆盖第三阶段完整 Demo 联调、历史记录存储与查询。

## 已完成任务

| 任务编号 | 当前状态 | 证据 |
| --- | --- | --- |
| B2-1 完善 `/api/analyze` 评分逻辑 | 已完成 | `backend/app/scoring.py` 按严重程度、频率、情绪、沟通状态、冲突状态计算压力值；`backend/tests/test_scoring.py` 覆盖低风险和高压力差异 |
| B2-2 设计多角色 Prompt | 已完成 | `backend/app/ai_prompts.py` 固定直接型、回避型、调和型舍友角色，并限制宿舍沟通、安全边界和结构化输出 |
| B2-3 实现 `/api/simulate` 接口 | 已完成 | `backend/app/main.py` 暴露 `POST /api/simulate`；`backend/app/ai_service.py` 通过 LangChain/DeepSeek 生成多角色结构化回复 |
| B2-4 实现 `/api/review` 接口 | 已完成 | `backend/app/main.py` 暴露 `POST /api/review`；`backend/app/ai_service.py` 通过 LangChain/DeepSeek 生成沟通复盘报告 |
| B2-5 添加心理安全边界 | 已完成 | `backend/app/ai_prompts.py` 和 `backend/app/ai_service.py` 要求非诊断性输出、避免人格评价，并保留现实支持建议 |
| B2-6 准备演示用样例数据 | 已完成 | `backend/app/demo_data.py` 覆盖噪音冲突、卫生分工、隐私边界 3 个场景 |

## 运行配置

第二阶段 AI 接口需要本地环境变量：

```bash
export DEEPSEEK_API_KEY="你的 DeepSeek API Key"
export DORM_HARMONY_LLM_BASE_URL="https://api.deepseek.com"
export DORM_HARMONY_LLM_MODEL="deepseek-v4-flash"
export DORM_HARMONY_LLM_TIMEOUT="20"
```

`DEEPSEEK_API_KEY` 不得提交到仓库。`OPENAI_API_KEY` 仅作为旧配置兼容 fallback。未配置任一 Key 时，`/api/simulate` 和 `/api/review` 返回 `503`，不会返回模板伪结果。LangChain/DeepSeek 调用失败或 AI 输出结构不符合契约时返回 `502`。DeepSeek 官方 V4 Flash 的 API 模型名是 `deepseek-v4-flash`。

## 未覆盖范围

- 曹乐负责的前端 AI 沟通模拟页面联调
- 第三阶段完整 Demo、页面截图和联调验收
- 第 7 天产品演示视频、宣传海报和线上提交材料
- 历史记录存储与查询
