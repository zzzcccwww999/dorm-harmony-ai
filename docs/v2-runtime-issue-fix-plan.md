# v2 版本运行问题修复实施计划

> **给后续 Codex/Agent 执行者：** 必须使用 `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans` 按任务逐项执行。所有步骤使用复选框（`- [ ]`）跟踪进度。

**目标：** 修复当前 v1 版本运行中的沟通模拟、事件档案、总压力分析、AI 心晴见解和事件日期问题，并把本次 v2 内的前后端交接职责写清楚，方便后续 Codex 直接按文档执行。

**架构：** 保留现有 FastAPI + Vue/Vite 单页架构，后端继续作为接口契约和规则评分的权威来源，前端负责页面体验、逐条展示和路由闭环。v2 新增轻量事件档案能力：事件记录写入后端本地 JSON store，分析报告基于档案内所有事件计算总压力，AI 心晴见解通过 LangChain/DeepSeek 单独接入；没有 API Key 时必须显示显式错误或“AI 未配置”，不能伪装成真实 AI 成功。

**技术栈：** Python 3.11+, FastAPI, Pydantic v2, pytest, LangChain/DeepSeek, Vue 3, Vue Router, TypeScript, Vite, 原生 `fetch`, 本地静态验证脚本。

---

## 范围与分工

以前制定并完成的三个阶段任务视为 **v1 版本完成基线**。本计划不是继续拆旧阶段任务，而是在 v1 已完成后制定 **v2 版本运行问题修复计划**，专门修复当前运行时暴露的五个问题。

本计划只覆盖用户列出的五类运行问题：

1. 沟通模拟不能持续对话。
2. 沟通模拟页面需要优化。
3. 三位舍友回复需要一条一条间隔出现。
4. 事件记录后可查看事件档案，压力分析基于所有事件计算总压力，主要压力来源由算法得出，AI 心晴见解接入真实 AI。
5. 事件记录增加日期字段。

v2 版本两位同学分工：

- **朱春雯负责后端与契约：** `backend/**`、`docs/backend-api-contract.md`、`docs/scoring-model.md`、`docs/v2-status.md` 中的接口、数据模型、JSON store、总压力公式、AI insight、后端测试和交接样例。
- **曹乐负责前端与页面：** `frontend/**` 中的事件记录日期字段、事件档案页、压力分析页改造、沟通模拟持续对话和逐条展示、页面样式优化、前端验证脚本和前端交接确认。

禁止事项：

- 不引入账号系统、云数据库、管理后台或线上部署流程。
- 不把前端演示兜底写成后端 AI 成功。
- 不把 `/api/analyze` 改成不可解释的大模型评分；总压力仍基于规则公式，AI 只用于“AI 心晴见解”文本。
- 不放宽 `ReviewRequest` 为任意浏览器 payload；extra 字段拒绝仍是安全边界。

---

## 目标接口契约

### 事件档案接口

后端新增接口：

- `POST /api/events`：保存一条事件记录，要求包含 `event_date`。
- `GET /api/events`：按 `event_date desc, created_at desc` 返回事件档案。
- `GET /api/events/analysis`：基于所有事件返回总压力分析。
- `POST /api/events/insight`：基于事件档案和总压力分析调用 AI，生成 AI 心晴见解。

保留现有接口：

- `POST /api/analyze` 继续支持单事件分析，兼容旧前端和测试。
- `POST /api/simulate` 与 `POST /api/simulate/stream` 保留现有字段，并新增可选 `dialogue` 字段用于持续对话。
- `POST /api/review` 保持现有复盘契约。

### 事件日期字段

字段名统一为 `event_date`，格式为 ISO 日期字符串 `YYYY-MM-DD`。前端标签显示为“事件日期”。后端用 `date` 类型校验，禁止空值，默认值由前端填入今天日期，但后端仍要求请求里显式传入。

### 事件档案总压力公式

总压力必须基于档案内所有事件计算。每条事件先复用现有 `analyze_pressure()` 得到单事件压力 `single_score_i`，再按事件日期做时效加权和累积修正。

公式：

```text
recency_weight_i =
  1.00, days_since_event <= 7
  0.85, 8 <= days_since_event <= 14
  0.70, 15 <= days_since_event <= 30
  0.50, 31 <= days_since_event <= 60
  0.30, days_since_event > 60

weighted_average =
  sum(single_score_i * recency_weight_i) / sum(recency_weight_i)

active_30d_count = count(events where days_since_event <= 30)
event_type_count = count(distinct event_type in all events)

accumulation_bonus =
  min(15, round(5 * ln(1 + max(active_30d_count - 1, 0))))

diversity_bonus =
  min(8, 2 * max(event_type_count - 1, 0))

archive_pressure_score =
  clamp(round(weighted_average + accumulation_bonus + diversity_bonus), 0, 100)
```

