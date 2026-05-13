# 朱春雯第二阶段 LangChain AI 后端 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Zhu Chunwen's phase-2 backend AI work with real LangChain/OpenAI calls, structured `/api/simulate` and `/api/review` endpoints, safety boundaries, demo samples, and updated documentation.

**Architecture:** Keep FastAPI thin and move AI orchestration into `backend/app/ai_service.py`. Prompt text lives in `backend/app/ai_prompts.py`; request/response contracts live in `backend/app/schemas.py`; demo samples live in `backend/app/demo_data.py`; tests inject fake runners and never require real API keys or network.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic v2, pytest, LangChain `langchain_openai.ChatOpenAI`, OpenAI API key via `OPENAI_API_KEY`.

---

## File Structure

Create:

- `backend/app/ai_prompts.py`: Prompt builders and safety instructions for simulation and review.
- `backend/app/ai_service.py`: AI service, LangChain runner, environment config, and safe exception types.
- `backend/app/demo_data.py`: Three phase-2 demo scenarios.
- `backend/tests/test_ai_contracts.py`: Schema, prompt, safety, and demo-data tests.
- `backend/tests/test_ai_service.py`: Service-layer tests with fake runners.
- `docs/phase2-status.md`: Phase-2 completion status after implementation.

Modify:

- `backend/app/schemas.py`: Add simulate/review request and response models.
- `backend/app/main.py`: Add dependency-injected `/api/simulate` and `/api/review` endpoints.
- `backend/requirements.txt`: Add LangChain/OpenAI dependencies.
- `backend/tests/test_api.py`: Add endpoint tests and dependency overrides.
- `backend/tests/test_scoring.py`: Add B2-1 regression showing different inputs produce different risk levels.
- `README.md`: Update current backend status, environment variables, and AI endpoint run notes.
- `docs/backend-api-contract.md`: Promote `/api/simulate` and `/api/review` from draft to implemented runtime contracts.
- `DEVELOPMENT_PLAN_AND_DELIVERABLES.md`: Mark B2-1 through B2-6 completion evidence for Zhu Chunwen.

Do not modify:

- `frontend/**`
- 第 7 天演示视频、宣传海报、线上提交材料成品
- History/storage endpoints

---

### Task 1: Contracts, Prompts, and Demo Data

**Files:**
- Modify: `backend/app/schemas.py`
- Create: `backend/app/ai_prompts.py`
- Create: `backend/app/demo_data.py`
- Create: `backend/tests/test_ai_contracts.py`
- Modify: `backend/tests/test_scoring.py`

- [ ] **Step 1: Write failing contract and demo tests**

Create `backend/tests/test_ai_contracts.py` with:

```python
import pytest
from pydantic import ValidationError

from app.ai_prompts import REVIEW_SYSTEM_PROMPT, SIMULATE_SYSTEM_PROMPT, build_review_messages, build_simulate_messages
from app.demo_data import DEMO_SCENARIOS
from app.schemas import (
    DialogueMessage,
    ReviewRequest,
    ReviewResponse,
    RoommateReply,
    SimulateRequest,
    SimulateResponse,
)


def test_simulate_request_trims_optional_context_to_none():
    request = SimulateRequest(
        scenario="  舍友晚上打游戏声音较大，影响睡眠  ",
        user_message="  能不能晚上小声一点？  ",
        risk_level="high",
        context="   ",
    )

    assert request.scenario == "舍友晚上打游戏声音较大，影响睡眠"
    assert request.user_message == "能不能晚上小声一点？"
    assert request.context is None


def test_simulate_request_rejects_blank_user_message():
    with pytest.raises(ValidationError):
        SimulateRequest(scenario="噪音冲突", user_message="   ")


def test_simulate_response_requires_three_fixed_roommate_roles():
    response = SimulateResponse(
        replies=[
            RoommateReply(roommate="舍友 A", personality="直接型", message="我也没开很大声吧。"),
            RoommateReply(roommate="舍友 B", personality="回避型", message="这个之后再说吧。"),
            RoommateReply(roommate="舍友 C", personality="调和型", message="我们可以定个休息规则。"),
        ],
        safety_note="本回复仅用于宿舍沟通演练，不进行心理诊断、医学判断或人格评价。如有现实安全风险，请联系辅导员、心理老师、家人或可信任同学。",
    )

    assert [reply.roommate for reply in response.replies] == ["舍友 A", "舍友 B", "舍友 C"]


def test_simulate_response_rejects_missing_fixed_role():
    with pytest.raises(ValidationError):
        SimulateResponse(
            replies=[
                RoommateReply(roommate="舍友 A", personality="直接型", message="我也没开很大声吧。"),
                RoommateReply(roommate="舍友 C", personality="调和型", message="我们可以定个休息规则。"),
            ],
            safety_note="本回复仅用于宿舍沟通演练，不进行心理诊断、医学判断或人格评价。",
        )


def test_review_request_requires_at_least_one_dialogue_message():
    with pytest.raises(ValidationError):
        ReviewRequest(scenario="噪音冲突", dialogue=[])


def test_review_response_requires_actionable_lists():
    response = ReviewResponse(
        summary="用户表达了睡眠受影响的事实，整体语气较温和。",
        strengths=["说明了具体影响"],
        risks=["可以进一步明确时间范围"],
        rewritten_message="我最近睡眠状态不太好，晚上 11 点后能不能戴耳机或调低音量？",
        next_steps=["选择双方情绪平稳的时间沟通"],
        safety_note="本复盘仅用于沟通训练建议，不进行心理诊断、医学判断或人格评价。如压力持续升高，请寻求现实支持。",
    )

    assert response.strengths == ["说明了具体影响"]


def test_prompts_contain_role_and_safety_boundaries():
    required_phrases = [
        "大学宿舍关系沟通场景",
        "不进行心理疾病诊断",
        "不进行医学判断",
        "不进行人格评价",
        "不得输出攻击",
        "辅导员",
        "心理老师",
    ]

    for phrase in required_phrases:
        assert phrase in SIMULATE_SYSTEM_PROMPT
        assert phrase in REVIEW_SYSTEM_PROMPT

    assert "舍友 A" in SIMULATE_SYSTEM_PROMPT
    assert "直接型" in SIMULATE_SYSTEM_PROMPT
    assert "舍友 B" in SIMULATE_SYSTEM_PROMPT
    assert "回避型" in SIMULATE_SYSTEM_PROMPT
    assert "舍友 C" in SIMULATE_SYSTEM_PROMPT
    assert "调和型" in SIMULATE_SYSTEM_PROMPT


def test_prompt_builders_include_user_inputs():
    simulate_request = SimulateRequest(
        scenario="舍友晚上打游戏声音较大，影响睡眠",
        user_message="我想商量一下晚上能不能小声一点。",
        risk_level="high",
        context="用户尚未正式沟通。",
    )
    review_request = ReviewRequest(
        scenario="舍友晚上打游戏声音较大，影响睡眠",
        dialogue=[
            DialogueMessage(speaker="user", message="我想商量一下晚上能不能小声一点。"),
            DialogueMessage(speaker="roommate_a", message="我也没开很大声吧。"),
        ],
    )

    simulate_messages = build_simulate_messages(simulate_request)
    review_messages = build_review_messages(review_request)

    assert "我想商量一下晚上能不能小声一点" in simulate_messages[-1][1]
    assert "用户尚未正式沟通" in simulate_messages[-1][1]
    assert "roommate_a" in review_messages[-1][1]
    assert "我也没开很大声吧" in review_messages[-1][1]


def test_demo_scenarios_cover_required_phase2_cases():
    scenario_ids = {sample["id"] for sample in DEMO_SCENARIOS}

    assert {"noise_conflict", "hygiene_division", "privacy_boundary"}.issubset(scenario_ids)

    for sample in DEMO_SCENARIOS:
        assert sample["analyze_request"]["description"]
        assert sample["simulate_request"]["scenario"]
        assert sample["simulate_request"]["user_message"]
        assert len(sample["review_request"]["dialogue"]) >= 1
```

