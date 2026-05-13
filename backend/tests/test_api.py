from fastapi.testclient import TestClient
import pytest

from app.ai_service import AIServiceConfigurationError, AIServiceUnavailableError
from app.main import app, get_ai_service
from app.safety import SAFETY_DISCLAIMER
from app.schemas import ReviewResponse, RoommateReply, SimulateResponse


client = TestClient(app)


class FakeAIService:
    def simulate(self, request):
        return SimulateResponse(
            replies=[
                RoommateReply(
                    roommate="舍友 A",
                    personality="直接型",
                    message="我知道你觉得吵，我会注意音量。",
                ),
                RoommateReply(
                    roommate="舍友 B",
                    personality="回避型",
                    message="我可能没意识到已经影响你了，可以再提醒我。",
                ),
                RoommateReply(
                    roommate="舍友 C",
                    personality="调和型",
                    message="我们可以一起约定 11 点后的安静时间。",
                ),
            ],
            safety_note=(
                "仅用于宿舍沟通演练，不代表真实舍友想法，不进行心理诊断，"
                "不进行医学判断，不进行人格评价；如冲突升级请寻求辅导员或心理老师等现实支持。"
            ),
        )

    def review(self, request):
        return ReviewResponse(
            summary="表达了睡眠受影响的具体困扰。",
            strengths=["说明了具体时间和影响", "语气保持克制"],
            risks=["可能让对方觉得被指责"],
            rewritten_message="我最近 11 点后比较需要休息，可以麻烦你那之后降低音量吗？",
            next_steps=["先约定安静时段", "必要时请辅导员协助沟通"],
            safety_note=(
                "仅用于沟通训练建议，不代表真实舍友想法，不进行心理诊断，"
                "不进行医学判断，不进行人格评价；如持续困扰请联系辅导员或心理老师获得现实支持。"
            ),
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
def clear_ai_service_override():
    app.dependency_overrides.pop(get_ai_service, None)
    yield
    app.dependency_overrides.pop(get_ai_service, None)


def test_health_endpoint_returns_ok_status():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_endpoint_returns_structured_pressure_analysis():
    response = client.post(
        "/api/analyze",
        json={
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
    assert body.keys() == {
        "pressure_score",
        "risk_level",
        "risk_label",
        "main_sources",
        "emotion_keywords",
        "trend_message",
        "suggestion",
        "recommend_simulation",
        "disclaimer",
    }
    assert body["pressure_score"] == 76
    assert body["risk_level"] == "high"
    assert body["risk_label"] == "冲突风险较高"
    assert body["main_sources"] == ["噪音冲突", "发生频率较高", "尚未有效沟通", "已出现争吵或冷战"]
    assert body["emotion_keywords"] == ["焦虑"]
    assert body["recommend_simulation"] is True
    assert "当前压力值为 76" in body["trend_message"]
    assert "沟通演练" in body["suggestion"]
    assert body["disclaimer"] == SAFETY_DISCLAIMER


def test_analyze_endpoint_rejects_out_of_range_severity():
    response = client.post(
        "/api/analyze",
        json={
            "event_type": "noise",
            "severity": 6,
            "frequency": "daily",
            "emotion": "angry",
            "has_communicated": False,
            "has_conflict": True,
            "description": "测试严重程度越界。",
        },
    )

    assert response.status_code == 422


def test_simulate_endpoint_returns_structured_roommate_replies():
    app.dependency_overrides[get_ai_service] = lambda: FakeAIService()

    response = client.post(
        "/api/simulate",
        json={
            "scenario": "舍友晚上打游戏声音很大，影响睡眠。",
            "user_message": "能不能晚上小声一点？",
            "risk_level": "high",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert [reply["roommate"] for reply in body["replies"]] == [
        "舍友 A",
        "舍友 B",
        "舍友 C",
    ]
    assert "不进行心理诊断" in body["safety_note"]


def test_review_endpoint_returns_structured_report():
    app.dependency_overrides[get_ai_service] = lambda: FakeAIService()

    response = client.post(
        "/api/review",
        json={
            "scenario": "舍友晚上打游戏声音很大，影响睡眠。",
            "dialogue": [
                {"speaker": "user", "message": "能不能晚上小声一点？"},
                {"speaker": "roommate_a", "message": "我会注意音量。"},
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
        json={
            "scenario": "舍友晚上打游戏声音很大，影响睡眠。",
            "user_message": "能不能晚上小声一点？",
        },
    )

    assert response.status_code == 503
    assert "OPENAI_API_KEY" in response.json()["detail"]


def test_review_endpoint_returns_502_when_ai_service_fails():
    app.dependency_overrides[get_ai_service] = lambda: BrokenAIService()

    response = client.post(
        "/api/review",
        json={
            "scenario": "舍友晚上打游戏声音很大，影响睡眠。",
            "dialogue": [
                {"speaker": "user", "message": "能不能晚上小声一点？"},
            ],
        },
    )

    assert response.status_code == 502
    assert "AI 服务暂时不可用" in response.json()["detail"]


def test_simulate_endpoint_rejects_blank_message():
    response = client.post(
        "/api/simulate",
        json={
            "scenario": "舍友晚上打游戏声音很大，影响睡眠。",
            "user_message": "   ",
        },
    )

    assert response.status_code == 422