事实合理性要求：

- 只有 1 条事件时，总压力应接近该事件的单事件分数，不额外放大。
- 多条 30 天内事件会产生累积加成，符合“问题反复出现会增加压力”的事实。
- 多个不同类型的冲突会产生少量多源加成，符合“压力来源变复杂”的事实。
- 60 天前事件仍有低权重影响，但不会主导当前压力。
- 无事件时返回 `pressure_score=0`、`risk_level=stable`、`risk_label=关系平稳`，并提示先记录事件。

主要压力来源算法：

```text
对每条事件：
  event_source_label contribution += single_score_i * recency_weight_i * 0.55

  if frequency is weekly_multiple or daily:
    "发生频率较高" contribution += FREQUENCY_SCORES[frequency] * recency_weight_i * 0.20

  if has_communicated is false:
    "尚未有效沟通" contribution += 100 * recency_weight_i * 0.15

  if has_conflict is true:
    "已出现争吵或冷战" contribution += 100 * recency_weight_i * 0.10

按贡献值从高到低排序。
返回前 3 个标签。
把这 3 个来源的贡献归一化成百分比，且百分比总和必须为 100。
```

前端压力来源柱状图必须使用后端返回的 `source_breakdown[]`，不能再把来源平均分成相同百分比。

---

## 文件结构

新增：

- `backend/app/event_store.py`: 本地 JSON 事件档案 store、排序、读写和测试注入点。
- `backend/app/archive_analysis.py`: 总压力公式、主要压力来源算法、档案趋势文案。
- `backend/tests/test_event_archive.py`: 事件日期、档案持久化、排序、总压力公式和来源贡献测试。
- `frontend/src/data/eventArchive.ts`: 事件档案 API 类型、请求函数和响应守卫。
- `frontend/src/views/EventArchiveView.vue`: 事件档案页面。
- `frontend/scripts/verify-v2.mjs`: v2 前端静态门禁。

修改：

- `backend/app/schemas.py`: 新增事件档案、总压力分析、AI insight 和模拟持续对话字段。
- `backend/app/main.py`: 新增事件档案路由，模拟接口接受 `dialogue`。
- `backend/app/ai_prompts.py`: 新增持续对话提示词输入和档案 AI insight 提示词。
- `backend/app/ai_service.py`: 新增 archive insight AI 调用。
- `backend/tests/test_api.py`: 新增事件档案路由、模拟持续对话、AI insight 错误语义测试。
- `backend/tests/test_ai_contracts.py`: 新增持续对话和 archive insight schema/提示词测试。
- `docs/backend-api-contract.md`: 写明新增接口、错误码、字段、交接样例。
- `docs/scoring-model.md`: 补充总压力公式和主要压力来源算法。
- `docs/v2-status.md`: 记录 v2 修复范围和交接状态。
- `frontend/src/router/index.ts`: 新增 `/archive` 路由。
- `frontend/src/App.vue`: 新增事件档案导航入口。
- `frontend/src/views/RecordView.vue`: 新增 `event_date` 字段，提交到 `POST /api/events`。
- `frontend/src/views/AnalysisView.vue`: 改为读取 `GET /api/events/analysis` 和 `POST /api/events/insight`。
- `frontend/src/views/SimulationView.vue`: 支持持续对话、逐条间隔显示和页面优化。
- `frontend/src/views/ReviewView.vue`: 使用完整模拟会话生成复盘 dialogue。
- `frontend/src/styles/main.css`: 事件档案页、模拟页持续对话和移动端样式。
- `frontend/package.json`: 新增 `verify:v2`。

不修改：

- 第 7 天视频、海报或线上提交材料。
- 账号系统、云存储、权限系统。
- 与本次 v2 五个问题无关的页面重做。

---

### 任务 1：后端事件档案契约

**负责人：** 朱春雯

**文件：**
- 修改：`backend/app/schemas.py`
- 新增：`backend/app/event_store.py`
- 修改：`backend/app/main.py`
- 新增：`backend/tests/test_event_archive.py`
- 修改：`backend/tests/test_api.py`

- [ ] **步骤 1：为事件日期和档案路由编写预期失败测试**