Append this test to `backend/tests/test_scoring.py`:

```python
def test_phase2_scoring_regression_keeps_inputs_distinct():
    low_request = AnalyzeRequest(
        event_type=EventType.HYGIENE,
        severity=1,
        frequency=EventFrequency.OCCASIONAL,
        emotion=Emotion.HELPLESS,
        has_communicated=True,
        has_conflict=False,
        description="公共区域偶尔有点乱，但已经沟通过。",
    )
    high_request = AnalyzeRequest(
        event_type=EventType.NOISE,
        severity=5,
        frequency=EventFrequency.DAILY,
        emotion=Emotion.DEPRESSED,
        has_communicated=False,
        has_conflict=True,
        description="舍友每天深夜打游戏，长期影响睡眠并已经冷战。",
    )

    low_result = analyze_pressure(low_request)
    high_result = analyze_pressure(high_request)

    assert low_result.pressure_score < high_result.pressure_score
    assert low_result.risk_level == "stable"
    assert high_result.risk_level == "severe"
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
cd backend
python3 -m pytest -p no:cacheprovider tests/test_ai_contracts.py tests/test_scoring.py::test_phase2_scoring_regression_keeps_inputs_distinct -q
```

Expected: FAIL because `app.ai_prompts`, `app.demo_data`, and new schema classes do not exist. The scoring regression may pass after imports are in place, but the command must fail because phase-2 contracts are missing.

- [ ] **Step 3: Add schema models**

Append to `backend/app/schemas.py` after `AnalyzeResponse`:

```python
from typing import Any, Literal

from pydantic import model_validator
```

Move these imports to the top with the existing imports, then add:

```python
RoommateName = Literal["舍友 A", "舍友 B", "舍友 C"]
RoommatePersonality = Literal["直接型", "回避型", "调和型"]
DialogueSpeaker = Literal["user", "roommate_a", "roommate_b", "roommate_c", "system"]


class SimulateRequest(BaseModel):
    scenario: str = Field(max_length=300)
    user_message: str = Field(max_length=500)
    risk_level: str | None = None
    context: str | None = Field(default=None, max_length=500)

    @field_validator("scenario", "user_message", mode="before")
    @classmethod
    def trim_and_require_text(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("value must be a string")

        text = value.strip()
        if not text:
            raise ValueError("value must not be empty")

        return text

    @field_validator("context", mode="before")
    @classmethod
    def trim_optional_context(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("context must be a string")

        text = value.strip()
        return text or None


class RoommateReply(BaseModel):
    roommate: RoommateName
    personality: RoommatePersonality
    message: str = Field(max_length=500)

    @field_validator("message", mode="before")
    @classmethod
    def trim_and_require_message(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("message must be a string")

        message = value.strip()
        if not message:
            raise ValueError("message must not be empty")

        return message


class SimulateResponse(BaseModel):
    replies: list[RoommateReply]
    safety_note: str

    @model_validator(mode="after")
    def require_fixed_roommate_roles(self) -> "SimulateResponse":
        expected = [
            ("舍友 A", "直接型"),
            ("舍友 B", "回避型"),
            ("舍友 C", "调和型"),
        ]
        actual = [(reply.roommate, reply.personality) for reply in self.replies]
        if actual != expected:
            raise ValueError("replies must contain 舍友 A/B/C with fixed personalities in order")
        return self


class DialogueMessage(BaseModel):
    speaker: DialogueSpeaker
    message: str = Field(max_length=500)

    @field_validator("message", mode="before")
    @classmethod
    def trim_and_require_message(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("message must be a string")

        message = value.strip()
        if not message:
            raise ValueError("message must not be empty")

        return message


class ReviewRequest(BaseModel):
    scenario: str = Field(max_length=300)
    dialogue: list[DialogueMessage] = Field(min_length=1)
    original_event: dict[str, Any] | None = None

    @field_validator("scenario", mode="before")
    @classmethod
    def trim_and_require_scenario(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("scenario must be a string")

        scenario = value.strip()
        if not scenario:
            raise ValueError("scenario must not be empty")

        return scenario


class ReviewResponse(BaseModel):
    summary: str
    strengths: list[str] = Field(min_length=1)
    risks: list[str] = Field(min_length=1)
    rewritten_message: str
    next_steps: list[str] = Field(min_length=1)
    safety_note: str
```

