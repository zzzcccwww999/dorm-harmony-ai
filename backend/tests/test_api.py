import inspect
import json

from fastapi.testclient import TestClient
import pytest

from app.ai_service import AIServiceConfigurationError, AIServiceUnavailableError
from app.main import _get_cors_origins, app, get_ai_service, review, simulate
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
        raise AIServiceConfigurationError(
            "AI 服务未配置：请设置 DEEPSEEK_API_KEY（推荐）或 OPENAI_API_KEY（兼容旧配置）。"
        )

    def review(self, request):
        raise AIServiceConfigurationError(
            "AI 服务未配置：请设置 DEEPSEEK_API_KEY（推荐）或 OPENAI_API_KEY（兼容旧配置）。"
        )


class BrokenAIService:
    def simulate(self, request):
        raise AIServiceUnavailableError("AI 服务暂时不可用，请稍后重试。")

    def review(self, request):
        raise AIServiceUnavailableError("AI 服务暂时不可用，请稍后重试。")


class CapturingReviewService(FakeAIService):
    def __init__(self):
        self.review_request = None

    def review(self, request):
        self.review_request = request
        return super().review(request)


def assert_llm_key_hint(detail):
    assert "DEEPSEEK_API_KEY" in detail
    assert "OPENAI_API_KEY" in detail


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