创建 `backend/tests/test_event_archive.py`，覆盖：

```python
from datetime import date

from app.archive_analysis import analyze_archive_pressure
from app.event_store import InMemoryEventStore
from app.schemas import EventRecordCreate


def test_event_record_requires_event_date():
    payload = EventRecordCreate(
        event_date=date(2026, 5, 15),
        event_type="noise",
        severity=4,
        frequency="weekly_multiple",
        emotion="anxious",
        has_communicated=False,
        has_conflict=True,
        description="舍友晚上打游戏声音很大，影响睡眠。",
    )

    assert payload.event_date == date(2026, 5, 15)


def test_event_store_lists_newest_event_first():
    store = InMemoryEventStore()
    older = EventRecordCreate(
        event_date=date(2026, 5, 12),
        event_type="hygiene",
        severity=2,
        frequency="occasional",
        emotion="helpless",
        has_communicated=True,
        has_conflict=False,
        description="公共区域偶尔有点乱。",
    )
    newer = EventRecordCreate(
        event_date=date(2026, 5, 15),
        event_type="noise",
        severity=4,
        frequency="weekly_multiple",
        emotion="anxious",
        has_communicated=False,
        has_conflict=True,
        description="舍友晚上打游戏声音很大。",
    )

    first = store.add(older)
    second = store.add(newer)

    assert [event.id for event in store.list()] == [second.id, first.id]
```

向 `backend/tests/test_api.py` 追加路由测试：

```python
def test_create_event_record_returns_saved_event_and_single_analysis():
    response = client.post(
        "/api/events",
        json={
            "event_date": "2026-05-15",
            "event_type": "noise",
            "severity": 4,
            "frequency": "weekly_multiple",
            "emotion": "anxious",
            "has_communicated": False,
            "has_conflict": True,
            "description": "舍友晚上打游戏声音很大，影响睡眠。",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["event_date"] == "2026-05-15"
    assert body["single_analysis"]["pressure_score"] == 76
```

- [ ] **步骤 2：运行测试并确认预期失败**

运行：

```bash
cd backend
python3 -m pytest -p no:cacheprovider tests/test_event_archive.py tests/test_api.py::test_create_event_record_returns_saved_event_and_single_analysis -q
```

预期结果：失败，因为事件档案 schema、store 和路由还不存在。

- [ ] **步骤 3：新增 schema**

在 `backend/app/schemas.py` 新增这些模型：

```python
from datetime import date, datetime


class EventRecordCreate(AnalyzeRequest):
    event_date: date


class EventRecord(EventRecordCreate):
    id: str
    created_at: datetime
    single_analysis: AnalyzeResponse


class EventArchiveResponse(BaseModel):
    events: list[EventRecord]


class SourceBreakdown(BaseModel):
    label: str
    percent: int
    contribution: float


class ArchiveAnalysisResponse(AnalyzeResponse):
    event_count: int
    active_30d_count: int
    source_breakdown: list[SourceBreakdown]
```

- [ ] **步骤 4：新增事件档案 store**

实现 `backend/app/event_store.py`，包含：

- 测试用 `InMemoryEventStore`。
- 本地演示持久化用 `JsonEventStore`。
- `get_default_event_store_path()`，在未配置 `DORM_HARMONY_EVENT_STORE_PATH` 时返回 `backend/.runtime/events.json`。
- `add(payload: EventRecordCreate) -> EventRecord`.
- `list() -> list[EventRecord]`, sorted by `event_date desc, created_at desc`.
- 写入时先写临时文件，再替换正式 JSON 文件，保证原子写入。

- [ ] **步骤 5：接入路由**

在 `backend/app/main.py` 新增：

- 依赖注入函数 `get_event_store()`。
- `POST /api/events`，返回 `EventRecord`。
- `GET /api/events`，返回 `EventArchiveResponse`。

`POST /api/events` 必须对已保存事件调用 `analyze_pressure()`，并存储得到的 `single_analysis`。

- [ ] **步骤 6：验证通过**

运行：

```bash
cd backend
python3 -m pytest -p no:cacheprovider tests/test_event_archive.py tests/test_api.py::test_create_event_record_returns_saved_event_and_single_analysis -q
```

预期结果：通过。

---

### 任务 2：后端事件档案总压力分析

**负责人：** 朱春雯

**文件：**
- 新增：`backend/app/archive_analysis.py`
- 修改：`backend/app/main.py`
- 修改：`backend/tests/test_event_archive.py`
- 修改：`docs/scoring-model.md`