- [ ] **Step 4: Add prompt builders**

Create `backend/app/ai_prompts.py`:

```python
from app.schemas import ReviewRequest, SimulateRequest


SAFETY_BOUNDARY_TEXT = (
    "仅处理大学宿舍关系沟通场景。"
    "不进行心理疾病诊断，不进行医学判断，不进行人格评价。"
    "不得输出攻击、威胁、羞辱、操控、报复性建议。"
    "如出现高压力、暴力风险、严重失眠或现实安全风险，"
    "必须提示用户寻求辅导员、心理老师、家人或可信任同学等现实支持。"
)

SIMULATE_SYSTEM_PROMPT = (
    "你是舍友心晴的 AI 沟通演练模块。"
    f"{SAFETY_BOUNDARY_TEXT}"
    "请固定生成三位虚拟舍友的中文回复："
    "舍友 A 是直接型，容易反驳，但不得攻击或羞辱用户；"
    "舍友 B 是回避型，不愿正面沟通，但回复必须有沟通训练价值；"
    "舍友 C 是调和型，愿意缓和关系并提出可执行规则。"
    "输出必须符合结构化 schema，语言温和、具体、可执行。"
)

REVIEW_SYSTEM_PROMPT = (
    "你是舍友心晴的沟通复盘模块。"
    f"{SAFETY_BOUNDARY_TEXT}"
    "请基于对话记录分析用户表达方式，输出表达总结、表达优点、潜在风险、"
    "优化后的沟通话术、后续行动建议和安全提示。"
    "所有建议必须具体、温和、可执行，不得替用户诊断心理问题或评价舍友人格。"
)


def build_simulate_messages(request: SimulateRequest) -> list[tuple[str, str]]:
    context_text = request.context or "无补充背景"
    risk_text = request.risk_level or "未提供"
    human_prompt = (
        f"场景：{request.scenario}\n"
        f"用户准备表达的话术：{request.user_message}\n"
        f"风险等级：{risk_text}\n"
        f"补充背景：{context_text}\n"
        "请生成舍友 A、舍友 B、舍友 C 的结构化回复，并给出安全提示。"
    )
    return [("system", SIMULATE_SYSTEM_PROMPT), ("human", human_prompt)]


def build_review_messages(request: ReviewRequest) -> list[tuple[str, str]]:
    dialogue_text = "\n".join(f"{item.speaker}: {item.message}" for item in request.dialogue)
    original_event_text = request.original_event or "未提供"
    human_prompt = (
        f"场景：{request.scenario}\n"
        f"对话记录：\n{dialogue_text}\n"
        f"原始事件摘要：{original_event_text}\n"
        "请生成结构化沟通复盘报告。"
    )
    return [("system", REVIEW_SYSTEM_PROMPT), ("human", human_prompt)]
```

- [ ] **Step 5: Add demo data**

Create `backend/app/demo_data.py`:

```python
DEMO_SCENARIOS = [
    {
        "id": "noise_conflict",
        "title": "夜间噪音冲突",
        "analyze_request": {
            "event_type": "noise",
            "severity": 4,
            "frequency": "weekly_multiple",
            "emotion": "anxious",
            "has_communicated": False,
            "has_conflict": True,
            "description": "舍友晚上打游戏声音很大，已经连续影响睡眠好几次。",
        },
        "simulate_request": {
            "scenario": "舍友晚上打游戏声音较大，影响睡眠",
            "user_message": "我想和你商量一下，晚上能不能把游戏声音调小一点，我最近睡眠受影响比较明显。",
            "risk_level": "high",
            "context": "用户尚未正式沟通过，但已经因为噪音问题感到焦虑。",
        },
        "review_request": {
            "scenario": "舍友晚上打游戏声音较大，影响睡眠",
            "dialogue": [
                {
                    "speaker": "user",
                    "message": "我想和你商量一下，晚上能不能把游戏声音调小一点。",
                }
            ],
        },
    },
    {
        "id": "hygiene_division",
        "title": "公共卫生分工",
        "analyze_request": {
            "event_type": "hygiene",
            "severity": 3,
            "frequency": "weekly_multiple",
            "emotion": "wronged",
            "has_communicated": True,
            "has_conflict": False,
            "description": "公共区域经常没人打扫，用户觉得自己承担了太多卫生工作。",
        },
        "simulate_request": {
            "scenario": "公共区域长期无人打扫，卫生分工不均",
            "user_message": "我们能不能重新排一下值日表？最近公共区域大多是我在收拾。",
            "risk_level": "pressure",
            "context": "用户已经简单提醒过一次，但没有形成固定分工。",
        },
        "review_request": {
            "scenario": "公共区域长期无人打扫，卫生分工不均",
            "dialogue": [
                {
                    "speaker": "user",
                    "message": "我们能不能重新排一下值日表？最近公共区域大多是我在收拾。",
                }
            ],
        },
    },
    {
        "id": "privacy_boundary",
        "title": "个人隐私边界",
        "analyze_request": {
            "event_type": "privacy",
            "severity": 4,
            "frequency": "occasional",
            "emotion": "angry",
            "has_communicated": False,
            "has_conflict": False,
            "description": "舍友未经允许使用用户的个人物品，用户感到隐私边界被冒犯。",
        },
        "simulate_request": {
            "scenario": "舍友未经允许使用个人物品",
            "user_message": "这个东西对我来说比较私人，下次使用前可以先问我一下吗？",
            "risk_level": "pressure",
            "context": "用户希望表达边界，但不想让关系变僵。",
        },
        "review_request": {
            "scenario": "舍友未经允许使用个人物品",
            "dialogue": [
                {
                    "speaker": "user",
                    "message": "这个东西对我来说比较私人，下次使用前可以先问我一下吗？",
                }
            ],
        },
    },
]
```

