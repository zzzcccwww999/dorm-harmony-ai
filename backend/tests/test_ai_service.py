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


SIMULATE_SAFETY_NOTE = (
    "本回复仅用于宿舍沟通演练，不代表真实舍友想法，"
    "不进行心理诊断、不进行医学判断、不进行人格评价。"
    "如有现实安全风险，请联系辅导员、心理老师、家人或可信任同学。"
)
REVIEW_SAFETY_NOTE = (
    "本复盘仅用于沟通训练建议，不代表真实舍友想法，"
    "不进行心理诊断、不进行医学判断、不进行人格评价。"
    "如压力持续升高，请寻求现实支持或联系辅导员、心理老师。"
)


class FakeRunner:
    def generate_simulation(self, request):
        return SimulateResponse(
            replies=[
                RoommateReply(
                    roommate="舍友 A",
                    personality="直接型",
                    message="我也没开很大声吧，但可以试着戴耳机。",
                ),
                RoommateReply(
                    roommate="舍友 B",
                    personality="回避型",
                    message="这个事情我现在不太想聊，但可以晚点再说。",
                ),
                RoommateReply(
                    roommate="舍友 C",
                    personality="调和型",
                    message="我们可以一起定一个晚上安静时间。",
                ),
            ],
            safety_note=SIMULATE_SAFETY_NOTE,
        )

    def generate_review(self, request):
        return ReviewResponse(
            summary="用户表达了睡眠受影响的事实，整体语气较温和。",
            strengths=["说明了具体影响"],
            risks=["可以进一步明确时间范围"],
            rewritten_message="我最近睡眠状态不太好，晚上 11 点后能不能戴耳机或调低音量？",
            next_steps=["选择双方情绪平稳的时间沟通"],
            safety_note=REVIEW_SAFETY_NOTE,
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