- [ ] **步骤 1：编写总压力公式的预期失败测试**

向 `backend/tests/test_event_archive.py` 追加：

```python
from datetime import date

from app.archive_analysis import analyze_archive_pressure


def test_archive_pressure_single_event_stays_close_to_single_score():
    store = InMemoryEventStore()
    store.add(EventRecordCreate(
        event_date=date(2026, 5, 15),
        event_type="noise",
        severity=4,
        frequency="weekly_multiple",
        emotion="anxious",
        has_communicated=False,
        has_conflict=True,
        description="舍友晚上打游戏声音很大，影响睡眠。",
    ))

    result = analyze_archive_pressure(store.list(), today=date(2026, 5, 15))

    assert result.pressure_score == 76
    assert result.risk_level == "high"
    assert result.event_count == 1
```

```python
def test_archive_pressure_accumulates_recent_multiple_events():
    store = InMemoryEventStore()
    store.add(EventRecordCreate(
        event_date=date(2026, 5, 15),
        event_type="noise",
        severity=4,
        frequency="weekly_multiple",
        emotion="anxious",
        has_communicated=False,
        has_conflict=True,
        description="舍友晚上打游戏声音很大。",
    ))
    store.add(EventRecordCreate(
        event_date=date(2026, 5, 14),
        event_type="hygiene",
        severity=4,
        frequency="daily",
        emotion="angry",
        has_communicated=False,
        has_conflict=True,
        description="公共区域长期没人打扫，已经吵过。",
    ))
    store.add(EventRecordCreate(
        event_date=date(2026, 5, 13),
        event_type="privacy",
        severity=3,
        frequency="weekly_multiple",
        emotion="wronged",
        has_communicated=False,
        has_conflict=False,
        description="舍友未经允许拿用私人物品。",
    ))

    result = analyze_archive_pressure(store.list(), today=date(2026, 5, 15))

    assert result.pressure_score >= 80
    assert result.risk_level == "severe"
    assert result.active_30d_count == 3
    assert result.source_breakdown[0].percent > 0
```

```python
def test_archive_pressure_old_event_has_lower_current_weight():
    store = InMemoryEventStore()
    store.add(EventRecordCreate(
        event_date=date(2026, 2, 1),
        event_type="noise",
        severity=5,
        frequency="daily",
        emotion="depressed",
        has_communicated=False,
        has_conflict=True,
        description="很久之前的严重噪音冲突。",
    ))

    result = analyze_archive_pressure(store.list(), today=date(2026, 5, 15))

    assert result.pressure_score < 80
    assert result.active_30d_count == 0
```

- [ ] **步骤 2：运行测试并确认预期失败**

运行：

```bash
cd backend
python3 -m pytest -p no:cacheprovider tests/test_event_archive.py -q
```

预期结果：失败，因为 `archive_analysis.py` 不存在，或公式尚未实现。

- [ ] **步骤 3：严格按本文档实现公式**

创建 `backend/app/archive_analysis.py`，按“目标接口契约”章节中的公式实现。复用现有 `analyze_pressure()`，通过公开响应字段保持 `_risk_for_score()` 的行为一致，并复用当前 `EVENT_SOURCE_LABELS`、`FREQUENCY_SCORES`。

压力来源贡献使用这些标签：

- event type label from existing `EVENT_SOURCE_LABELS`.
- `发生频率较高`.
- `尚未有效沟通`.
- `已出现争吵或冷战`.

百分比归一化规则：先对每个主要来源百分比四舍五入，再调整贡献最大的来源，使总和严格等于 100。

- [ ] **步骤 4：新增总压力分析路由**

在 `backend/app/main.py` 新增 `GET /api/events/analysis`。它必须：

- read all events from `get_event_store()`;
- 调用 `analyze_archive_pressure(events)`；
- 返回 `ArchiveAnalysisResponse`。

- [ ] **步骤 5：更新评分模型文档**

在 `docs/scoring-model.md` 新增 `## 事件档案总压力模型` 小节，写入：

- the recency table;
- the formula;
- the main source contribution algorithm;
- 单条事件、近期多次事件、旧事件、无事件这四种情况的预期行为。

- [ ] **步骤 6：验证通过**

运行：

```bash
cd backend
python3 -m pytest -p no:cacheprovider tests/test_event_archive.py -q
```

预期结果：通过。

---

### 任务 3：后端持续对话模拟与 AI 心晴见解

**负责人：** 朱春雯