- [ ] **Step 6: Run tests and verify GREEN**

Run:

```bash
cd backend
python3 -m pytest -p no:cacheprovider tests/test_ai_contracts.py tests/test_scoring.py -q
```

Expected: PASS for `test_ai_contracts.py` and existing scoring tests.

- [ ] **Step 7: Commit Task 1**

Run:

```bash
git add backend/app/schemas.py backend/app/ai_prompts.py backend/app/demo_data.py backend/tests/test_ai_contracts.py backend/tests/test_scoring.py
git commit -m "feat(ai): 新增第二阶段 AI 契约与样例数据"
```

---

### Task 2: LangChain AI Service

**Files:**
- Modify: `backend/requirements.txt`
- Create: `backend/app/ai_service.py`
- Create: `backend/tests/test_ai_service.py`

- [ ] **Step 1: Add failing service tests**

Create `backend/tests/test_ai_service.py`:

```python
import os

import pytest

from app.ai_service import (
    AIOutputStructureError,
    AIServiceConfigurationError,
    AIServiceUnavailableError,
    DormHarmonyAIService,
    LangChainOpenAIRunner,
    load_ai_settings,
)
from app.schemas import (
    DialogueMessage,
    ReviewRequest,
    ReviewResponse,
    RoommateReply,
    SimulateRequest,
    SimulateResponse,
)


class FakeRunner:
    def generate_simulation(self, request):
        return SimulateResponse(
            replies=[
                RoommateReply(roommate="舍友 A", personality="直接型", message="我也没开很大声吧，但可以试着戴耳机。"),
                RoommateReply(roommate="舍友 B", personality="回避型", message="这个事情我现在不太想聊，但可以晚点再说。"),
                RoommateReply(roommate="舍友 C", personality="调和型", message="我们可以一起定一个晚上安静时间。"),
            ],
            safety_note="本回复仅用于宿舍沟通演练，不代表真实舍友想法，不进行心理诊断、医学判断或人格评价。如有现实安全风险，请联系辅导员、心理老师、家人或可信任同学。",
        )

    def generate_review(self, request):
        return ReviewResponse(
            summary="用户表达了睡眠受影响的事实，整体语气较温和。",
            strengths=["说明了具体影响"],
            risks=["可以进一步明确时间范围"],
            rewritten_message="我最近睡眠状态不太好，晚上 11 点后能不能戴耳机或调低音量？",
            next_steps=["选择双方情绪平稳的时间沟通"],
            safety_note="本复盘仅用于沟通训练建议，不进行心理诊断、医学判断或人格评价。如压力持续升高，请寻求现实支持。",
        )


class BrokenRunner:
    def generate_simulation(self, request):
        raise RuntimeError("network exploded with secret sk-test")

    def generate_review(self, request):
        raise RuntimeError("network exploded with secret sk-test")


class BadShapeRunner:
    def generate_simulation(self, request):
        return {"replies": []}

    def generate_review(self, request):
        return {"summary": "missing fields"}


def test_load_ai_settings_requires_openai_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(AIServiceConfigurationError):
        load_ai_settings()


def test_load_ai_settings_uses_defaults(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.delenv("DORM_HARMONY_LLM_MODEL", raising=False)
    monkeypatch.delenv("DORM_HARMONY_LLM_TIMEOUT", raising=False)

    settings = load_ai_settings()

    assert settings.api_key == "test-key"
    assert settings.model == "gpt-4o-mini"
    assert settings.timeout == 20.0


def test_service_returns_simulation_from_runner():
    request = SimulateRequest(scenario="噪音冲突", user_message="晚上能不能小声一点？")
    service = DormHarmonyAIService(runner=FakeRunner())

    response = service.simulate(request)

    assert [reply.roommate for reply in response.replies] == ["舍友 A", "舍友 B", "舍友 C"]
    assert "不进行心理诊断" in response.safety_note


def test_service_returns_review_from_runner():
    request = ReviewRequest(
        scenario="噪音冲突",
        dialogue=[DialogueMessage(speaker="user", message="晚上能不能小声一点？")],
    )
    service = DormHarmonyAIService(runner=FakeRunner())

    response = service.review(request)

    assert response.strengths
    assert "不进行心理诊断" in response.safety_note


def test_service_sanitizes_runner_failures():
    request = SimulateRequest(scenario="噪音冲突", user_message="晚上能不能小声一点？")
    service = DormHarmonyAIService(runner=BrokenRunner())

    with pytest.raises(AIServiceUnavailableError) as exc_info:
        service.simulate(request)

    assert "AI 服务暂时不可用" in str(exc_info.value)
    assert "sk-test" not in str(exc_info.value)


def test_service_rejects_invalid_runner_shape():
    request = SimulateRequest(scenario="噪音冲突", user_message="晚上能不能小声一点？")
    service = DormHarmonyAIService(runner=BadShapeRunner())

    with pytest.raises(AIOutputStructureError):
        service.simulate(request)


def test_langchain_runner_can_be_constructed_with_settings(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    runner = LangChainOpenAIRunner(settings=load_ai_settings())

    assert runner.model == "gpt-4o-mini"
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
cd backend
python3 -m pytest -p no:cacheprovider tests/test_ai_service.py -q
```