def test_cors_preflight_allows_local_vite_frontend():
    response = client.options(
        "/api/analyze",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_preflight_allows_local_vite_frontend_by_ip():
    response = client.options(
        "/api/analyze",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"


def test_cors_origin_loader_accepts_comma_separated_override(monkeypatch):
    monkeypatch.setenv(
        "DORM_HARMONY_CORS_ORIGINS",
        "http://localhost:3000, http://127.0.0.1:7357",
    )

    assert _get_cors_origins() == ["http://localhost:3000", "http://127.0.0.1:7357"]


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


def test_ai_endpoints_run_as_sync_functions_for_threadpool_execution():
    assert not inspect.iscoroutinefunction(simulate)
    assert not inspect.iscoroutinefunction(review)


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


def test_simulate_stream_endpoint_returns_ordered_reply_events():
    app.dependency_overrides[get_ai_service] = lambda: FakeAIService()

    with client.stream(
        "POST",
        "/api/simulate/stream",
        json={
            "scenario": "舍友晚上打游戏声音很大，影响睡眠。",
            "user_message": "能不能晚上小声一点？",
            "risk_level": "high",
        },
    ) as response:
        lines = [line for line in response.iter_lines() if line]

    assert response.status_code == 200

    events = [json.loads(line) for line in lines]
    assert [event["type"] for event in events] == [
        "start",
        "reply",
        "reply",
        "reply",
        "final",
    ]
    assert [event["reply"]["roommate"] for event in events[1:4]] == [
        "舍友 A",
        "舍友 B",
        "舍友 C",
    ]
    assert events[-1]["response"]["replies"][0]["roommate"] == "舍友 A"
    assert "不进行心理诊断" in events[-1]["response"]["safety_note"]


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


def test_review_endpoint_accepts_frontend_display_payload_until_ai_config_check():
    app.dependency_overrides[get_ai_service] = lambda: MissingKeyService()

    response = client.post(
        "/api/review",
        json={
            "scenario": "舍友晚上打游戏声音很大，影响睡眠。",
            "dialogue": [
                {"speaker": "你", "message": "能不能晚上小声一点？"},
                {"speaker": "舍友 A（直接型）", "message": "我会注意音量。"},
                {"speaker": "舍友 C（调和型）", "message": "我们可以约个安静时间。"},
            ],
            "original_event": {
                "event_type": "noise_conflict",
                "severity": 4,
                "frequency": "weekly_multiple",
                "emotion": "anxious",
                "has_communicated": False,
                "has_conflict": True,
                "description": "舍友晚上打游戏声音很大，影响睡眠。",
            },
        },
    )

    assert response.status_code == 503
    assert_llm_key_hint(response.json()["detail"])


def test_review_endpoint_normalizes_frontend_display_payload_for_ai_service():
    service = CapturingReviewService()
    app.dependency_overrides[get_ai_service] = lambda: service

    response = client.post(
        "/api/review",
        json={
            "scenario": "舍友晚上打游戏声音很大，影响睡眠。",
            "dialogue": [
                {"speaker": "你", "message": "能不能晚上小声一点？"},
                {"speaker": "舍友 A（直接型）", "message": "我会注意音量。"},
                {"speaker": "舍友 B（回避型）", "message": "我再想想。"},
                {"speaker": "舍友 C（调和型）", "message": "我们可以约个安静时间。"},
                {"speaker": "系统", "message": "复盘阶段记录。"},
            ],
            "original_event": {
                "event_type": "noise_conflict",
                "severity": 4,
                "frequency": "weekly_multiple",
                "emotion": "anxious",
                "has_communicated": False,
                "has_conflict": True,
                "description": "舍友晚上打游戏声音很大，影响睡眠。",
            },
        },
    )

    assert response.status_code == 200
    assert service.review_request is not None
    assert [message.speaker for message in service.review_request.dialogue] == [
        "user",
        "roommate_a",
        "roommate_b",
        "roommate_c",
        "system",
    ]
    assert service.review_request.original_event is not None
    assert service.review_request.original_event.event_type == "noise"


def test_review_endpoint_accepts_additional_frontend_aliases_until_ai_config_check():
    app.dependency_overrides[get_ai_service] = lambda: MissingKeyService()

    response = client.post(
        "/api/review",
        json={
            "scenario": "宿舍公共区域使用问题。",
            "dialogue": [
                {"speaker": "我", "message": "我想商量一下公共区域的使用。"},
                {"speaker": "舍友A", "message": "我觉得可以。"},
                {"speaker": "舍友B", "message": "我再想想。"},
                {"speaker": "舍友C", "message": "我们一起定个规则。"},
                {"speaker": "系统", "message": "复盘阶段记录。"},
            ],
            "original_event": {
                "event_type": "expense_conflict",
                "description": "宿舍费用分摊有争议。",
            },
        },
    )

    assert response.status_code == 503
    assert_llm_key_hint(response.json()["detail"])


@pytest.mark.parametrize(
    "event_type",
    ["expense_conflict", "privacy_boundary", "emotional_conflict"],
)
def test_review_endpoint_accepts_spec_event_type_aliases_until_ai_config_check(event_type):
    app.dependency_overrides[get_ai_service] = lambda: MissingKeyService()

    response = client.post(
        "/api/review",
        json={
            "scenario": "宿舍边界问题需要复盘。",
            "dialogue": [
                {"speaker": "用户", "message": "我想复盘一下刚才的沟通。"},
            ],
            "original_event": {
                "event_type": event_type,
                "description": "宿舍边界问题需要复盘。",
            },
        },
    )

    assert response.status_code == 503
    assert_llm_key_hint(response.json()["detail"])


def test_review_endpoint_ignores_analysis_only_event_alias_until_ai_config_check():
    app.dependency_overrides[get_ai_service] = lambda: MissingKeyService()

    response = client.post(
        "/api/review",
        json={
            "scenario": "舍友晚上打游戏声音很大，影响睡眠。",
            "dialogue": [
                {"speaker": "用户", "message": "能不能晚上小声一点？"},
            ],
            "original_event": {
                "event_type": "risk-high",
                "description": "舍友晚上打游戏声音很大，影响睡眠。",
            },
        },
    )

    assert response.status_code == 503
    assert_llm_key_hint(response.json()["detail"])


def test_review_endpoint_rejects_unknown_risk_prefixed_event_alias():
    response = client.post(
        "/api/review",
        json={
            "scenario": "沟通复盘场景",
            "dialogue": [{"speaker": "用户", "message": "我想先说清楚我的睡眠受影响了。"}],
            "original_event": {
                "event_type": "risk-critical",
                "risk_level": "high",
                "pressure_score": 76,
            },
        },
    )

    assert response.status_code == 422


def test_review_endpoint_rejects_extra_top_level_fields():
    response = client.post(
        "/api/review",
        json={
            "scenario": "舍友晚上打游戏声音很大，影响睡眠。",
            "dialogue": [
                {"speaker": "user", "message": "能不能晚上小声一点？"},
            ],
            "debug_payload": {"unexpected": True},
        },
    )

    assert response.status_code == 422


def test_review_endpoint_rejects_extra_dialogue_fields():
    response = client.post(
        "/api/review",
        json={
            "scenario": "舍友晚上打游戏声音很大，影响睡眠。",
            "dialogue": [
                {
                    "speaker": "user",
                    "message": "能不能晚上小声一点？",
                    "ui_label": "你",
                },
            ],
        },
    )

    assert response.status_code == 422


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
    assert_llm_key_hint(response.json()["detail"])


def test_review_endpoint_returns_503_when_ai_key_missing():
    app.dependency_overrides[get_ai_service] = lambda: MissingKeyService()

    response = client.post(
        "/api/review",
        json={
            "scenario": "舍友晚上打游戏声音很大，影响睡眠。",
            "dialogue": [
                {"speaker": "user", "message": "能不能晚上小声一点？"},
            ],
        },
    )

    assert response.status_code == 503
    assert_llm_key_hint(response.json()["detail"])


def test_simulate_endpoint_returns_502_when_ai_service_fails():
    app.dependency_overrides[get_ai_service] = lambda: BrokenAIService()

    response = client.post(
        "/api/simulate",
        json={
            "scenario": "舍友晚上打游戏声音很大，影响睡眠。",
            "user_message": "能不能晚上小声一点？",
        },
    )

    assert response.status_code == 502
    assert "AI 服务暂时不可用" in response.json()["detail"]


def test_simulate_stream_endpoint_returns_503_when_ai_key_missing():
    app.dependency_overrides[get_ai_service] = lambda: MissingKeyService()

    response = client.post(
        "/api/simulate/stream",
        json={
            "scenario": "舍友晚上打游戏声音很大，影响睡眠。",
            "user_message": "能不能晚上小声一点？",
        },
    )

    assert response.status_code == 503
    assert_llm_key_hint(response.json()["detail"])


def test_simulate_stream_endpoint_returns_502_when_ai_service_fails():
    app.dependency_overrides[get_ai_service] = lambda: BrokenAIService()

    response = client.post(
        "/api/simulate/stream",
        json={
            "scenario": "舍友晚上打游戏声音很大，影响睡眠。",
            "user_message": "能不能晚上小声一点？",
        },
    )

    assert response.status_code == 502
    assert "AI 服务暂时不可用" in response.json()["detail"]


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