**文件：**
- 修改：`backend/app/schemas.py`
- 修改：`backend/app/ai_prompts.py`
- 修改：`backend/app/ai_service.py`
- 修改：`backend/app/main.py`
- 修改：`backend/tests/test_ai_contracts.py`
- 修改：`backend/tests/test_api.py`
- 修改：`docs/backend-api-contract.md`

- [ ] **步骤 1：编写预期失败测试**

为模拟接口可选 `dialogue` 增加测试：

```python
def test_simulate_request_accepts_prior_dialogue_for_continuous_conversation():
    request = SimulateRequest(
        scenario="舍友晚上打游戏声音很大，影响睡眠。",
        user_message="那我们能不能约定 11 点后戴耳机？",
        risk_level="high",
        dialogue=[
            {"speaker": "user", "message": "晚上能不能小声一点？"},
            {"speaker": "roommate_a", "message": "我也没开很大声吧。"},
        ],
    )

    assert len(request.dialogue) == 2
    assert request.dialogue[1].speaker == "roommate_a"
```

为事件档案 AI 心晴见解增加测试：

```python
def test_archive_insight_endpoint_returns_503_when_ai_key_missing():
    app.dependency_overrides[get_ai_service] = lambda: MissingKeyService()

    response = client.post("/api/events/insight")

    assert response.status_code == 503
    assert_llm_key_hint(response.json()["detail"])
```

- [ ] **步骤 2：运行测试并确认预期失败**

运行：

```bash
cd backend
python3 -m pytest -p no:cacheprovider tests/test_ai_contracts.py::test_simulate_request_accepts_prior_dialogue_for_continuous_conversation tests/test_api.py::test_archive_insight_endpoint_returns_503_when_ai_key_missing -q
```

预期结果：失败，因为持续对话和档案 AI 心晴见解尚不存在。

- [ ] **步骤 3：兼容性扩展模拟接口 schema**

在 `SimulateRequest` 中新增：

```python
dialogue: list[DialogueMessage] = Field(default_factory=list, max_length=20)
```

保持 `dialogue` 可选，确保现有客户端继续可用。

- [ ] **步骤 4：把历史对话写入 prompt**

在 `build_simulate_messages()` 中，把历史 `dialogue` 放在当前 `user_message` 之前。Prompt 必须包含：

```text
如果 dialogue 非空，请把本次 user_message 视为同一场景下的下一轮对话，不要重启场景，不要重复上一轮已经说过的内容。
```

- [ ] **步骤 5：新增档案见解 schema 和 AI service 方法**

新增模型：

```python
class ArchiveInsightResponse(BaseModel):
    insight: str
    care_suggestion: str
    communication_focus: list[str] = Field(min_length=1)
    safety_note: str
```

新增 `DormHarmonyAIService.archive_insight(events, analysis)`，调用新的提示词构造函数并返回 `ArchiveInsightResponse`。错误行为保持：

- missing key: `503`;
- upstream/model/parse failure: `502`;
- unsafe or malformed safety note: `502`.

- [ ] **步骤 6：新增路由**

在 `backend/app/main.py` 新增 `POST /api/events/insight`。它读取当前事件档案和总压力分析，然后调用 AI service。

If there are no events, return `400` with detail `请先记录至少一条事件后再生成 AI 心晴见解。`

- [ ] **步骤 7：更新 API 契约文档**

在 `docs/backend-api-contract.md` 中记录：

- `/api/simulate` 和 `/api/simulate/stream` 中的可选 `dialogue`；
- `POST /api/events/insight`;
- 400/503/502 behavior;
- `ArchiveInsightResponse` fields.

- [ ] **步骤 8：验证通过**

运行：

```bash
cd backend
python3 -m pytest -p no:cacheprovider tests/test_ai_contracts.py tests/test_api.py -q
```

预期结果：通过。

---

### 任务 4：前端事件日期与事件档案页

**负责人：** 曹乐

**文件：**
- 新增：`frontend/src/data/eventArchive.ts`
- 修改：`frontend/src/views/RecordView.vue`
- 新增：`frontend/src/views/EventArchiveView.vue`
- 修改：`frontend/src/router/index.ts`
- 修改：`frontend/src/App.vue`
- 修改：`frontend/src/styles/main.css`
- 新增：`frontend/scripts/verify-v2.mjs`
- 修改：`frontend/package.json`

- [ ] **步骤 1：编写前端预期失败验证脚本**

创建 `frontend/scripts/verify-v2.mjs`，检查以下字符串：