Expected: FAIL because `app.ai_service` does not exist.

- [ ] **Step 3: Add dependencies**

Append to `backend/requirements.txt`:

```text
langchain-core>=0.2.43,<1
langchain-openai>=0.1.21,<1
openai>=1.40,<2
```

Then run if dependencies are missing:

```bash
cd backend
python3 -m pip install -r requirements.txt
```

Expected: dependencies install successfully. If network is blocked, request escalation before continuing.

- [ ] **Step 4: Implement AI service**

Create `backend/app/ai_service.py`:

```python
from dataclasses import dataclass
import os
from typing import Protocol, TypeVar

from pydantic import BaseModel, ValidationError

from app.ai_prompts import build_review_messages, build_simulate_messages
from app.schemas import ReviewRequest, ReviewResponse, SimulateRequest, SimulateResponse


class AIServiceConfigurationError(RuntimeError):
    pass


class AIServiceUnavailableError(RuntimeError):
    pass


class AIOutputStructureError(AIServiceUnavailableError):
    pass


@dataclass(frozen=True)
class AISettings:
    api_key: str
    model: str
    timeout: float


class AIRunner(Protocol):
    def generate_simulation(self, request: SimulateRequest) -> SimulateResponse:
        raise NotImplementedError

    def generate_review(self, request: ReviewRequest) -> ReviewResponse:
        raise NotImplementedError


OutputModel = TypeVar("OutputModel", bound=BaseModel)


def load_ai_settings() -> AISettings:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise AIServiceConfigurationError("AI 服务未配置：请设置 OPENAI_API_KEY。")

    timeout_text = os.getenv("DORM_HARMONY_LLM_TIMEOUT", "20").strip()
    try:
        timeout = float(timeout_text)
    except ValueError as exc:
        raise AIServiceConfigurationError("AI 服务未配置：DORM_HARMONY_LLM_TIMEOUT 必须是数字。") from exc

    return AISettings(
        api_key=api_key,
        model=os.getenv("DORM_HARMONY_LLM_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini",
        timeout=timeout,
    )


class LangChainOpenAIRunner:
    def __init__(self, settings: AISettings | None = None) -> None:
        self._settings = settings or load_ai_settings()
        self.model = self._settings.model

    def generate_simulation(self, request: SimulateRequest) -> SimulateResponse:
        return self._invoke_structured(SimulateResponse, build_simulate_messages(request))

    def generate_review(self, request: ReviewRequest) -> ReviewResponse:
        return self._invoke_structured(ReviewResponse, build_review_messages(request))

    def _invoke_structured(self, schema: type[OutputModel], messages: list[tuple[str, str]]) -> OutputModel:
        try:
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                model=self._settings.model,
                temperature=0.3,
                timeout=self._settings.timeout,
                max_retries=1,
                api_key=self._settings.api_key,
            )
            structured_llm = llm.with_structured_output(schema)
            result = structured_llm.invoke(messages)
        except ValidationError as exc:
            raise AIOutputStructureError("AI 输出结构异常，请稍后重试。") from exc
        except Exception as exc:
            raise AIServiceUnavailableError("AI 服务暂时不可用，请稍后重试。") from exc

        return _ensure_model_instance(result, schema)


class DormHarmonyAIService:
    def __init__(self, runner: AIRunner | None = None) -> None:
        self._runner = runner or LangChainOpenAIRunner()

    def simulate(self, request: SimulateRequest) -> SimulateResponse:
        try:
            return _ensure_model_instance(self._runner.generate_simulation(request), SimulateResponse)
        except AIServiceUnavailableError:
            raise
        except ValidationError as exc:
            raise AIOutputStructureError("AI 输出结构异常，请稍后重试。") from exc
        except Exception as exc:
            raise AIServiceUnavailableError("AI 服务暂时不可用，请稍后重试。") from exc

    def review(self, request: ReviewRequest) -> ReviewResponse:
        try:
            return _ensure_model_instance(self._runner.generate_review(request), ReviewResponse)
        except AIServiceUnavailableError:
            raise
        except ValidationError as exc:
            raise AIOutputStructureError("AI 输出结构异常，请稍后重试。") from exc
        except Exception as exc:
            raise AIServiceUnavailableError("AI 服务暂时不可用，请稍后重试。") from exc


def _ensure_model_instance(value: object, schema: type[OutputModel]) -> OutputModel:
    if isinstance(value, schema):
        return value
    if isinstance(value, dict):
        try:
            return schema.model_validate(value)
        except ValidationError as exc:
            raise AIOutputStructureError("AI 输出结构异常，请稍后重试。") from exc

    raise AIOutputStructureError("AI 输出结构异常，请稍后重试。")
```

- [ ] **Step 5: Run tests and verify GREEN**

