# 第一阶段后端基础状态

本文档记录朱春雯负责的第一阶段后端 / 基础文档任务状态。范围仅覆盖后端接口、评分模型、安全边界和文档，不覆盖曹乐负责的前端页面交互。

## 任务状态

| 任务编号 | 状态 | 证据 |
| --- | --- | --- |
| B1-1 明确 Demo 功能范围 | 已完成 | `README.md`、`DEVELOPMENT_PLAN_AND_DELIVERABLES.md` 保留核心流程与可选历史记录说明；本状态文档明确第一阶段运行范围 |
| B1-2 设计接口字段草案 | 已完成 | `docs/backend-api-contract.md` 记录 `/health`、`/api/analyze` 已实现字段，并把 `/api/simulate`、`/api/review` 标为第二阶段字段草案 |
| B1-3 设计压力评分模型 | 已完成 | `docs/scoring-model.md` 记录规则分、权重、风险区间和典型夜间噪音案例 |
| B1-4 搭建 FastAPI 后端基础结构 | 已完成 | `backend/app/main.py` 提供 FastAPI 入口；`backend/app/schemas.py` 定义请求响应结构；`backend/app/scoring.py` 提供评分逻辑；`backend/app/safety.py` 提供安全提示 |
| B1-5 实现 `/api/analyze` 初版 | 已完成 | `backend/app/main.py` 暴露 `POST /api/analyze`；`backend/tests/test_api.py` 覆盖结构化响应和 76 分典型案例 |
| B1-6 整理策划文档基础内容 | 已完成 | `README.md`、`DEVELOPMENT_PLAN_AND_DELIVERABLES.md` 和 `docs/phase1-status.md` 记录第一阶段后端基础状态与边界 |

## 已实现后端文件

- `backend/app/main.py`：FastAPI 应用入口，已实现 `GET /health` 和 `POST /api/analyze`。
- `backend/app/schemas.py`：事件分析请求、响应和枚举字段。
- `backend/app/scoring.py`：第一阶段规则评分模型、风险等级、建议生成。
- `backend/app/safety.py`：非诊断性安全提示。
- `backend/requirements.txt`：后端依赖。

## 已有测试

- `backend/tests/test_api.py`：覆盖 `/health`、`/api/analyze` 结构化响应、严重程度越界校验。
- `backend/tests/test_scoring.py`：覆盖典型夜间噪音案例、低风险案例、描述字段清洗与校验。

## 第一阶段未实现内容

- `/api/simulate` 运行时接口未实现；当前只在接口契约中保留第二阶段字段草案。
- `/api/review` 运行时接口未实现；当前只在接口契约中保留第二阶段字段草案。
- LangChain / 大模型调用未接入；第一阶段 `/api/analyze` 使用规则评分模型。
- 历史记录存储与查询未实现。
- 完整产品 Demo 和前端行为不属于本次后端文档整理的完成范围。