- `src/router/index.ts` 包含 `/archive`、`name: 'archive'` 和 `EventArchiveView.vue`。
- `src/App.vue` 包含 `事件档案` 和 `name: 'archive'`。
- `src/views/RecordView.vue` 包含 `event_date`、`事件日期` 和 `createEventRecord`。
- `src/views/EventArchiveView.vue` 包含 `事件档案`、`fetchEventArchive`、`生成压力分析报告` 和 `name: 'analysis'`。
- `src/data/eventArchive.ts` 包含 `/api/events`、`/api/events/analysis`、`/api/events/insight`、`ArchiveAnalysisResponse` 和 `ArchiveInsightResponse`。
- `src/styles/main.css` 包含 `archive-page`、`event-timeline` 和 `archive-event-card`。

新增 package 脚本：

```json
"verify:v2": "node scripts/verify-v2.mjs"
```

- [ ] **步骤 2：运行验证脚本并确认预期失败**

运行：

```bash
cd frontend
npm run verify:v2
```

预期结果：失败，因为事件档案页面和 API 层还不存在。

- [ ] **步骤 3：新增 API 层**

创建 `frontend/src/data/eventArchive.ts`，包含：

- 包含 `event_date` 的 `EventRecordCreate`。
- `EventRecord`.
- `EventArchiveResponse`.
- `ArchiveAnalysisResponse`.
- `ArchiveInsightResponse`.
- `createEventRecord(payload)`.
- `fetchEventArchive()`.
- `fetchArchiveAnalysis()`.
- `fetchArchiveInsight()`.

所有函数使用原生 `fetch`。只有明确标记为兜底时才能返回结构化演示兜底；API 失败状态必须在用户可见文案中保留 HTTP 状态。

- [ ] **步骤 4：在事件记录页增加事件日期字段**

在 `RecordView.vue` 中：

- 在表单状态中增加 `event_date`，默认值为今天的 `YYYY-MM-DD`；
- 增加一个可见的日期输入框，标签为 `事件日期`；
- 通过 `createEventRecord()` 提交，而不是直接调用 `submitAnalyzeRequest()`；
- 成功后跳转到 `{ name: 'archive' }`；
- 保留旧的 `LAST_EVENT_STORAGE_KEY` 和 `ANALYSIS_RESULT_STORAGE_KEY` 仅作为兼容缓存，不再作为主要数据来源。

- [ ] **步骤 5：新增事件档案页**

创建 `EventArchiveView.vue`：

- 页面挂载时请求 `GET /api/events`；
- 按后端返回顺序渲染事件卡片；
- 展示日期、事件类型、严重程度、发生频率、情绪、单事件压力值、风险标签和描述；
- 展示空状态 `还没有事件记录，请先记录一条宿舍事件。`；
- 提供跳转到 `record` 和 `analysis` 的按钮；
- 不在该页面计算总压力。

- [ ] **步骤 6：新增路由和导航**

新增 `/archive` 路由，路由名为 `archive`；同时新增桌面端和移动端导航入口 `事件档案`。

- [ ] **步骤 7：新增样式**

新增这些 CSS：

- `.archive-page`;
- `.event-timeline`;
- `.archive-event-card`;
- 移动端换行约束，避免事件卡片横向溢出。

- [ ] **步骤 8：验证通过**

运行：

```bash
cd frontend
npm run verify:v2
npm run build
```

预期结果：两条命令都通过。

---

### 任务 5：前端总压力分析与 AI 心晴见解

**负责人：** 曹乐

**文件：**
- 修改：`frontend/src/views/AnalysisView.vue`
- 修改：`frontend/src/data/eventArchive.ts`
- 修改：`frontend/src/styles/main.css`
- 修改：`frontend/scripts/verify-v2.mjs`

- [ ] **步骤 1：扩展验证脚本**

更新 `verify-v2.mjs`，要求：

- `AnalysisView.vue` 包含 `fetchArchiveAnalysis`、`fetchArchiveInsight`、`source_breakdown`、`AI 心晴见解` 和 `事件档案`；
- `AnalysisView.vue` 不再使用 `Math.floor(100 / labels.length)` 计算平均来源百分比；
- `eventArchive.ts` 包含 `source_breakdown` 和 `communication_focus` 的响应守卫。

- [ ] **步骤 2：运行验证脚本并确认预期失败**

运行：

```bash
cd frontend
npm run verify:v2
```

预期结果：失败，因为分析页仍读取单条缓存分析，并且把来源柱状图平均分配百分比。

- [ ] **步骤 3：加载总压力分析**