Run:

```bash
cd backend
python3 -m pytest -p no:cacheprovider tests/test_ai_service.py tests/test_ai_contracts.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit Task 2**

Run:

```bash
git add backend/requirements.txt backend/app/ai_service.py backend/tests/test_ai_service.py
git commit -m "feat(ai): 接入 LangChain OpenAI 服务层"
```

---

### Task 3: FastAPI Endpoints

**Files:**
- Modify: `backend/app/main.py`
- Modify: `backend/tests/test_api.py`

- [ ] **Step 1: Add failing endpoint tests**

Append to `backend/tests/test_api.py`:

```python
import pytest

from app.ai_service import AIServiceConfigurationError, AIServiceUnavailableError
from app.main import get_ai_service
from app.schemas import ReviewResponse, RoommateReply, SimulateResponse
```

If imports already exist, merge them cleanly.

Append test helpers and tests:

```python
class FakeAIService:
    def simulate(self, request):
        return SimulateResponse(
            replies=[
                RoommateReply(roommate="舍友 A", personality="直接型", message="我也没开很大声吧，但可以试着戴耳机。"),
                RoommateReply(roommate="舍友 B", personality="回避型", message="这个事情我现在不太想聊，但可以晚点再说。"),
                RoommateReply(roommate="舍友 C", personality="调和型", message="我们可以一起定一个晚上安静时间。"),
            ],
            safety_note="本回复仅用于宿舍沟通演练，不代表真实舍友想法，不进行心理诊断、医学判断或人格评价。如有现实安全风险，请联系辅导员、心理老师、家人或可信任同学。",
        )

    def review(self, request):
        return ReviewResponse(
            summary="用户表达了睡眠受影响的事实，整体语气较温和。",
            strengths=["说明了具体影响"],
            risks=["可以进一步明确时间范围"],
            rewritten_message="我最近睡眠状态不太好，晚上 11 点后能不能戴耳机或调低音量？",
            next_steps=["选择双方情绪平稳的时间沟通"],
            safety_note="本复盘仅用于沟通训练建议，不进行心理诊断、医学判断或人格评价。如压力持续升高，请寻求现实支持。",
        )


class MissingKeyService:
    def simulate(self, request):
        raise AIServiceConfigurationError("AI 服务未配置：请设置 OPENAI_API_KEY。")

    def review(self, request):
        raise AIServiceConfigurationError("AI 服务未配置：请设置 OPENAI_API_KEY。")


class BrokenAIService:
    def simulate(self, request):
        raise AIServiceUnavailableError("AI 服务暂时不可用，请稍后重试。")

    def review(self, request):
        raise AIServiceUnavailableError("AI 服务暂时不可用，请稍后重试。")


@pytest.fixture(autouse=True)
def clear_ai_dependency_override():
    app.dependency_overrides.pop(get_ai_service, None)
    yield
    app.dependency_overrides.pop(get_ai_service, None)