在 `AnalysisView.vue` 中：

- 页面挂载时调用 `fetchArchiveAnalysis()`；
- 渲染后端返回的 `pressure_score`、`risk_label`、`source_breakdown`、`emotion_keywords`、`trend_message`、`suggestion`；
- 展示 `event_count` 和 `active_30d_count`；
- 事件数为 0 时提供跳转到 `archive` 的入口。

- [ ] **步骤 4：单独加载 AI 心晴见解**

总压力分析加载完成且至少有一条事件后，调用 `fetchArchiveInsight()`。

展示：

- `insight`;
- `care_suggestion`;
- `communication_focus`;
- `safety_note`.

如果接口返回 503，展示 `AI 心晴见解需要配置 DEEPSEEK_API_KEY 后生成。` 如果返回 502，展示 `AI 心晴见解暂时不可用，请稍后重试。` 不允许用演示文本替代并标记为真实 AI。

- [ ] **步骤 5：使用后端返回的压力来源分布**

用 `result.source_breakdown` 替换当前平均百分比逻辑。UI 必须展示后端为每个来源返回的 `percent`。

- [ ] **步骤 6：验证通过**

运行：

```bash
cd frontend
npm run verify:v2
npm run build
```

预期结果：两条命令都通过。

---

### 任务 6：前端持续对话模拟与间隔回复

**负责人：** 曹乐

**文件：**
- 修改：`frontend/src/views/SimulationView.vue`
- 修改：`frontend/src/views/ReviewView.vue`
- 修改：`frontend/src/data/week1.ts`
- 修改：`frontend/src/styles/main.css`
- 修改：`frontend/scripts/verify-v2.mjs`

- [ ] **步骤 1：扩展验证脚本**

更新 `verify-v2.mjs`，要求：

- `SimulationView.vue` 包含 `conversationMessages`、`appendReplyWithDelay`、`replyDelayMs` 和 `dialogue`；
- `SimulationView.vue` 在 JSON 回退路径中不再直接执行 `replies.value = result.replies`；
- `SimulationView.vue` 包含 `正在生成` 相关文案或状态；
- `ReviewView.vue` 读取完整对话，而不是只读取最新三条回复。

- [ ] **步骤 2：运行验证脚本并确认预期失败**

运行：

```bash
cd frontend
npm run verify:v2
```

预期结果：失败，因为当前模拟页只保存单轮对话，并且 JSON 回退路径会一次性展示全部回复。

- [ ] **步骤 3：新增完整对话状态**

在 `SimulationView.vue` 中：

- 维护 `conversationMessages: ReviewDialogueLine[]`；
- 用户发送消息时追加 `{ speaker: 'user', message }`；
- 在 `SimulationRequest` 中包含 `dialogue: conversationMessages`；
- 每条舍友回复出现后，追加对应的 `roommate_a`、`roommate_b` 或 `roommate_c` 对话行。

- [ ] **步骤 4：新增间隔回复展示**

实现：

```ts
const replyDelayMs = 750

async function appendReplyWithDelay(reply: SimulationReply, index: number) {
  await new Promise((resolve) => window.setTimeout(resolve, replyDelayMs * index))
  replies.value = [...replies.value, reply]
}
```

流式 `onReply` 事件和 `/api/simulate` JSON 回退结果都必须使用该函数。这样即使流式返回很快，三位舍友回复也不会同时显示。

- [ ] **步骤 5：优化沟通模拟页体验**

新增这些状态：

- 生成中禁用发送按钮；
- `正在生成舍友 A/B/C 的回复` 状态；
- 可见的完整对话区域，展示之前的用户轮次和舍友回复；
- 重置对话时清空 `conversationMessages`、`replies` 和模拟缓存；
- 移动端布局保持输入框和消息列表可读，不横向溢出。

- [ ] **步骤 6：更新复盘上下文**

在 `ReviewView.vue` 中，从已存储的完整对话构造 `dialogue`。如果不存在完整对话，则使用当前兜底逻辑。

- [ ] **步骤 7：验证通过**

运行：

```bash
cd frontend
npm run verify:v2
npm run build
```

预期结果：两条命令都通过。

---

### 任务 7：契约文档与 v2 前后端交接

**负责人：** 朱春雯和曹乐共同完成

**文件：**
- 修改：`docs/backend-api-contract.md`
- 新增：`docs/v2-status.md`
- 修改：`docs/scoring-model.md`
- 修改：`frontend/README.md`
- 修改：`README.md`