def test_simulate_endpoint_returns_structured_roommate_replies():
    app.dependency_overrides[get_ai_service] = lambda: FakeAIService()

    response = client.post(
        "/api/simulate",
        json={
            "scenario": "舍友晚上打游戏声音较大，影响睡眠",
            "user_message": "我想和你商量一下，晚上能不能把游戏声音调小一点。",
            "risk_level": "high",
            "context": "用户尚未正式沟通过。",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert [reply["roommate"] for reply in body["replies"]] == ["舍友 A", "舍友 B", "舍友 C"]
    assert "不进行心理诊断" in body["safety_note"]


def test_review_endpoint_returns_structured_report():
    app.dependency_overrides[get_ai_service] = lambda: FakeAIService()

    response = client.post(
        "/api/review",
        json={
            "scenario": "舍友晚上打游戏声音较大，影响睡眠",
            "dialogue": [
                {"speaker": "user", "message": "我想和你商量一下，晚上能不能把游戏声音调小一点。"},
                {"speaker": "roommate_a", "message": "我也没开很大声吧。"},
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["strengths"]
    assert body["risks"]
    assert "11 点后" in body["rewritten_message"]
    assert "不进行心理诊断" in body["safety_note"]


def test_simulate_endpoint_returns_503_when_ai_key_missing():
    app.dependency_overrides[get_ai_service] = lambda: MissingKeyService()

    response = client.post(
        "/api/simulate",
        json={"scenario": "噪音冲突", "user_message": "晚上能不能小声一点？"},
    )

    assert response.status_code == 503
    assert "OPENAI_API_KEY" in response.json()["detail"]


def test_review_endpoint_returns_502_when_ai_service_fails():
    app.dependency_overrides[get_ai_service] = lambda: BrokenAIService()

    response = client.post(
        "/api/review",
        json={
            "scenario": "噪音冲突",
            "dialogue": [{"speaker": "user", "message": "晚上能不能小声一点？"}],
        },
    )

    assert response.status_code == 502
    assert "AI 服务暂时不可用" in response.json()["detail"]


def test_simulate_endpoint_rejects_blank_message():
    app.dependency_overrides[get_ai_service] = lambda: FakeAIService()

    response = client.post(
        "/api/simulate",
        json={"scenario": "噪音冲突", "user_message": "   "},
    )

    assert response.status_code == 422
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
cd backend
python3 -m pytest -p no:cacheprovider tests/test_api.py::test_simulate_endpoint_returns_structured_roommate_replies -q
```

Expected: FAIL because `get_ai_service` or `/api/simulate` does not exist.

- [ ] **Step 3: Implement FastAPI routes**

Update `backend/app/main.py` to:

```python
from fastapi import Depends, FastAPI, HTTPException

from app.ai_service import AIServiceConfigurationError, AIServiceUnavailableError, DormHarmonyAIService
from app.schemas import AnalyzeRequest, AnalyzeResponse, ReviewRequest, ReviewResponse, SimulateRequest, SimulateResponse
from app.scoring import analyze_pressure


app = FastAPI(title="Dorm Harmony AI")


def get_ai_service() -> DormHarmonyAIService:
    return DormHarmonyAIService()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    return analyze_pressure(request)


@app.post("/api/simulate", response_model=SimulateResponse)
async def simulate(
    request: SimulateRequest,
    ai_service: DormHarmonyAIService = Depends(get_ai_service),
) -> SimulateResponse:
    try:
        return ai_service.simulate(request)
    except AIServiceConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AIServiceUnavailableError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/review", response_model=ReviewResponse)
async def review(
    request: ReviewRequest,
    ai_service: DormHarmonyAIService = Depends(get_ai_service),
) -> ReviewResponse:
    try:
        return ai_service.review(request)
    except AIServiceConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AIServiceUnavailableError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
```

- [ ] **Step 4: Run endpoint tests**

Run:

```bash
cd backend
python3 -m pytest -p no:cacheprovider tests/test_api.py -q
```

Expected: PASS. If sandbox `TestClient` hangs, run:

```bash
cd backend
python3 -m pytest -p no:cacheprovider tests/test_ai_service.py tests/test_ai_contracts.py tests/test_scoring.py -q
```

Record the exact API-test failure or timeout before continuing.

- [ ] **Step 5: Commit Task 3**

Run:

```bash
git add backend/app/main.py backend/tests/test_api.py
git commit -m "feat(api): 新增 AI 模拟与复盘接口"
```

---

### Task 4: Documentation and Phase Status

**Files:**
- Modify: `README.md`
- Modify: `docs/backend-api-contract.md`
- Create: `docs/phase2-status.md`
- Modify: `DEVELOPMENT_PLAN_AND_DELIVERABLES.md`

- [ ] **Step 1: Write status/documentation checks first**

Run this before editing docs to see current gaps:

```bash
rg -n "第二阶段后端 AI|OPENAI_API_KEY|DORM_HARMONY_LLM_MODEL|/api/simulate.*已实现|/api/review.*已实现|docs/phase2-status.md|B2-1.*已完成|B2-6.*已完成" README.md docs/backend-api-contract.md DEVELOPMENT_PLAN_AND_DELIVERABLES.md docs || true
```

Expected: missing or draft-only matches, because docs still describe `/api/simulate` and `/api/review` as planned/draft.

- [ ] **Step 2: Update README current status**

In `README.md`, replace the first-stage current-status paragraph with text that says:

```markdown
当前仓库已完成第二阶段朱春雯负责的后端 AI 能力：已实现 `GET /health`、`POST /api/analyze`、`POST /api/simulate` 和 `POST /api/review`。`/api/simulate` 与 `/api/review` 通过 LangChain 调用 OpenAI 模型，并使用结构化响应供前端展示。前端 AI 页面联调、完整 Demo、历史记录存储、第 7 天演示视频和宣传海报仍属于曹乐任务、第三阶段或后续提交材料范围。
```

In the backend run section, add:

```markdown
第二阶段 AI 接口需要配置：

```bash
export OPENAI_API_KEY="你的 OpenAI API Key"
export DORM_HARMONY_LLM_MODEL="gpt-4o-mini"
export DORM_HARMONY_LLM_TIMEOUT="20"
```

`OPENAI_API_KEY` 必须只通过本地环境变量配置，不要提交到仓库。未配置时，`/api/simulate` 和 `/api/review` 会返回 `503`，不会返回模板伪结果。
```
```

Also update the available endpoint list to include:

```markdown
- `POST /api/simulate`
- `POST /api/review`
```

- [ ] **Step 3: Update backend API contract**

In `docs/backend-api-contract.md`:

1. Change the introduction to say second-stage runtime AI endpoints are implemented.
2. Change `## 第二阶段字段草案` to `## 第二阶段已实现 AI 接口`.
3. For `POST /api/simulate`, change status to:

```markdown
状态：第二阶段已实现。运行时通过 LangChain 调用 OpenAI 模型；缺少 `OPENAI_API_KEY` 时返回 `503`。
```

4. For `POST /api/review`, change status to:

```markdown
状态：第二阶段已实现。运行时通过 LangChain 调用 OpenAI 模型；缺少 `OPENAI_API_KEY` 时返回 `503`。
```

5. Add error responses:

```markdown
AI 接口错误语义：

| 场景 | HTTP 状态 |
| --- | --- |
| 请求字段非法 | `422` |
| 未配置 `OPENAI_API_KEY` | `503` |
| LangChain / OpenAI 调用失败 | `502` |
| AI 输出结构不符合契约 | `502` |
```

- [ ] **Step 4: Add phase-2 status**

Create `docs/phase2-status.md`:

```markdown
# 第二阶段后端 AI 状态

本文档记录朱春雯负责的第二阶段后端 / AI 任务状态。范围覆盖 FastAPI 后端接口、LangChain AI 服务、Prompt、安全边界、演示样例和技术文档；不覆盖曹乐负责的前端页面、UI、截图、演示视频和宣传海报。

## 当前已完成

| 任务编号 | 状态 | 证据 |
| --- | --- | --- |
| B2-1 完善 `/api/analyze` 评分逻辑 | 已完成 | `backend/app/scoring.py` 按严重程度、频率、情绪、沟通状态、冲突状态计算不同压力值；`backend/tests/test_scoring.py` 覆盖低风险和高压力差异 |
| B2-2 设计多角色 Prompt | 已完成 | `backend/app/ai_prompts.py` 固定舍友 A 直接型、舍友 B 回避型、舍友 C 调和型，并包含安全边界 |
| B2-3 实现 `/api/simulate` 接口 | 已完成 | `backend/app/main.py` 注册 `POST /api/simulate`，通过 `backend/app/ai_service.py` 调用 LangChain/OpenAI |
| B2-4 实现 `/api/review` 接口 | 已完成 | `backend/app/main.py` 注册 `POST /api/review`，返回结构化复盘报告 |
| B2-5 添加心理安全边界 | 已完成 | `backend/app/ai_prompts.py` 和响应 `safety_note` 明确不做心理诊断、医学判断或人格评价，并提示现实支持 |
| B2-6 准备演示用样例数据 | 已完成 | `backend/app/demo_data.py` 覆盖噪音冲突、卫生分工、隐私边界 3 个场景 |

## 运行配置

AI 接口需要本地环境变量：

```bash
export OPENAI_API_KEY="你的 OpenAI API Key"
export DORM_HARMONY_LLM_MODEL="gpt-4o-mini"
export DORM_HARMONY_LLM_TIMEOUT="20"
```

`OPENAI_API_KEY` 不得提交到仓库。未配置时，`/api/simulate` 和 `/api/review` 返回 `503`，不会返回模板伪结果。

## 未覆盖范围

- 曹乐负责的前端 AI 沟通模拟页面和复盘报告页面联调。
- 第三阶段完整 Demo 跑通、问题修复记录、截图素材。
- 第 7 天演示视频、宣传海报和线上提交材料。
- 历史记录存储与查询。
```

- [ ] **Step 5: Update development plan B2 table**

In `DEVELOPMENT_PLAN_AND_DELIVERABLES.md`, under "### 5.1 朱春雯任务", add a short status subsection after the B2 task table:

```markdown
### 5.1.1 第二阶段后端 / AI 状态记录

| 任务编号 | 当前状态 | 证据 |
| --- | --- | --- |
| B2-1 | 已完成 | `backend/app/scoring.py` 与 `backend/tests/test_scoring.py` 覆盖不同输入对应不同压力值和风险等级 |
| B2-2 | 已完成 | `backend/app/ai_prompts.py` 固定三位舍友角色和输出边界 |
| B2-3 | 已完成 | `POST /api/simulate` 已在 `backend/app/main.py` 注册，并由 `backend/app/ai_service.py` 通过 LangChain/OpenAI 生成结构化回复 |
| B2-4 | 已完成 | `POST /api/review` 已在 `backend/app/main.py` 注册，并返回结构化复盘报告 |
| B2-5 | 已完成 | Prompt 与 `safety_note` 包含非诊断性提示和现实支持建议 |
| B2-6 | 已完成 | `backend/app/demo_data.py` 提供噪音冲突、卫生分工、隐私边界演示样例 |
```

- [ ] **Step 6: Verify docs**

Run:

```bash
rg -n "第二阶段后端 AI|OPENAI_API_KEY|DORM_HARMONY_LLM_MODEL|/api/simulate|/api/review|B2-1|B2-6" README.md docs/backend-api-contract.md docs/phase2-status.md DEVELOPMENT_PLAN_AND_DELIVERABLES.md
```

Expected: all documents mention the implemented endpoints/config/status.

- [ ] **Step 7: Commit Task 4**

Run:

```bash
git add README.md docs/backend-api-contract.md docs/phase2-status.md DEVELOPMENT_PLAN_AND_DELIVERABLES.md
git commit -m "docs(ai): 记录第二阶段后端 AI 状态"
```

---

### Task 5: Final Verification

**Files:**
- No source changes unless verification exposes a bug.

- [ ] **Step 1: Run full backend tests**

Run:

```bash
cd backend
python3 -m pytest -p no:cacheprovider
```

Expected: all tests pass. If API tests hang in this sandbox, capture exact command and failure mode, then run service/contract/scoring tests:

```bash
cd backend
python3 -m pytest -p no:cacheprovider tests/test_ai_contracts.py tests/test_ai_service.py tests/test_scoring.py -q
```

- [ ] **Step 2: Verify route registration without real API call**

Run:

```bash
cd backend
python3 - <<'PY'
from app.main import app
routes = sorted(route.path for route in app.routes)
print(routes)
assert "/api/analyze" in routes
assert "/api/simulate" in routes
assert "/api/review" in routes
PY
```

Expected: printed route list includes `/api/analyze`, `/api/simulate`, and `/api/review`.

- [ ] **Step 3: Verify no secrets are committed**

Run:

```bash
rg -n "sk-[A-Za-z0-9]|OPENAI_API_KEY=.*[A-Za-z0-9]" .
```

Expected: no real API key values. Documentation may mention `OPENAI_API_KEY` as a variable name only.

- [ ] **Step 4: Review git history and status**

Run:

```bash
git status --short --branch
git log --oneline --decorate -5
```

Expected: on `feature/zcc-phase2-backend-ai`; no unintended untracked files except acceptable local caches ignored by git; commits are split into spec, contracts/demo data, service, routes, docs.

- [ ] **Step 5: Final code review**

Dispatch a final code reviewer subagent with:

- Description: Zhu Chunwen phase-2 backend AI implementation.
- Requirements: this plan and `docs/superpowers/specs/2026-05-13-zcc-phase2-langchain-ai-design.md`.
- Base SHA: commit before Task 1 implementation, after spec commit `0dc36ec`.
- Head SHA: current `HEAD`.

Fix any Critical or Important findings before final response.