- [ ] **步骤 1：后端负责人更新接口契约文档**

朱春雯必须更新 `docs/backend-api-contract.md`，写入：

- `POST /api/events` 请求/响应样例；
- `GET /api/events` 响应样例；
- `GET /api/events/analysis` 响应样例；
- `POST /api/events/insight` 响应样例和 400/503/502 错误语义；
- `/api/simulate` 和 `/api/simulate/stream` 的可选 `dialogue` 字段；
- 准确的本地启动命令：

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- [ ] **步骤 2：后端负责人提供联调样例 payload**

朱春雯必须在 `docs/backend-api-contract.md` 添加 `## 前后端交接样例` 小节，并包含一条完整样例流程：

1. 使用 `event_date` 创建事件；
2. 查询事件档案；
3. 查询总压力分析；
4. 使用 `dialogue` 发起第二轮模拟请求；
5. 生成事件档案 AI 心晴见解。

这些样例必须使用前端实际消费的准确字段名。

- [ ] **步骤 3：前端负责人更新前端运行文档**

曹乐必须更新 `frontend/README.md`，写入：

```bash
npm install
npm run dev
npm run verify:phase2
npm run verify:v2
npm run build
```

同时说明 Vite 开发服务器通过 `/api` 代理访问 `http://127.0.0.1:8000` 后端。

- [ ] **步骤 4：双方在 `docs/v2-status.md` 记录 v2 交接清单**

新增 `## v2 前后端交接清单` 小节，并写入以下清单：

- 朱春雯完成后端接口、schema、错误码、测试和 API 契约样例。
- 朱春雯运行 `cd backend && python3 -m pytest -p no:cacheprovider` 并记录结果。
- 曹乐根据 `docs/backend-api-contract.md` 更新前端 API 类型和页面。
- 曹乐运行 `cd frontend && npm run verify:phase2 && npm run verify:v2 && npm run build` 并记录结果。
- 双方用同一条夜间噪音样例走通 `record -> archive -> analysis -> simulate -> review`。
- AI Key 缺失时，前端显示明确配置提示；后端返回 503；不使用假成功。
- 真实 AI 可用时，`AI 心晴见解` 来自 `POST /api/events/insight`。

- [ ] **步骤 5：验证文档已写明双方职责**

运行：

```bash
rg -n "朱春雯|曹乐|前后端交接|verify:v2|/api/events|/api/events/analysis|/api/events/insight" docs frontend/README.md README.md
```

预期结果：输出包含已更新的契约、状态文档和前端 README 引用。

---

### 任务 8：最终验证与评审门禁

**负责人：** 执行本计划的 Codex agent

**文件：**
- 对已修改文件做只读验证。

- [ ] **步骤 1：后端验证**

运行：

```bash
cd backend
python3 -m pytest -p no:cacheprovider
```

预期结果：全部后端测试通过。

- [ ] **步骤 2：前端验证**

运行：

```bash
cd frontend
npm run verify:phase2
npm run verify:v2
npm run build
```

预期结果：全部前端检查通过。

- [ ] **步骤 3：使用子代理评审**

使用两个新的评审子代理：

- 后端评审子代理检查 schema 安全边界、JSON store 行为、压力公式、AI 错误语义和契约文档。
- 前端评审子代理检查路由流程、事件档案体验、持续对话状态、延迟回复和 API 字段对齐。

两次评审都必须只读。如果任一评审发现阻塞问题，先修复，再重新运行对应验证命令。

- [ ] **步骤 4：手动 smoke 路径**

后端运行在 `127.0.0.1:8000`、前端运行在 Vite 后，按以下路径手动验证：

1. 打开 `http://localhost:5173/record`；
2. 记录一条日期为今天的噪音事件；
3. 确认 `/archive` 展示该事件；
4. 打开 `/analysis`，确认压力值来自事件档案总压力；
5. 打开 `/simulate`，连续发送两条用户消息，确认第二次请求延续同一段对话；
6. 确认三位舍友回复按间隔一条一条出现；
7. 打开 `/review`，确认复盘使用完整对话；
8. 确认配置 Key 时 AI 心晴见解显示真实内容，缺 Key 时显示 503 配置提示。

- [ ] **步骤 5：最终状态记录**

更新实现分支总结，写明：

- 已修改文件；
- 后端测试结果；
- 前端验证结果；
- 手动 smoke 结果；
- 如有未解决项，列出未解决项。

在当前环境运行并阅读步骤 1 和步骤 2 的命令输出之前，不允许声明任务完成。
